"""
    .. module:: hypervclient
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`HypervClient`, a typed
                   Python client driving Microsoft Hyper-V through PowerShell
                   cmdlets executed via an :class:`ICommandRunner`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import os

from ccai.errors.exceptions import ConfigurationError
from ccai.interfaces.icommandrunner import ICommandRunner
from ccai.waiting import wait_for_it, WaitContext

from ccai.interop.hyperv.apigroups.adaptersgroup import AdaptersGroup
from ccai.interop.hyperv.apigroups.checkpointsgroup import (
    CheckpointsGroup
)
from ccai.interop.hyperv.apigroups.hardwaregroup import HardwareGroup
from ccai.interop.hyperv.apigroups.hostgroup import HostGroup
from ccai.interop.hyperv.apigroups.jobsgroup import JobsGroup
from ccai.interop.hyperv.apigroups.switchesgroup import SwitchesGroup
from ccai.interop.hyperv.apigroups.vhdxgroup import VhdxGroup
from ccai.interop.hyperv.apigroups.vmsgroup import VmsGroup
from ccai.interop.hyperv.aspectshyperv import (
    AspectsRunner, DEFAULT_HYPERV_ASPECTS
)
from ccai.interop.hyperv.hypervwinrmcredential import (
    HypervWinrmCredential
)
from ccai.interop.hyperv.model.hypervvm import HypervVm
from ccai.interop.hyperv.pwsh.powershelldispatcher import (
    PowershellDispatcher
)


class HypervClient:
    """
        Typed Python client for Microsoft Hyper-V.

        The client drives the ``Hyper-V`` PowerShell module cmdlets
        through an injected :class:`ICommandRunner` — there is no REST
        surface, so :class:`RestClientBase` does not apply.  Operations
        are grouped onto cohesive API-group objects (``host``,
        ``switches``, ``vhdx``, ``vms``, ``hardware``, ``adapters``,
        ``checkpoints``, ``jobs``), and every behaviour-bearing method
        accepts ``aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS``.
    """

    def __init__(self, *, runner: ICommandRunner,
                 credential: HypervWinrmCredential) -> None:
        """
            Initialise a HypervClient.

            :param runner: An ICommandRunner that executes ``pwsh``
                invocations against the Hyper-V host.
            :param credential: The HypervWinrmCredential describing the
                host endpoint and authentication material.

            :raises: ConfigurationError
        """
        if runner is None:
            raise ConfigurationError(
                "HypervClient requires a non-None ICommandRunner."
            )

        if not isinstance(credential, HypervWinrmCredential):
            err_msg_lines = [
                "HypervClient requires a HypervWinrmCredential."
            ]
            err_msg_lines.append("ACTUAL: {}".format(
                type(credential).__name__
            ))
            err_msg = os.linesep.join(err_msg_lines)
            raise ConfigurationError(err_msg)

        self._runner: ICommandRunner = runner
        self._credential: HypervWinrmCredential = credential
        self._dispatcher: PowershellDispatcher = PowershellDispatcher(
            runner=runner
        )

        self._host: HostGroup = HostGroup(dispatcher=self._dispatcher)
        self._switches: SwitchesGroup = SwitchesGroup(
            dispatcher=self._dispatcher
        )
        self._vhdx: VhdxGroup = VhdxGroup(dispatcher=self._dispatcher)
        self._vms: VmsGroup = VmsGroup(dispatcher=self._dispatcher)
        self._hardware: HardwareGroup = HardwareGroup(
            dispatcher=self._dispatcher, vms_group=self._vms
        )
        self._adapters: AdaptersGroup = AdaptersGroup(
            dispatcher=self._dispatcher
        )
        self._checkpoints: CheckpointsGroup = CheckpointsGroup(
            dispatcher=self._dispatcher
        )
        self._jobs: JobsGroup = JobsGroup(dispatcher=self._dispatcher)
        return

    @property
    def credential(self) -> HypervWinrmCredential:
        """
            Return the WinRM credential bound to this client.

            :returns: The HypervWinrmCredential.
        """
        rtnval = self._credential
        return rtnval

    @property
    def host(self) -> HostGroup:
        """
            Return the host-info API group.

            :returns: The HostGroup.
        """
        rtnval = self._host
        return rtnval

    @property
    def switches(self) -> SwitchesGroup:
        """
            Return the virtual-switch API group.

            :returns: The SwitchesGroup.
        """
        rtnval = self._switches
        return rtnval

    @property
    def vhdx(self) -> VhdxGroup:
        """
            Return the VHDX disk API group.

            :returns: The VhdxGroup.
        """
        rtnval = self._vhdx
        return rtnval

    @property
    def vms(self) -> VmsGroup:
        """
            Return the VM lifecycle API group.

            :returns: The VmsGroup.
        """
        rtnval = self._vms
        return rtnval

    @property
    def hardware(self) -> HardwareGroup:
        """
            Return the VM hardware-configuration API group.

            :returns: The HardwareGroup.
        """
        rtnval = self._hardware
        return rtnval

    @property
    def adapters(self) -> AdaptersGroup:
        """
            Return the adapter / disk attach-detach API group.

            :returns: The AdaptersGroup.
        """
        rtnval = self._adapters
        return rtnval

    @property
    def checkpoints(self) -> CheckpointsGroup:
        """
            Return the checkpoint API group.

            :returns: The CheckpointsGroup.
        """
        rtnval = self._checkpoints
        return rtnval

    @property
    def jobs(self) -> JobsGroup:
        """
            Return the background-job API group.

            :returns: The JobsGroup.
        """
        rtnval = self._jobs
        return rtnval

    def wait_for_state(self, *, name: str, desired_state: str,
                       aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS
                       ) -> HypervVm:
        """
            Poll ``Get-VM`` until the VM reaches the desired state.

            :param name: The VM name.
            :param desired_state: The desired ``State`` string
                (e.g. ``Running``, ``Off``).
            :param aspects: AspectsRunner controlling the poll loop.

            :returns: The HypervVm once it reaches the desired state.
            :raises: TimeoutError
        """
        # The poll cadence/timeout is owned by codecraftai-waiting's wait_for_it;
        # the looper returns True once the VM reaches the desired state and raises
        # a descriptive TimeoutError on the final attempt.
        result_box = {"vm": None}

        def state_looper(wctx: WaitContext) -> bool:
            current = self._vms.get_vm(name=name, aspects=aspects)
            result_box["vm"] = current

            if current is not None and current.state.lower() == desired_state.lower():
                return True

            if wctx.final_attempt:
                err_msg_lines = ["Timed out waiting for Hyper-V VM state."]
                err_msg_lines.append("VM: {}".format(name))
                err_msg_lines.append("DESIRED-STATE: {}".format(desired_state))
                if current is not None:
                    err_msg_lines.append("LAST-STATE: {}".format(current.state))
                else:
                    err_msg_lines.append("LAST-STATE: <not found>")
                err_msg_lines.append("TIMEOUT: {}".format(aspects.completion_timeout))
                err_msg = os.linesep.join(err_msg_lines)
                raise TimeoutError(err_msg) from None

            return False

        wait_for_it(
            state_looper,
            what_for="Hyper-V VM '{}' to reach state '{}'".format(name, desired_state),
            interval=aspects.completion_interval,
            timeout=aspects.completion_timeout,
        )

        rtnval = result_box["vm"]
        return rtnval


__all__ = ["HypervClient"]
