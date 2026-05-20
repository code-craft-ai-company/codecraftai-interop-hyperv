"""
    .. module:: hypervvhdxspec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`HypervVhdxSpec` request
                   object for creating a VHDX disk.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Optional

from automojo.errors.exceptions import SemanticError


class HypervVhdxSpec:
    """
        Request object describing a VHDX disk to create.
    """

    def __init__(self, *, path: str, size_bytes: int,
                 dynamic: bool = True,
                 parent_path: Optional[str] = None) -> None:
        """
            Initialise a HypervVhdxSpec.

            :param path: The destination path of the VHDX file.
            :param size_bytes: The disk size in bytes; must be > 0.
            :param dynamic: Whether the VHDX is dynamically expanding.
            :param parent_path: Optional parent path for a differencing
                disk.

            :raises: SemanticError
        """
        if path is None or len(path) == 0:
            raise SemanticError("HypervVhdxSpec requires a 'path'.")

        if size_bytes is None or size_bytes <= 0:
            raise SemanticError(
                "HypervVhdxSpec requires 'size_bytes' greater than zero."
            )

        self.path: str = path
        self.size_bytes: int = size_bytes
        self.dynamic: bool = dynamic
        self.parent_path: Optional[str] = parent_path
        return
