import signal
import subprocess


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
