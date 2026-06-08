"""
    .. module:: pwshquote
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :func:`pwsh_quote` safe argument
                   composer used for every caller-supplied substitution in a
                   PowerShell command.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import os

from ccai.errors.exceptions import SemanticError


def pwsh_quote(*, value: str) -> str:
    """
        Quote a string for safe inclusion in a PowerShell command line.

        PowerShell single-quoted strings are literal: the only character
        requiring escaping is the single quote itself, which is escaped by
        doubling it.  No other character — including ``"``, ``;``, ``|``,
        ``$``, and backtick — has special meaning inside a single-quoted
        string, so this rendering eliminates command injection.

        Newline and null bytes cannot appear in a single-statement command
        line and are rejected outright.

        :param value: The raw string to quote.

        :returns: The single-quoted, injection-safe PowerShell literal.
        :raises: SemanticError
    """
    if value is None:
        raise SemanticError(
            "pwsh_quote requires a non-None 'value' substitution."
        )

    if not isinstance(value, str):
        raise SemanticError(
            "pwsh_quote requires a str 'value', got {!r}.".format(
                type(value).__name__
            )
        )

    if "\n" in value or "\r" in value:
        err_msg_lines = ["pwsh_quote rejected a substitution with a newline."]
        err_msg_lines.append("VALUE: {!r}".format(value))
        err_msg = os.linesep.join(err_msg_lines)
        raise SemanticError(err_msg)

    if "\x00" in value:
        err_msg_lines = ["pwsh_quote rejected a substitution with a null byte."]
        err_msg_lines.append("VALUE: {!r}".format(value))
        err_msg = os.linesep.join(err_msg_lines)
        raise SemanticError(err_msg)

    doubled = value.replace("'", "''")
    rtnval = "'{}'".format(doubled)
    return rtnval


def pwsh_unquote(*, literal: str) -> str:
    """
        Reverse :func:`pwsh_quote`, recovering the original string.

        Used by the property-based round-trip test to assert that quoting
        is lossless for every accepted input.

        :param literal: A PowerShell single-quoted literal.

        :returns: The original unquoted string.
        :raises: SemanticError
    """
    if literal is None or len(literal) < 2:
        raise SemanticError(
            "pwsh_unquote requires a quoted literal of length >= 2."
        )

    if literal[0] != "'" or literal[-1] != "'":
        raise SemanticError(
            "pwsh_unquote requires a single-quoted literal."
        )

    inner = literal[1:-1]
    rtnval = inner.replace("''", "'")
    return rtnval


__all__ = ["pwsh_quote", "pwsh_unquote"]
