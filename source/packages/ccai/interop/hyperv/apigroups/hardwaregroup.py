"""
    .. module:: hardwaregroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`HardwareGroup` API group for
                   configuring VM hardware.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from ccai.interop.hyperv.aspectshyperv import (
    AspectsRunner, DEFAULT_HYPERV_ASPECTS
)
from ccai.interop.hyperv.apigroups.vmsgroup import VmsGroup
from ccai.interop.hyperv.exceptions.hypervcmdleterror import HypervCmdletError
from ccai.interop.hyperv.pwsh.powershelldispatcher import (
    PowershellDispatcher
)
from ccai.interop.hyperv.pwsh.pwshscriptbuilder import PwshScriptBuilder


class HardwareGroup:
    """
        API group covering VM hardware configuration with no-op-on-match
        idempotency.
    """

    def __init__(self, *, dispatcher: PowershellDispatcher,
                 vms_group: VmsGroup) -> None:
        """
            Initialise a HardwareGroup.

            :param dispatcher: The PowershellDispatcher used for cmdlets.
            :param vms_group: The VmsGroup used to read current values.
        """
        self._dispatcher: PowershellDispatcher = dispatcher
        self._vms_group: VmsGroup = vms_group
        return

    def set_vm_processor(self, *, name: str, count: int,
                         aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                         ) -> None:
        """
            Set the processor count with ``Set-VMProcessor`` (no-op on
            match).

            :param name: The VM name.
            :param count: The desired logical processor count.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        current = self._vms_group.get_vm(name=name, aspects=aspects)
        if current is not None and current.processor_count == count:
            return

        builder = PwshScriptBuilder(cmdlet="Set-VMProcessor")
        builder.parameter(name="VMName", value=name)
        builder.literal_parameter(name="Count", value=str(count))
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)
        return

    def set_vm_memory(self, *, name: str, startup_bytes: int,
                      dynamic: bool = False,
                      min_bytes: int = 0, max_bytes: int = 0,
                      aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                      ) -> None:
        """
            Set memory with ``Set-VMMemory`` (no-op on match).

            :param name: The VM name.
            :param startup_bytes: Startup memory in bytes.
            :param dynamic: Whether dynamic memory is enabled.
            :param min_bytes: Minimum memory for dynamic mode.
            :param max_bytes: Maximum memory for dynamic mode.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        current = self._vms_group.get_vm(name=name, aspects=aspects)
        if current is not None:
            if current.memory_startup_bytes == startup_bytes and dynamic is False:
                return

        builder = PwshScriptBuilder(cmdlet="Set-VMMemory")
        builder.parameter(name="VMName", value=name)
        builder.literal_parameter(name="StartupBytes",
                                  value=str(startup_bytes))
        if dynamic is True:
            builder.literal_parameter(name="DynamicMemoryEnabled",
                                      value="true")
            if min_bytes > 0:
                builder.literal_parameter(name="MinimumBytes",
                                          value=str(min_bytes))
            if max_bytes > 0:
                builder.literal_parameter(name="MaximumBytes",
                                          value=str(max_bytes))
        else:
            builder.literal_parameter(name="DynamicMemoryEnabled",
                                      value="false")
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)
        return

    def set_vm_secure_boot(self, *, name: str, enabled: bool,
                           aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                           ) -> None:
        """
            Set Secure Boot with ``Set-VMFirmware``.

            :param name: The VM name.
            :param enabled: Whether Secure Boot is enabled.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        builder = PwshScriptBuilder(cmdlet="Set-VMFirmware")
        builder.parameter(name="VMName", value=name)
        if enabled is True:
            builder.literal_parameter(name="EnableSecureBoot", value="On")
        else:
            builder.literal_parameter(name="EnableSecureBoot", value="Off")
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)
        return

    def set_vm_generation(self, *, name: str, generation: int,
                          aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                          ) -> None:
        """
            Report the desired VM generation; a no-op on match.

            Hyper-V generation is fixed at create time and cannot be
            mutated in place.  When the current generation already
            matches this call is a no-op; otherwise a HypervCmdletError
            is raised naming the immutability.

            :param name: The VM name.
            :param generation: The desired generation (1 or 2).
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        current = self._vms_group.get_vm(name=name, aspects=aspects)
        if current is not None and current.generation == generation:
            return

        err_msg = (
            "Hyper-V VM generation is immutable; recreate the VM to "
            "change generation for {!r}.".format(name)
        )
        raise HypervCmdletError(err_msg)


__all__ = ["HardwareGroup"]
