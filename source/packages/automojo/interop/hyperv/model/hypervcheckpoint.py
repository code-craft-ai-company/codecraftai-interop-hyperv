"""
    .. module:: hypervcheckpoint
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`HypervCheckpoint` record.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class HypervCheckpoint:
    """
        Typed record describing a VM checkpoint (snapshot) as reported by
        ``Get-VMSnapshot``.
    """
    vm_name: str
    name: str
    snapshot_id: str
    parent_snapshot_name: str

    @classmethod
    def from_json(cls, record: Dict[str, Any]) -> "HypervCheckpoint":
        """
            Build a HypervCheckpoint from a ``Get-VMSnapshot`` record.

            :param record: The parsed JSON object.

            :returns: A HypervCheckpoint instance.
        """
        vm_name = str(record.get("VMName", ""))
        name = str(record.get("Name", ""))
        snapshot_id = str(record.get("Id", ""))
        parent = record.get("ParentSnapshotName", None)
        parent_snapshot_name = str(parent) if parent is not None else ""

        rtnval = cls(vm_name=vm_name, name=name, snapshot_id=snapshot_id,
                     parent_snapshot_name=parent_snapshot_name)
        return rtnval
