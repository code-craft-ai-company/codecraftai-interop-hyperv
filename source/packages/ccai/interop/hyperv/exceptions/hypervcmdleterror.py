"""
    .. module:: hypervcmdleterror
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`HypervCmdletError`
                   exception type.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Optional


class HypervCmdletError(RuntimeError):
    """
        Raised when a PowerShell cmdlet dispatched through the
        :class:`HypervClient` exits non-zero or writes a terminating
        error to stderr.

        The exception carries the rendered command line, the exit code,
        and the captured stderr so failure reports stay debuggable.
    """

    def __init__(self, message: str, *,
                 command_line: Optional[str] = None,
                 exit_code: Optional[int] = None,
                 stderr: Optional[str] = None) -> None:
        """
            Initialise a HypervCmdletError.

            :param message: The summary error message.
            :param command_line: The rendered PowerShell command line.
            :param exit_code: The cmdlet process exit code.
            :param stderr: The captured standard-error text.
        """
        super().__init__(message)
        self.command_line: Optional[str] = command_line
        self.exit_code: Optional[int] = exit_code
        self.stderr: Optional[str] = stderr
        return
