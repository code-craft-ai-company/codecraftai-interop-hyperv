"""
    .. module:: hostgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`HostGroup` API group for
                   querying Hyper-V host capability information.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from automojo.interop.hyperv.aspectshyperv import (
    AspectsRunner, DEFAULT_HYPERV_ASPECTS
)
from automojo.interop.hyperv.exceptions.hypervcmdleterror import (
    HypervCmdletError
)
from automojo.interop.hyperv.model.hypervhostinfo import HypervHostInfo
from automojo.interop.hyperv.pwsh.powershelldispatcher import (
    PowershellDispatcher
)
from automojo.interop.hyperv.pwsh.pwshscriptbuilder import PwshScriptBuilder


class HostGroup:
    """
        API group covering Hyper-V host capability information.
    """

    def __init__(self, *, dispatcher: PowershellDispatcher) -> None:
        """
            Initialise a HostGroup.

            :param dispatcher: The PowershellDispatcher used for cmdlets.
        """
        self._dispatcher: PowershellDispatcher = dispatcher
        return

    def host_info(self, *,
                  aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                  ) -> HypervHostInfo:
        """
            Query the Hyper-V host with ``Get-VMHost``.

            :param aspects: AspectsRunner controlling behaviour.

            :returns: A HypervHostInfo record.
            :raises: HypervCmdletError
        """
        builder = PwshScriptBuilder(cmdlet="Get-VMHost")
        record = self._dispatcher.dispatch_record(builder=builder,
                                                  aspects=aspects)
        if record is None or not isinstance(record, dict):
            raise HypervCmdletError(
                "Get-VMHost returned no host record.",
                command_line=builder.render()
            )

        rtnval = HypervHostInfo.from_json(record)
        return rtnval


__all__ = ["HostGroup"]
