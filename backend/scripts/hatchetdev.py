import subprocess
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class ChangeHandler(FileSystemEventHandler):
    """Handles file system changes by managing and running a specified command with streaming output."""

    def __init__(self, command):
        self.command = command
        self.process = None

    def terminate_process(self):
        """Terminate the existing command process if it's running."""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=1)  # Wait for the process to terminate
            except subprocess.TimeoutExpired:
                self.process.kill()  # Force kill if not terminated within timeout
                self.process.wait()

    def on_any_event(self, event):
        """Executes the command on any file system event."""
        if not event.is_directory:  # Ignore directory changes for simplicity
            print(f"Event type: {event.event_type} - Path: {event.src_path}")
            self.terminate_process()  # Terminate any existing process
            try:
                # Start a new process with stdout and stderr streamed to the terminal
                self.process = subprocess.Popen(
                    self.command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                self.stream_output()
            except Exception as e:
                print(f"An error occurred when executing the command: {e}")

    def stream_output(self):
        """Stream the output of the subprocess to the console."""
        if self.process:
            for line in iter(self.process.stdout.readline, b""):
                print(line.decode(), end="")


def main(directory_to_watch, command):
    """Sets up the watchdog observer to monitor a directory."""
    event_handler = ChangeHandler(command)
    observer = Observer()
    observer.schedule(event_handler, directory_to_watch, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        event_handler.terminate_process()  # Ensure to terminate any running process on exit
    observer.join()


if __name__ == "__main__":
    directory_to_watch = "/path/to/directory"  # Set the directory you want to monitor
    command = "poetry run hatchet"  # Set the command you want to run
    main(directory_to_watch, command)
