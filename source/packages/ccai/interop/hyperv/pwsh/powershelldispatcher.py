"""
    .. module:: powershelldispatcher
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`PowershellDispatcher` which
                   builds a cmdlet invocation, dispatches it through an
                   :class:`ICommandRunner`, and parses the JSON output.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import os

from typing import Any, Dict, List

from ccai.interfaces.icommandrunner import ICommandRunner, RunResult

from ccai.interop.hyperv.aspectshyperv import AspectsRunner
from ccai.interop.hyperv.exceptions.hypervcmdleterror import (
    HypervCmdletError
)
from ccai.interop.hyperv.pwsh.pwshjsonparser import (
    parse_json_output, parse_json_records
)
from ccai.interop.hyperv.pwsh.pwshscriptbuilder import PwshScriptBuilder


class PowershellDispatcher:
    """
        Builds and dispatches PowerShell cmdlet invocations.

        The dispatcher is the single seam between the typed API-group code
        and the injected :class:`ICommandRunner`.  It renders the argv,
        passes the elevation aspect through, reclassifies non-zero exits
        into :class:`HypervCmdletError`, and parses ``ConvertTo-Json``
        stdout into typed records.
    """

    def __init__(self, *, runner: ICommandRunner) -> None:
        """
            Initialise a PowershellDispatcher.

            :param runner: The ICommandRunner used to execute cmdlets.
        """
        self._runner: ICommandRunner = runner
        return

    def dispatch_record(self, *, builder: PwshScriptBuilder,
                        aspects: AspectsRunner) -> Any:
        """
            Dispatch a cmdlet and return its parsed JSON object.

            :param builder: A configured PwshScriptBuilder.
            :param aspects: AspectsRunner controlling behaviour.

            :returns: A dict, list, scalar, or ``None``.
            :raises: HypervCmdletError
        """
        command_line = builder.render()
        run_result = self._run(builder=builder, aspects=aspects)
        rtnval = parse_json_output(stdout=run_result.stdout,
                                   command_line=command_line)
        return rtnval

    def dispatch_records(self, *, builder: PwshScriptBuilder,
                         aspects: AspectsRunner) -> List[Dict[str, Any]]:
        """
            Dispatch a cmdlet and return a list of parsed JSON records.

            :param builder: A configured PwshScriptBuilder.
            :param aspects: AspectsRunner controlling behaviour.

            :returns: A list of dict records (possibly empty).
            :raises: HypervCmdletError
        """
        command_line = builder.render()
        run_result = self._run(builder=builder, aspects=aspects)
        rtnval = parse_json_records(stdout=run_result.stdout,
                                    command_line=command_line)
        return rtnval

    def dispatch_void(self, *, builder: PwshScriptBuilder,
                      aspects: AspectsRunner) -> None:
        """
            Dispatch a cmdlet with no useful object output.

            :param builder: A configured PwshScriptBuilder.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        self._run(builder=builder, aspects=aspects)
        return

    def _run(self, *, builder: PwshScriptBuilder,
             aspects: AspectsRunner) -> RunResult:
        """
            Execute the rendered cmdlet through the runner and check the
            exit code.

            :param builder: A configured PwshScriptBuilder.
            :param aspects: AspectsRunner controlling behaviour.

            :returns: The RunResult.
            :raises: HypervCmdletError
        """
        argv = builder.render_argv()
        command_line = builder.render()

        run_result = self._runner.run(
            argv,
            elevated=aspects.elevated,
            timeout=aspects.connection_timeout,
        )

        if run_result.timed_out is True:
            err_msg_lines = ["Hyper-V cmdlet timed out."]
            err_msg_lines.append("COMMAND: {}".format(command_line))
            err_msg_lines.append("TIMEOUT: {}".format(
                aspects.connection_timeout
            ))
            err_msg = os.linesep.join(err_msg_lines)
            raise HypervCmdletError(err_msg, command_line=command_line,
                                    exit_code=run_result.exit_code,
                                    stderr=run_result.stderr)

        if run_result.exit_code is not None and run_result.exit_code != 0:
            err_msg_lines = ["Hyper-V cmdlet exited non-zero."]
            err_msg_lines.append("COMMAND: {}".format(command_line))
            err_msg_lines.append("EXIT-CODE: {}".format(
                run_result.exit_code
            ))
            err_msg_lines.append("STDERR:")
            err_msg_lines.append("    {}".format(run_result.stderr.strip()))
            err_msg = os.linesep.join(err_msg_lines)
            raise HypervCmdletError(err_msg, command_line=command_line,
                                    exit_code=run_result.exit_code,
                                    stderr=run_result.stderr)

        rtnval = run_result
        return rtnval


__all__ = ["PowershellDispatcher"]
