"""
    .. module:: jobsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`JobsGroup` API group for
                   querying background PowerShell jobs.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from ccai.interop.hyperv.aspectshyperv import (
    AspectsRunner, DEFAULT_HYPERV_ASPECTS
)
from ccai.interop.hyperv.exceptions.hypervcmdleterror import (
    HypervCmdletError
)
from ccai.interop.hyperv.model.hypervjobinfo import HypervJobInfo
from ccai.interop.hyperv.pwsh.powershelldispatcher import (
    PowershellDispatcher
)
from ccai.interop.hyperv.pwsh.pwshscriptbuilder import PwshScriptBuilder


class JobsGroup:
    """
        API group covering background PowerShell job introspection.
    """

    def __init__(self, *, dispatcher: PowershellDispatcher) -> None:
        """
            Initialise a JobsGroup.

            :param dispatcher: The PowershellDispatcher used for cmdlets.
        """
        self._dispatcher: PowershellDispatcher = dispatcher
        return

    def get(self, *, job_id: str,
            aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
            ) -> HypervJobInfo:
        """
            Query a background job with ``Get-Job``.

            :param job_id: The PowerShell job identifier.
            :param aspects: AspectsRunner controlling behaviour.

            :returns: A HypervJobInfo record.
            :raises: HypervCmdletError
        """
        builder = PwshScriptBuilder(cmdlet="Get-Job")
        builder.parameter(name="Id", value=job_id)
        record = self._dispatcher.dispatch_record(builder=builder,
                                                  aspects=aspects)
        if record is None or not isinstance(record, dict):
            err_msg = "Get-Job returned no job record for id {!r}.".format(
                job_id
            )
            raise HypervCmdletError(err_msg, command_line=builder.render())

        rtnval = HypervJobInfo.from_json(record)
        return rtnval


__all__ = ["JobsGroup"]
