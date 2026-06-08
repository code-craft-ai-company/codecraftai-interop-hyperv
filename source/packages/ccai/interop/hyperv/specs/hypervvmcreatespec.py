"""
    .. module:: hypervvmcreatespec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`HypervVmCreateSpec` request
                   object for creating a virtual machine.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Optional

from ccai.errors.exceptions import SemanticError


class HypervVmCreateSpec:
    """
        Request object describing a virtual machine to create with
        ``New-VM``.
    """

    def __init__(self, *, name: str, memory_startup_bytes: int,
                 generation: int = 2,
                 switch_name: Optional[str] = None,
                 vhd_path: Optional[str] = None,
                 path: Optional[str] = None) -> None:
        """
            Initialise a HypervVmCreateSpec.

            :param name: The VM name.
            :param memory_startup_bytes: Startup memory in bytes; > 0.
            :param generation: VM generation (1 or 2).
            :param switch_name: Optional virtual switch to connect.
            :param vhd_path: Optional existing VHDX to attach as boot disk.
            :param path: Optional host directory for the VM configuration.

            :raises: SemanticError
        """
        if name is None or len(name) == 0:
            raise SemanticError("HypervVmCreateSpec requires a 'name'.")

        if memory_startup_bytes is None or memory_startup_bytes <= 0:
            raise SemanticError(
                "HypervVmCreateSpec requires 'memory_startup_bytes' > 0."
            )

        if generation not in (1, 2):
            raise SemanticError(
                "HypervVmCreateSpec 'generation' must be 1 or 2, got "
                "{!r}.".format(generation)
            )

        self.name: str = name
        self.memory_startup_bytes: int = memory_startup_bytes
        self.generation: int = generation
        self.switch_name: Optional[str] = switch_name
        self.vhd_path: Optional[str] = vhd_path
        self.path: Optional[str] = path
        return
