"""
    .. module:: vmsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`VmsGroup` API group for
                   managing virtual machine lifecycle.

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
from automojo.interop.hyperv.model.hypervvm import HypervVm
from automojo.interop.hyperv.pwsh.powershelldispatcher import (
    PowershellDispatcher
)
from automojo.interop.hyperv.pwsh.pwshscriptbuilder import PwshScriptBuilder
from automojo.interop.hyperv.specs.hypervvmcreatespec import HypervVmCreateSpec


class VmsGroup:
    """
        API group covering virtual machine lifecycle.
    """

    def __init__(self, *, dispatcher: PowershellDispatcher) -> None:
        """
            Initialise a VmsGroup.

            :param dispatcher: The PowershellDispatcher used for cmdlets.
        """
        self._dispatcher: PowershellDispatcher = dispatcher
        return

    def list_vms(self, *,
                 aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                 ) -> List[HypervVm]:
        """
            List virtual machines with ``Get-VM``.

            :param aspects: AspectsRunner controlling behaviour.

            :returns: A list of HypervVm records.
            :raises: HypervCmdletError
        """
        builder = PwshScriptBuilder(cmdlet="Get-VM")
        records = self._dispatcher.dispatch_records(builder=builder,
                                                   aspects=aspects)
        rtnval: List[HypervVm] = []
        for record in records:
            rtnval.append(HypervVm.from_json(record))
        return rtnval

    def get_vm(self, *, name: str,
               aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
               ) -> Optional[HypervVm]:
        """
            Look up a single VM by name with ``Get-VM``.

            :param name: The VM name.
            :param aspects: AspectsRunner controlling behaviour.

            :returns: A HypervVm or None when absent.
            :raises: HypervCmdletError
        """
        builder = PwshScriptBuilder(cmdlet="Get-VM")
        builder.parameter(name="Name", value=name)
        builder.literal_parameter(name="ErrorAction", value="SilentlyContinue")
        record = self._dispatcher.dispatch_record(builder=builder,
                                                  aspects=aspects)
        if record is None or not isinstance(record, dict):
            rtnval = None
            return rtnval

        rtnval = HypervVm.from_json(record)
        return rtnval

    def new_vm(self, *, spec: HypervVmCreateSpec,
               aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
               ) -> HypervVm:
        """
            Create a VM with ``New-VM`` (idempotent create).

            A VM of the same name is returned without mutation.

            :param spec: The HypervVmCreateSpec describing the VM.
            :param aspects: AspectsRunner controlling behaviour.

            :returns: The created or pre-existing HypervVm.
            :raises: HypervCmdletError
        """
        existing = self.get_vm(name=spec.name, aspects=aspects)
        if existing is not None:
            rtnval = existing
            return rtnval

        builder = PwshScriptBuilder(cmdlet="New-VM")
        builder.parameter(name="Name", value=spec.name)
        builder.literal_parameter(name="Generation",
                                  value=str(spec.generation))
        builder.literal_parameter(name="MemoryStartupBytes",
                                  value=str(spec.memory_startup_bytes))
        if spec.switch_name is not None:
            builder.parameter(name="SwitchName", value=spec.switch_name)
        if spec.vhd_path is not None:
            builder.parameter(name="VHDPath", value=spec.vhd_path)
        if spec.path is not None:
            builder.parameter(name="Path", value=spec.path)

        record = self._dispatcher.dispatch_record(builder=builder,
                                                  aspects=aspects)
        if record is None or not isinstance(record, dict):
            raise HypervCmdletError(
                "New-VM returned no VM record.",
                command_line=builder.render()
            )

        rtnval = HypervVm.from_json(record)
        return rtnval

    def start_vm(self, *, name: str,
                 aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS) -> None:
        """
            Start a VM with ``Start-VM``.

            :param name: The VM name.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        self._dispatch_simple(cmdlet="Start-VM", name=name, aspects=aspects)
        return

    def stop_vm(self, *, name: str, force: bool = True,
                aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS) -> None:
        """
            Stop a VM with ``Stop-VM``.

            :param name: The VM name.
            :param force: Whether to pass ``-Force``.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        builder = PwshScriptBuilder(cmdlet="Stop-VM")
        builder.parameter(name="Name", value=name)
        if force is True:
            builder.switch(name="Force")
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)
        return

    def shutdown_vm(self, *, name: str,
                    aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS) -> None:
        """
            Gracefully shut down a VM with ``Stop-VM`` (no ``-Force``).

            ``Stop-VM`` performs a graceful guest-OS shutdown through the
            Hyper-V integration services when ``-Force`` is omitted; the
            cmdlet has no ``-Shutdown`` parameter.

            :param name: The VM name.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        builder = PwshScriptBuilder(cmdlet="Stop-VM")
        builder.parameter(name="Name", value=name)
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)
        return

    def restart_vm(self, *, name: str,
                   aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS) -> None:
        """
            Restart a VM with ``Restart-VM``.

            :param name: The VM name.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        builder = PwshScriptBuilder(cmdlet="Restart-VM")
        builder.parameter(name="Name", value=name)
        builder.switch(name="Force")
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)
        return

    def remove_vm(self, *, name: str,
                  aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS) -> None:
        """
            Remove a VM with ``Remove-VM``.

            Removing an absent VM is a no-op.

            :param name: The VM name.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        existing = self.get_vm(name=name, aspects=aspects)
        if existing is None:
            return

        builder = PwshScriptBuilder(cmdlet="Remove-VM")
        builder.parameter(name="Name", value=name)
        builder.switch(name="Force")
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)
        return

    def set_vm_notes(self, *, name: str, notes: str,
                     aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                     ) -> None:
        """
            Set the ``Notes`` field of a VM with ``Set-VM``.

            :param name: The VM name.
            :param notes: The notes string.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        builder = PwshScriptBuilder(cmdlet="Set-VM")
        builder.parameter(name="Name", value=name)
        builder.parameter(name="Notes", value=notes)
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)
        return

    def _dispatch_simple(self, *, cmdlet: str, name: str,
                         aspects: AspectsRunner) -> None:
        """
            Dispatch a name-only VM cmdlet that produces no useful output.

            :param cmdlet: The cmdlet name.
            :param name: The VM name.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        builder = PwshScriptBuilder(cmdlet=cmdlet)
        builder.parameter(name="Name", value=name)
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)
        return


__all__ = ["VmsGroup"]
