import select
import signal
import subprocess
from typing import Callable

STREAM_SUCCESS_STRING = "PROCESS_STREAM_SUCCESS"
STREAM_ERROR_STRING = "PROCESS_STREAM_ERROR"


class CustomCalledProcessError(subprocess.CalledProcessError):
    def __str__(self):
        if self.returncode and self.returncode < 0:
            try:
                base_out = "Command '%s' died with %r." % (
                    self.cmd,
                    signal.Signals(-self.returncode),
                )

            except ValueError:
                base_out = "Command '%s' died with unknown signal %d." % (
                    self.cmd,
                    -self.returncode,
                )
        else:
            base_out = "Command '%s' returned non-zero exit status %d." % (
                self.cmd,
                self.returncode,
            )
        if self.stderr:
            return base_out + "\n\n" + f"Stderr:\n_______\n{self.stderr}"
        return base_out


def run_and_capture_subprocess(
    command: list[str], shell: bool = False, check: bool = False
) -> str:
    """
    Runs a subprocess, captures the output, and streams it to the terminal in real-time.

    Args:
    command (list): The command to run as a list of strings. Example: ['ls', '-l']

    Returns:
    output (str): The complete captured output of the command.
    """
    process = subprocess.run(command, text=True, shell=shell, stderr=subprocess.PIPE)
    if process.returncode != 0 and check:
        raise CustomCalledProcessError(
            process.returncode, command, stderr=process.stderr
        )
    return process


def stream_subprocess(
    command_ls: list[str],
    env: dict[str, str] | None = None,
    cwd: str = None,
    check_success: Callable[[], bool] = None,
    should_terminate: Callable[[], bool] = None,
):
    stdouts = []
    stderrs = []
    try:
        process = subprocess.Popen(
            command_ls,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            cwd=cwd,
        )

        while process.poll() is None:
            if should_terminate is not None and should_terminate():
                process.terminate()
                return
            ready, _, _ = select.select([process.stdout, process.stderr], [], [], 0.1)
            for stream in ready:
                line = stream.readline()
                if line:
                    if stream == process.stdout:
                        stdouts.append(line)
                    else:
                        stderrs.append(line)
                    yield line

        # Read any remaining output after termination
        if process.stdout:
            for line in process.stdout:
                stdouts.append(line)
                yield line
        if process.stderr:
            for line in process.stderr:
                stderrs.append(line)
                yield line

        stdout = "".join(stdouts)
        stderr = "".join(stderrs)

        if not check_success:
            return

        success = check_success(stdout, stderr) if check_success else None
        success_str = STREAM_SUCCESS_STRING if success else STREAM_ERROR_STRING
        yield success_str
    finally:
        if "process" in locals() and process and process.poll() is None:
            process.terminate()
