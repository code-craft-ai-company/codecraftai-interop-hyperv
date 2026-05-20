"""
    .. module:: hypervvm
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`HypervVm` record.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class HypervVm:
    """
        Typed record describing a virtual machine as reported by
        ``Get-VM``.
    """
    name: str
    vm_id: str
    state: str
    generation: int
    processor_count: int
    memory_startup_bytes: int
    notes: str
    ip_addresses: List[str] = field(default_factory=list)

    @classmethod
    def from_json(cls, record: Dict[str, Any]) -> "HypervVm":
        """
            Build a HypervVm from a ``Get-VM`` / ``New-VM`` JSON record.

            :param record: The parsed JSON object.

            :returns: A HypervVm instance.
        """
        name = str(record.get("Name", ""))
        vm_id = str(record.get("Id", record.get("VMId", "")))
        state = str(record.get("State", ""))
        generation = int(record.get("Generation", 2))
        processor_count = int(record.get("ProcessorCount", 0))
        memory_startup_bytes = int(record.get("MemoryStartup", 0))
        notes = str(record.get("Notes", ""))

        raw_ips = record.get("IPAddresses", None)
        ip_addresses: List[str] = []
        if isinstance(raw_ips, list):
            for entry in raw_ips:
                ip_addresses.append(str(entry))
        elif isinstance(raw_ips, str) and len(raw_ips) > 0:
            ip_addresses.append(raw_ips)

        rtnval = cls(name=name, vm_id=vm_id, state=state,
                     generation=generation,
                     processor_count=processor_count,
                     memory_startup_bytes=memory_startup_bytes,
                     notes=notes, ip_addresses=ip_addresses)
        return rtnval
