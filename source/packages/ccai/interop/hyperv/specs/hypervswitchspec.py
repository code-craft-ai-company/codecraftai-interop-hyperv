"""
    .. module:: hypervswitchspec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`HypervSwitchSpec` request
                   object for creating a virtual switch.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import os

from typing import Optional

from ccai.errors.exceptions import SemanticError


_SUPPORTED_SWITCH_TYPES = ("External", "Internal", "Private")


class HypervSwitchSpec:
    """
        Request object describing a virtual switch to create.
    """

    def __init__(self, *, name: str, switch_type: str,
                 net_adapter_name: Optional[str] = None,
                 allow_management_os: bool = True) -> None:
        """
            Initialise a HypervSwitchSpec.

            :param name: The switch name.
            :param switch_type: One of External, Internal, Private.
            :param net_adapter_name: Required physical adapter name when
                ``switch_type`` is External.
            :param allow_management_os: Whether the management OS keeps
                connectivity through an External switch.

            :raises: SemanticError
        """
        if name is None or len(name) == 0:
            raise SemanticError("HypervSwitchSpec requires a 'name'.")

        if switch_type not in _SUPPORTED_SWITCH_TYPES:
            err_msg_lines = ["HypervSwitchSpec 'switch_type' is invalid."]
            err_msg_lines.append("SUPPORTED: {}".format(
                ", ".join(_SUPPORTED_SWITCH_TYPES)
            ))
            err_msg_lines.append("ACTUAL: {!r}".format(switch_type))
            err_msg = os.linesep.join(err_msg_lines)
            raise SemanticError(err_msg)

        if switch_type == "External":
            if net_adapter_name is None or len(net_adapter_name) == 0:
                raise SemanticError(
                    "HypervSwitchSpec of type External requires a "
                    "'net_adapter_name'."
                )

        self.name: str = name
        self.switch_type: str = switch_type
        self.net_adapter_name: Optional[str] = net_adapter_name
        self.allow_management_os: bool = allow_management_os
        return
