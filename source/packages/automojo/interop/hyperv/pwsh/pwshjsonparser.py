"""
    .. module:: pwshjsonparser
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains :func:`parse_json_output` which parses
                   ``ConvertTo-Json -Compress`` stdout into Python records.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import json
import os

from typing import Any, Dict, List

from automojo.interop.hyperv.exceptions.hypervcmdleterror import (
    HypervCmdletError
)


def parse_json_output(*, stdout: str,
                      command_line: str) -> Any:
    """
        Parse ``ConvertTo-Json`` stdout into a Python object.

        ``ConvertTo-Json`` emits a JSON object for a single result and a
        JSON array for multiple results.  Empty stdout (a cmdlet matched
        nothing) parses to ``None``.

        :param stdout: The captured standard-output text.
        :param command_line: The rendered command, for error context.

        :returns: A dict, list, scalar, or ``None``.
        :raises: HypervCmdletError
    """
    stripped = stdout.strip()
    if len(stripped) == 0:
        rtnval = None
        return rtnval

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as xcpt:
        err_msg_lines = ["Failed to parse ConvertTo-Json cmdlet output."]
        err_msg_lines.append("COMMAND: {}".format(command_line))
        err_msg_lines.append("PARSE-ERROR: {}".format(xcpt))
        err_msg_lines.append("STDOUT (first 512 chars):")
        err_msg_lines.append("    {}".format(stripped[:512]))
        err_msg = os.linesep.join(err_msg_lines)
        raise HypervCmdletError(err_msg,
                                command_line=command_line) from None

    rtnval = parsed
    return rtnval


def parse_json_records(*, stdout: str,
                       command_line: str) -> List[Dict[str, Any]]:
    """
        Parse ``ConvertTo-Json`` stdout into a list of record dicts.

        Normalises the single-object / array / empty cases so callers
        always receive a list.

        :param stdout: The captured standard-output text.
        :param command_line: The rendered command, for error context.

        :returns: A list of dict records (possibly empty).
        :raises: HypervCmdletError
    """
    parsed = parse_json_output(stdout=stdout, command_line=command_line)

    if parsed is None:
        rtnval: List[Dict[str, Any]] = []
        return rtnval

    if isinstance(parsed, list):
        records: List[Dict[str, Any]] = []
        for entry in parsed:
            if isinstance(entry, dict):
                records.append(entry)
        rtnval = records
        return rtnval

    if isinstance(parsed, dict):
        rtnval = [parsed]
        return rtnval

    err_msg_lines = ["ConvertTo-Json output was not a record or array."]
    err_msg_lines.append("COMMAND: {}".format(command_line))
    err_msg_lines.append("TYPE: {}".format(type(parsed).__name__))
    err_msg = os.linesep.join(err_msg_lines)
    raise HypervCmdletError(err_msg, command_line=command_line)


__all__ = ["parse_json_output", "parse_json_records"]
