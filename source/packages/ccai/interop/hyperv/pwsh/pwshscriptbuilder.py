"""
    .. module:: pwshscriptbuilder
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`PwshScriptBuilder` which
                   composes deterministic, single-statement PowerShell
                   commands for dispatch through an :class:`ICommandRunner`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import os

from typing import List, Optional

from ccai.errors.exceptions import SemanticError

from ccai.interop.hyperv.pwsh.pwshquote import pwsh_quote


class PwshScriptBuilder:
    """
        Composer for a single-statement PowerShell cmdlet invocation.

        A builder is created for one cmdlet (``New-VM``, ``Get-VMSwitch``,
        ...).  Switch flags and quoted parameters are appended in a
        deterministic order, and :meth:`render` produces the final command
        line.  By default the rendered command is piped through
        ``ConvertTo-Json -Compress`` so the runner returns a structured
        wire shape.
    """

    def __init__(self, *, cmdlet: str) -> None:
        """
            Initialise a PwshScriptBuilder.

            :param cmdlet: The PowerShell cmdlet name (e.g. ``New-VM``).

            :raises: SemanticError
        """
        if cmdlet is None or len(cmdlet) == 0:
            raise SemanticError(
                "PwshScriptBuilder requires a non-empty 'cmdlet' name."
            )
        if "\n" in cmdlet or "\r" in cmdlet or ";" in cmdlet:
            raise SemanticError(
                "PwshScriptBuilder 'cmdlet' must be a single bare token."
            )

        self._cmdlet: str = cmdlet
        self._tokens: List[str] = []
        self._convert_to_json: bool = True
        self._json_depth: int = 6
        return

    def parameter(self, *, name: str, value: str) -> "PwshScriptBuilder":
        """
            Append a named parameter with a quoted string value.

            :param name: The cmdlet parameter name (without leading dash).
            :param value: The raw string value; quoted safely.

            :returns: This builder, for chaining.
            :raises: SemanticError
        """
        self._validate_param_name(name=name)
        quoted = pwsh_quote(value=value)
        self._tokens.append("-{} {}".format(name, quoted))
        rtnval = self
        return rtnval

    def literal_parameter(self, *, name: str,
                          value: str) -> "PwshScriptBuilder":
        """
            Append a named parameter with an unquoted literal value.

            Used for numeric and enumeration values that are not
            caller-supplied free text (e.g. ``-Count 4``,
            ``-SwitchType External``).  The value is validated to contain
            only safe characters.

            :param name: The cmdlet parameter name (without leading dash).
            :param value: The literal value (numbers, enum tokens).

            :returns: This builder, for chaining.
            :raises: SemanticError
        """
        self._validate_param_name(name=name)
        for ch in value:
            is_alnum = ch.isalnum()
            is_allowed = ch in ".-_"
            if not is_alnum and not is_allowed:
                err_msg_lines = [
                    "PwshScriptBuilder.literal_parameter rejected a value."
                ]
                err_msg_lines.append("NAME: {}".format(name))
                err_msg_lines.append("VALUE: {!r}".format(value))
                err_msg = os.linesep.join(err_msg_lines)
                raise SemanticError(err_msg)
        self._tokens.append("-{} {}".format(name, value))
        rtnval = self
        return rtnval

    def switch(self, *, name: str) -> "PwshScriptBuilder":
        """
            Append a boolean switch flag.

            :param name: The switch name (without leading dash).

            :returns: This builder, for chaining.
            :raises: SemanticError
        """
        self._validate_param_name(name=name)
        self._tokens.append("-{}".format(name))
        rtnval = self
        return rtnval

    def without_json(self) -> "PwshScriptBuilder":
        """
            Disable the trailing ``ConvertTo-Json`` pipe.

            Used for cmdlets that have no useful object output
            (``Start-VM``, ``Stop-VM``).

            :returns: This builder, for chaining.
        """
        self._convert_to_json = False
        rtnval = self
        return rtnval

    def render(self) -> str:
        """
            Render the deterministic, single-statement command line.

            :returns: The PowerShell command string.
        """
        parts: List[str] = [self._cmdlet]
        parts.extend(self._tokens)
        statement = " ".join(parts)

        if self._convert_to_json is True:
            rtnval = "{} | ConvertTo-Json -Depth {} -Compress".format(
                statement, self._json_depth
            )
            return rtnval

        rtnval = statement
        return rtnval

    def render_argv(self, *,
                    elevated_unused: Optional[bool] = None) -> List[str]:
        """
            Render the full ``pwsh`` argument vector for the runner.

            :param elevated_unused: Reserved for symmetry; elevation is a
                runner concern passed via the ICommandRunner ``elevated``
                keyword, not an argv entry.

            :returns: The argv list passed to ``ICommandRunner.run``.
        """
        rtnval = ["pwsh", "-NoProfile", "-NonInteractive", "-Command",
                  self.render()]
        return rtnval

    @staticmethod
    def _validate_param_name(*, name: str) -> None:
        """
            Validate a parameter or switch name is a safe bare token.

            :param name: The candidate name.

            :raises: SemanticError
        """
        if name is None or len(name) == 0:
            raise SemanticError(
                "PwshScriptBuilder parameter 'name' must be non-empty."
            )
        for ch in name:
            if not ch.isalnum():
                raise SemanticError(
                    "PwshScriptBuilder parameter 'name' must be "
                    "alphanumeric, got {!r}.".format(name)
                )
        return


__all__ = ["PwshScriptBuilder"]
