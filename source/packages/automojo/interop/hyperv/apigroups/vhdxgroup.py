"""
    .. module:: vhdxgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`VhdxGroup` API group for
                   managing VHDX virtual disks.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Optional

from automojo.interop.hyperv.aspectshyperv import (
    AspectsRunner, DEFAULT_HYPERV_ASPECTS
)
from automojo.interop.hyperv.exceptions.hypervcmdleterror import (
    HypervCmdletError
)
from automojo.interop.hyperv.model.hypervvhdxinfo import HypervVhdxInfo
from automojo.interop.hyperv.pwsh.powershelldispatcher import (
    PowershellDispatcher
)
from automojo.interop.hyperv.pwsh.pwshscriptbuilder import PwshScriptBuilder
from automojo.interop.hyperv.specs.hypervvhdxspec import HypervVhdxSpec


class VhdxGroup:
    """
        API group covering VHDX virtual disk lifecycle.
    """

    def __init__(self, *, dispatcher: PowershellDispatcher) -> None:
        """
            Initialise a VhdxGroup.

            :param dispatcher: The PowershellDispatcher used for cmdlets.
        """
        self._dispatcher: PowershellDispatcher = dispatcher
        return

    def get_vhdx(self, *, path: str,
                 aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                 ) -> Optional[HypervVhdxInfo]:
        """
            Look up a VHDX with ``Get-VHD``.

            :param path: The VHDX file path.
            :param aspects: AspectsRunner controlling behaviour.

            :returns: A HypervVhdxInfo or None when absent.
            :raises: HypervCmdletError
        """
        builder = PwshScriptBuilder(cmdlet="Get-VHD")
        builder.parameter(name="Path", value=path)
        builder.literal_parameter(name="ErrorAction", value="SilentlyContinue")

        record = self._dispatcher.dispatch_record(builder=builder,
                                                  aspects=aspects)
        if record is None or not isinstance(record, dict):
            rtnval = None
            return rtnval

        rtnval = HypervVhdxInfo.from_json(record)
        return rtnval

    def new_vhdx(self, *, spec: HypervVhdxSpec,
                 aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                 ) -> HypervVhdxInfo:
        """
            Create a VHDX with ``New-VHD`` (idempotent).

            An existing VHDX at the same path matching the requested size
            and dynamic flag is returned without mutation.

            :param spec: The HypervVhdxSpec describing the disk.
            :param aspects: AspectsRunner controlling behaviour.

            :returns: The created or pre-existing HypervVhdxInfo.
            :raises: HypervCmdletError
        """
        existing = self.get_vhdx(path=spec.path, aspects=aspects)
        if existing is not None:
            size_matches = existing.size_bytes == spec.size_bytes
            dynamic_matches = existing.is_dynamic == spec.dynamic
            if size_matches is True and dynamic_matches is True:
                rtnval = existing
                return rtnval

        builder = PwshScriptBuilder(cmdlet="New-VHD")
        builder.parameter(name="Path", value=spec.path)

        if spec.parent_path is not None:
            builder.parameter(name="ParentPath", value=spec.parent_path)
            builder.switch(name="Differencing")
        else:
            builder.literal_parameter(name="SizeBytes",
                                      value=str(spec.size_bytes))
            if spec.dynamic is True:
                builder.switch(name="Dynamic")
            else:
                builder.switch(name="Fixed")

        record = self._dispatcher.dispatch_record(builder=builder,
                                                  aspects=aspects)
        if record is None or not isinstance(record, dict):
            raise HypervCmdletError(
                "New-VHD returned no disk record.",
                command_line=builder.render()
            )

        rtnval = HypervVhdxInfo.from_json(record)
        return rtnval

    def resize_vhdx(self, *, path: str, size_bytes: int,
                    aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                    ) -> None:
        """
            Resize a VHDX with ``Resize-VHD``.

            :param path: The VHDX file path.
            :param size_bytes: The new size in bytes.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        builder = PwshScriptBuilder(cmdlet="Resize-VHD")
        builder.parameter(name="Path", value=path)
        builder.literal_parameter(name="SizeBytes", value=str(size_bytes))
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)
        return

    def delete_vhdx(self, *, path: str,
                    aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                    ) -> None:
        """
            Delete a VHDX with ``Remove-Item``.

            Deleting an absent path is a no-op.

            :param path: The VHDX file path.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        existing = self.get_vhdx(path=path, aspects=aspects)
        if existing is None:
            return

        builder = PwshScriptBuilder(cmdlet="Remove-Item")
        builder.parameter(name="Path", value=path)
        builder.switch(name="Force")
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)
        return


__all__ = ["VhdxGroup"]
