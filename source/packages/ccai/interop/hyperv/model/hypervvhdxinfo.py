"""
    .. module:: hypervvhdxinfo
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`HypervVhdxInfo` record.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class HypervVhdxInfo:
    """
        Typed record describing a VHDX disk as reported by ``Get-VHD``.
    """
    path: str
    size_bytes: int
    vhd_type: str
    parent_path: Optional[str]

    @classmethod
    def from_json(cls, record: Dict[str, Any]) -> "HypervVhdxInfo":
        """
            Build a HypervVhdxInfo from a ``Get-VHD`` / ``New-VHD`` record.

            :param record: The parsed JSON object.

            :returns: A HypervVhdxInfo instance.
        """
        path = str(record.get("Path", ""))
        size_bytes = int(record.get("Size", 0))
        vhd_type = str(record.get("VhdType", ""))
        parent = record.get("ParentPath", None)
        normalized_parent = str(parent) if parent is not None else None

        rtnval = cls(path=path, size_bytes=size_bytes, vhd_type=vhd_type,
                     parent_path=normalized_parent)
        return rtnval

    @property
    def is_dynamic(self) -> bool:
        """
            Report whether this VHDX is dynamically expanding.

            :returns: True when the ``vhd_type`` is dynamic.
        """
        rtnval = self.vhd_type.lower() == "dynamic"
        return rtnval
