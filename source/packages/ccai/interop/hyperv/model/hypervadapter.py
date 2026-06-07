"""
    .. module:: hypervadapter
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`HypervAdapter` record.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class HypervAdapter:
    """
        Typed record describing a VM network adapter as reported by
        ``Get-VMNetworkAdapter``.
    """
    vm_name: str
    name: str
    switch_name: Optional[str]
    mac_address: str

    @classmethod
    def from_json(cls, record: Dict[str, Any]) -> "HypervAdapter":
        """
            Build a HypervAdapter from a ``Get-VMNetworkAdapter`` record.

            :param record: The parsed JSON object.

            :returns: A HypervAdapter instance.
        """
        vm_name = str(record.get("VMName", ""))
        name = str(record.get("Name", ""))
        switch = record.get("SwitchName", None)
        normalized_switch = str(switch) if switch is not None else None
        mac_address = str(record.get("MacAddress", ""))

        rtnval = cls(vm_name=vm_name, name=name,
                     switch_name=normalized_switch,
                     mac_address=mac_address)
        return rtnval
