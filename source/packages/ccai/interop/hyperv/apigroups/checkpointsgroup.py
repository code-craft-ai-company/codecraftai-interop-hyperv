"""
    .. module:: checkpointsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`CheckpointsGroup` API group
                   for managing VM checkpoints (snapshots).

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import List

from ccai.interop.hyperv.aspectshyperv import (
    AspectsRunner, DEFAULT_HYPERV_ASPECTS
)
from ccai.interop.hyperv.model.hypervcheckpoint import HypervCheckpoint
from ccai.interop.hyperv.pwsh.powershelldispatcher import (
    PowershellDispatcher
)
from ccai.interop.hyperv.pwsh.pwshscriptbuilder import PwshScriptBuilder


class CheckpointsGroup:
    """
        API group covering VM checkpoint (snapshot) management.
    """

    def __init__(self, *, dispatcher: PowershellDispatcher) -> None:
        """
            Initialise a CheckpointsGroup.

            :param dispatcher: The PowershellDispatcher used for cmdlets.
        """
        self._dispatcher: PowershellDispatcher = dispatcher
        return

    def list_checkpoints(self, *, name: str,
                         aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                         ) -> List[HypervCheckpoint]:
        """
            List checkpoints with ``Get-VMSnapshot``.

            :param name: The VM name.
            :param aspects: AspectsRunner controlling behaviour.

            :returns: A list of HypervCheckpoint records.
            :raises: HypervCmdletError
        """
        builder = PwshScriptBuilder(cmdlet="Get-VMSnapshot")
        builder.parameter(name="VMName", value=name)
        records = self._dispatcher.dispatch_records(builder=builder,
                                                   aspects=aspects)
        rtnval: List[HypervCheckpoint] = []
        for record in records:
            rtnval.append(HypervCheckpoint.from_json(record))
        return rtnval

    def checkpoint_vm(self, *, name: str, snapshot_name: str,
                      aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                      ) -> HypervCheckpoint:
        """
            Create a checkpoint with ``Checkpoint-VM`` (idempotent).

            A checkpoint of the same name is returned without mutation.

            :param name: The VM name.
            :param snapshot_name: The checkpoint name.
            :param aspects: AspectsRunner controlling behaviour.

            :returns: The created or pre-existing HypervCheckpoint.
            :raises: HypervCmdletError
        """
        for checkpoint in self.list_checkpoints(name=name, aspects=aspects):
            if checkpoint.name == snapshot_name:
                rtnval = checkpoint
                return rtnval

        builder = PwshScriptBuilder(cmdlet="Checkpoint-VM")
        builder.parameter(name="Name", value=name)
        builder.parameter(name="SnapshotName", value=snapshot_name)
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)

        for checkpoint in self.list_checkpoints(name=name, aspects=aspects):
            if checkpoint.name == snapshot_name:
                rtnval = checkpoint
                return rtnval

        rtnval = HypervCheckpoint(vm_name=name, name=snapshot_name,
                                  snapshot_id="", parent_snapshot_name="")
        return rtnval

    def restore_checkpoint(self, *, name: str, snapshot_name: str,
                           aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                           ) -> None:
        """
            Restore a checkpoint with ``Restore-VMSnapshot``.

            :param name: The VM name.
            :param snapshot_name: The checkpoint name.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        builder = PwshScriptBuilder(cmdlet="Restore-VMSnapshot")
        builder.parameter(name="VMName", value=name)
        builder.parameter(name="Name", value=snapshot_name)
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)
        return

    def remove_checkpoint(self, *, name: str, snapshot_name: str,
                          aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                          ) -> None:
        """
            Remove a checkpoint with ``Remove-VMSnapshot``.

            Removing an absent checkpoint is a no-op.

            :param name: The VM name.
            :param snapshot_name: The checkpoint name.
            :param aspects: AspectsRunner controlling behaviour.

            :raises: HypervCmdletError
        """
        present = False
        for checkpoint in self.list_checkpoints(name=name, aspects=aspects):
            if checkpoint.name == snapshot_name:
                present = True

        if present is False:
            return

        builder = PwshScriptBuilder(cmdlet="Remove-VMSnapshot")
        builder.parameter(name="VMName", value=name)
        builder.parameter(name="Name", value=snapshot_name)
        builder.without_json()
        self._dispatcher.dispatch_void(builder=builder, aspects=aspects)
        return


__all__ = ["CheckpointsGroup"]
