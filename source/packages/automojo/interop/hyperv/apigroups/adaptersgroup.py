"""
    .. module:: adaptersgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`AdaptersGroup` API group for
                   attaching and detaching virtual NICs and disks.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import List

from automojo.interop.hyperv.aspectshyperv import (
    AspectsRunner, DEFAULT_HYPERV_ASPECTS
)
from automojo.interop.hyperv.model.hypervadapter import HypervAdapter
from automojo.interop.hyperv.pwsh.powershelldispatcher import (
    PowershellDispatcher
)
from automojo.interop.hyperv.pwsh.pwshscriptbuilder import PwshScriptBuilder
from automojo.interop.hyperv.specs.hypervadapterspec import HypervAdapterSpec


class AdaptersGroup:
    """
        API group covering VM network adapter and hard disk attach-detach.
    """

    def __init__(self, *, dispatcher: PowershellDispatcher) -> None:
        """
            Initialise an AdaptersGroup.

            :param dispatcher: The PowershellDispatcher used for cmdlets.
        """
        self._dispatcher: PowershellDispatcher = dispatcher
        return

    def list_network_adapters(self, *, name: str,
                              aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                              ) -> List[HypervAdapter]:
        """
            List a VM's network adapters with ``Get-VMNetworkAdapter``.

            :param name: The VM name.
            :param aspects: AspectsRunner controlling behaviour.

            :returns: A list of HypervAdapter records.
            :raises: HypervCmdletError
        """
        builder = PwshScriptBuilder(cmdlet="Get-VMNetworkAdapter")
        builder.parameter(name="VMName", value=name)
        records = self._dispatcher.dispatch_records(builder=builder,
                                                   aspects=aspects)
        rtnval: List[HypervAdapter] = []
        for record in records:
            rtnval.append(HypervAdapter.from_json(record))
        return rtnval

    def add_vm_network_adapter(self, *, spec: HypervAdapterSpec,
                               aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                               ) -> None:
        """
            Attach a network adapter with ``Add-VMNetworkAdapter``
            (idempotent on MAC address when supplied).

            :param spec: The HypervAdapterSpec describing the adapter.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        if spec.mac_address is not None:
            for adapter in self.list_network_adapters(name=spec.vm_name,
                                                      aspects=aspects):
                if adapter.mac_address == spec.mac_address:
                    return

        builder = PwshScriptBuilder(cmdlet="Add-VMNetworkAdapter")
        builder.parameter(name="VMName", value=spec.vm_name)
        builder.parameter(name="SwitchName", value=spec.switch_name)
        if spec.adapter_name is not None:
            builder.parameter(name="Name", value=spec.adapter_name)
        if spec.mac_address is not None:
            builder.parameter(name="StaticMacAddress",
                              value=spec.mac_address)
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)
        return

    def remove_vm_network_adapter(self, *, name: str, mac: str,
                                  aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                                  ) -> None:
        """
            Detach a network adapter with ``Remove-VMNetworkAdapter``.

            Removing an absent adapter is a no-op.

            :param name: The VM name.
            :param mac: The MAC address identifying the adapter.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        present = False
        for adapter in self.list_network_adapters(name=name,
                                                  aspects=aspects):
            if adapter.mac_address == mac:
                present = True

        if present is False:
            return

        builder = PwshScriptBuilder(cmdlet="Remove-VMNetworkAdapter")
        builder.parameter(name="VMName", value=name)
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)
        return

    def add_vm_hard_disk(self, *, name: str, vhdx_path: str,
                         controller_type: str = "SCSI",
                         aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                         ) -> None:
        """
            Attach a hard disk with ``Add-VMHardDiskDrive`` (idempotent).

            :param name: The VM name.
            :param vhdx_path: The VHDX file path to attach.
            :param controller_type: SCSI or IDE.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        builder = PwshScriptBuilder(cmdlet="Add-VMHardDiskDrive")
        builder.parameter(name="VMName", value=name)
        builder.literal_parameter(name="ControllerType",
                                  value=controller_type)
        builder.parameter(name="Path", value=vhdx_path)
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)
        return

    def remove_vm_hard_disk(self, *, name: str,
                            controller_type: str,
                            controller_number: int,
                            controller_location: int,
                            aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                            ) -> None:
        """
            Detach a hard disk with ``Remove-VMHardDiskDrive``.

            :param name: The VM name.
            :param controller_type: SCSI or IDE.
            :param controller_number: The controller number.
            :param controller_location: The controller location slot.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        builder = PwshScriptBuilder(cmdlet="Remove-VMHardDiskDrive")
        builder.parameter(name="VMName", value=name)
        builder.literal_parameter(name="ControllerType",
                                  value=controller_type)
        builder.literal_parameter(name="ControllerNumber",
                                  value=str(controller_number))
        builder.literal_parameter(name="ControllerLocation",
                                  value=str(controller_location))
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)
        return

    def add_vm_dvd_drive(self, *, name: str, iso_path: str,
                         aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                         ) -> None:
        """
            Attach a DVD drive backed by an ISO with ``Add-VMDvdDrive``.

            Used to mount a NoCloud cloud-init config-drive ISO.

            :param name: The VM name.
            :param iso_path: The ISO file path to mount.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        builder = PwshScriptBuilder(cmdlet="Add-VMDvdDrive")
        builder.parameter(name="VMName", value=name)
        builder.parameter(name="Path", value=iso_path)
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)
        return


__all__ = ["AdaptersGroup"]
