"""
    .. module:: hypervadapterspec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`HypervAdapterSpec` request
                   object for adding a VM network adapter.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Optional

from ccai.errors.exceptions import SemanticError


class HypervAdapterSpec:
    """
        Request object describing a VM network adapter to attach.
    """

    def __init__(self, *, vm_name: str, switch_name: str,
                 mac_address: Optional[str] = None,
                 adapter_name: Optional[str] = None) -> None:
        """
            Initialise a HypervAdapterSpec.

            :param vm_name: The owning VM name.
            :param switch_name: The virtual switch to connect to.
            :param mac_address: Optional static MAC address.
            :param adapter_name: Optional adapter name.

            :raises: SemanticError
        """
        if vm_name is None or len(vm_name) == 0:
            raise SemanticError("HypervAdapterSpec requires a 'vm_name'.")

        if switch_name is None or len(switch_name) == 0:
            raise SemanticError(
                "HypervAdapterSpec requires a 'switch_name'."
            )

        self.vm_name: str = vm_name
        self.switch_name: str = switch_name
        self.mac_address: Optional[str] = mac_address
        self.adapter_name: Optional[str] = adapter_name
        return
