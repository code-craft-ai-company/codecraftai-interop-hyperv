"""
    .. module:: hypervhostinfo
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`HypervHostInfo` record.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class HypervHostInfo:
    """
        Typed record describing a Hyper-V host as reported by
        ``Get-VMHost``.
    """
    computer_name: str
    logical_processor_count: int
    memory_capacity: int
    virtual_machine_path: str
    virtual_hard_disk_path: str

    @classmethod
    def from_json(cls, record: Dict[str, Any]) -> "HypervHostInfo":
        """
            Build a HypervHostInfo from a ``Get-VMHost`` JSON record.

            :param record: The parsed JSON object.

            :returns: A HypervHostInfo instance.
        """
        computer_name = str(record.get("ComputerName", ""))
        logical_processor_count = int(record.get("LogicalProcessorCount", 0))
        memory_capacity = int(record.get("MemoryCapacity", 0))
        virtual_machine_path = str(record.get("VirtualMachinePath", ""))
        virtual_hard_disk_path = str(record.get("VirtualHardDiskPath", ""))

        rtnval = cls(computer_name=computer_name,
                     logical_processor_count=logical_processor_count,
                     memory_capacity=memory_capacity,
                     virtual_machine_path=virtual_machine_path,
                     virtual_hard_disk_path=virtual_hard_disk_path)
        return rtnval
