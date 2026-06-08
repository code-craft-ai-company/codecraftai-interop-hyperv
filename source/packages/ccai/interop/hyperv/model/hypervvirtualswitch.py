"""
    .. module:: hypervvirtualswitch
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`HypervVirtualSwitch` record.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class HypervVirtualSwitch:
    """
        Typed record describing a Hyper-V virtual switch as reported by
        ``Get-VMSwitch``.
    """
    name: str
    switch_type: str
    net_adapter_interface_description: Optional[str]
    switch_id: str

    @classmethod
    def from_json(cls, record: Dict[str, Any]) -> "HypervVirtualSwitch":
        """
            Build a HypervVirtualSwitch from a ``Get-VMSwitch`` record.

            :param record: The parsed JSON object.

            :returns: A HypervVirtualSwitch instance.
        """
        name = str(record.get("Name", ""))
        switch_type = str(record.get("SwitchType", ""))
        adapter_desc = record.get("NetAdapterInterfaceDescription", None)
        normalized_adapter = (
            str(adapter_desc) if adapter_desc is not None else None
        )
        switch_id = str(record.get("Id", record.get("SwitchId", "")))

        rtnval = cls(name=name, switch_type=switch_type,
                     net_adapter_interface_description=normalized_adapter,
                     switch_id=switch_id)
        return rtnval
