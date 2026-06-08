"""
    .. module:: mockcommandrunner
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`MockCommandRunner` used by
                   the Hyper-V client tests to return seeded ``RunResult``
                   objects keyed by the rendered PowerShell command.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Callable, Dict, List, Optional

from ccai.interfaces.icommandrunner import RunResult


class MockCommandRunner:
    """
        In-memory :class:`ICommandRunner` returning seeded results.

        The runner matches each invocation against an ordered list of
        ``(predicate, RunResult)`` rules; the first matching rule is used.
        Every invocation's command string is recorded for assertion.
    """

    def __init__(self) -> None:
        """
            Initialise an empty MockCommandRunner.
        """
        self._rules: List[tuple] = []
        self.invocations: List[str] = []
        self.argv_invocations: List[List[str]] = []
        self._default: Optional[RunResult] = None
        return

    def seed(self, *, contains: str, stdout: str = "",
             stderr: str = "", exit_code: int = 0,
             timed_out: bool = False) -> "MockCommandRunner":
        """
            Seed a result for any command whose text contains a substring.

            :param contains: Substring matched against the command text.
            :param stdout: Standard-output text to return.
            :param stderr: Standard-error text to return.
            :param exit_code: Process exit code to return.
            :param timed_out: Whether the result is flagged as timed out.

            :returns: This runner, for chaining.
        """
        result = RunResult(exit_code=exit_code, stdout=stdout,
                           stderr=stderr, timed_out=timed_out)

        def _predicate(command: str) -> bool:
            rtnval = contains in command
            return rtnval

        self._rules.append((_predicate, result))
        rtnval = self
        return rtnval

    def seed_predicate(self, *, predicate: Callable[[str], bool],
                       stdout: str = "", stderr: str = "",
                       exit_code: int = 0,
                       timed_out: bool = False) -> "MockCommandRunner":
        """
            Seed a result against an arbitrary command predicate.

            :param predicate: Callable mapping command text to a bool.
            :param stdout: Standard-output text to return.
            :param stderr: Standard-error text to return.
            :param exit_code: Process exit code to return.
            :param timed_out: Whether the result is flagged as timed out.

            :returns: This runner, for chaining.
        """
        result = RunResult(exit_code=exit_code, stdout=stdout,
                           stderr=stderr, timed_out=timed_out)
        self._rules.append((predicate, result))
        rtnval = self
        return rtnval

    def set_default(self, *, stdout: str = "", stderr: str = "",
                    exit_code: int = 0) -> "MockCommandRunner":
        """
            Set the fallback result returned when no rule matches.

            :param stdout: Standard-output text to return.
            :param stderr: Standard-error text to return.
            :param exit_code: Process exit code to return.

            :returns: This runner, for chaining.
        """
        self._default = RunResult(exit_code=exit_code, stdout=stdout,
                                  stderr=stderr, timed_out=False)
        rtnval = self
        return rtnval

    def run(self, args: List[str], *, elevated: bool = False,
            cwd: Optional[str] = None,
            env: Optional[Dict[str, str]] = None,
            stdin: Optional[str] = None,
            timeout: Optional[float] = None,
            on_output: Optional[Callable[[str], None]] = None,
            on_error: Optional[Callable[[str], None]] = None,
            capture_output: bool = True) -> RunResult:
        """
            Execute a recorded command and return its seeded result.

            :param args: The ``pwsh`` argv list.
            :param elevated: Ignored; recorded only for compatibility.
            :param cwd: Ignored.
            :param env: Ignored.
            :param stdin: Ignored.
            :param timeout: Ignored.
            :param on_output: Ignored.
            :param on_error: Ignored.
            :param capture_output: Ignored.

            :returns: The matching seeded RunResult.
        """
        command = args[-1] if len(args) > 0 else ""
        self.invocations.append(command)
        self.argv_invocations.append(list(args))

        for predicate, result in self._rules:
            if predicate(command) is True:
                rtnval = result
                return rtnval

        if self._default is not None:
            rtnval = self._default
            return rtnval

        rtnval = RunResult(exit_code=0, stdout="", stderr="",
                           timed_out=False)
        return rtnval


__all__ = ["MockCommandRunner"]
