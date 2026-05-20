"""
    .. module:: switchesgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`SwitchesGroup` API group for
                   managing Hyper-V virtual switches.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import List, Optional

from automojo.interop.hyperv.aspectshyperv import (
    AspectsRunner, DEFAULT_HYPERV_ASPECTS
)
from automojo.interop.hyperv.exceptions.hypervcmdleterror import (
    HypervCmdletError
)
from automojo.interop.hyperv.model.hypervvirtualswitch import (
    HypervVirtualSwitch
)
from automojo.interop.hyperv.pwsh.powershelldispatcher import (
    PowershellDispatcher
)
from automojo.interop.hyperv.pwsh.pwshscriptbuilder import PwshScriptBuilder
from automojo.interop.hyperv.specs.hypervswitchspec import HypervSwitchSpec


class SwitchesGroup:
    """
        API group covering Hyper-V virtual switch lifecycle.
    """

    def __init__(self, *, dispatcher: PowershellDispatcher) -> None:
        """
            Initialise a SwitchesGroup.

            :param dispatcher: The PowershellDispatcher used for cmdlets.
        """
        self._dispatcher: PowershellDispatcher = dispatcher
        return

    def list_switches(self, *,
                      aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                      ) -> List[HypervVirtualSwitch]:
        """
            List virtual switches with ``Get-VMSwitch``.

            :param aspects: AspectsRunner controlling behaviour.

            :returns: A list of HypervVirtualSwitch records.
            :raises: HypervCmdletError
        """
        builder = PwshScriptBuilder(cmdlet="Get-VMSwitch")
        records = self._dispatcher.dispatch_records(builder=builder,
                                                   aspects=aspects)
        rtnval: List[HypervVirtualSwitch] = []
        for record in records:
            rtnval.append(HypervVirtualSwitch.from_json(record))
        return rtnval

    def get_switch(self, *, name: str,
                   aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                   ) -> Optional[HypervVirtualSwitch]:
        """
            Look up a single virtual switch by name.

            :param name: The switch name.
            :param aspects: AspectsRunner controlling behaviour.

            :returns: A HypervVirtualSwitch or None when absent.
            :raises: HypervCmdletError
        """
        for switch in self.list_switches(aspects=aspects):
            if switch.name == name:
                rtnval = switch
                return rtnval
        rtnval = None
        return rtnval

    def new_switch(self, *, spec: HypervSwitchSpec,
                   aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                   ) -> HypervVirtualSwitch:
        """
            Create a virtual switch with ``New-VMSwitch`` (idempotent).

            When a switch with the same name already exists the existing
            record is returned without mutation.

            :param spec: The HypervSwitchSpec describing the switch.
            :param aspects: AspectsRunner controlling behaviour.

            :returns: The created or pre-existing HypervVirtualSwitch.
            :raises: HypervCmdletError
        """
        existing = self.get_switch(name=spec.name, aspects=aspects)
        if existing is not None:
            rtnval = existing
            return rtnval

        builder = PwshScriptBuilder(cmdlet="New-VMSwitch")
        builder.parameter(name="Name", value=spec.name)
        builder.literal_parameter(name="SwitchType",
                                  value=spec.switch_type)
        if spec.switch_type == "External" and spec.net_adapter_name is not None:
            builder.parameter(name="NetAdapterName",
                              value=spec.net_adapter_name)
            if spec.allow_management_os is True:
                builder.literal_parameter(name="AllowManagementOS",
                                          value="true")
            else:
                builder.literal_parameter(name="AllowManagementOS",
                                          value="false")

        record = self._dispatcher.dispatch_record(builder=builder,
                                                  aspects=aspects)
        if record is None or not isinstance(record, dict):
            raise HypervCmdletError(
                "New-VMSwitch returned no switch record.",
                command_line=builder.render()
            )

        rtnval = HypervVirtualSwitch.from_json(record)
        return rtnval

    def remove_switch(self, *, name: str,
                      aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                      ) -> None:
        """
            Remove a virtual switch with ``Remove-VMSwitch``.

            Removing an unknown switch is a no-op.

            :param name: The switch name.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        existing = self.get_switch(name=name, aspects=aspects)
        if existing is None:
            return

        builder = PwshScriptBuilder(cmdlet="Remove-VMSwitch")
        builder.parameter(name="Name", value=name)
        builder.switch(name="Force")
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)
        return


__all__ = ["SwitchesGroup"]
