"""
    Example-based tests for the HypervClient API groups using a mock
    ICommandRunner.
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import json

import pytest

from automojo.errors.exceptions import ConfigurationError

from automojo.interop.hyperv.hypervclient import HypervClient
from automojo.interop.hyperv.hypervwinrmcredential import (
    HypervWinrmCredential
)
from automojo.interop.hyperv.exceptions.hypervcmdleterror import (
    HypervCmdletError
)
from automojo.interop.hyperv.specs.hypervswitchspec import HypervSwitchSpec
from automojo.interop.hyperv.specs.hypervvhdxspec import HypervVhdxSpec
from automojo.interop.hyperv.specs.hypervvmcreatespec import (
    HypervVmCreateSpec
)

from automojo.tests.interop.hyperv.mockcommandrunner import MockCommandRunner


def _credential() -> HypervWinrmCredential:
    rtnval = HypervWinrmCredential(
        endpoint="hv-host.local", username="Administrator",
        password="p@ss", transport="winrm",
    )
    return rtnval


def test_construct_requires_hyperv_credential():
    runner = MockCommandRunner()
    with pytest.raises(ConfigurationError):
        HypervClient(runner=runner, credential=object())
    return


def test_credential_rejects_missing_auth_material():
    with pytest.raises(ConfigurationError):
        HypervWinrmCredential(endpoint="h", username="u")
    return


def test_host_info_parses_json():
    runner = MockCommandRunner()
    host_record = {
        "ComputerName": "HV01", "LogicalProcessorCount": 16,
        "MemoryCapacity": 137438953472,
        "VirtualMachinePath": "C:\\VMs",
        "VirtualHardDiskPath": "C:\\VHDs",
    }
    runner.seed(contains="Get-VMHost",
                stdout=json.dumps(host_record))
    client = HypervClient(runner=runner, credential=_credential())
    info = client.host.host_info()
    assert info.computer_name == "HV01"
    assert info.logical_processor_count == 16
    return


def test_new_switch_is_idempotent_when_present():
    runner = MockCommandRunner()
    switch_record = {"Name": "ext-sw", "SwitchType": "External",
                     "Id": "sw-1"}
    runner.seed(contains="Get-VMSwitch",
                stdout=json.dumps(switch_record))
    runner.seed(contains="New-VMSwitch", stdout="{}", exit_code=1,
                stderr="should not be called")
    client = HypervClient(runner=runner, credential=_credential())
    spec = HypervSwitchSpec(name="ext-sw", switch_type="External",
                            net_adapter_name="Ethernet")
    switch = client.switches.new_switch(spec=spec)
    assert switch.name == "ext-sw"
    # New-VMSwitch must not have been dispatched.
    new_calls = [c for c in runner.invocations if "New-VMSwitch" in c]
    assert len(new_calls) == 0
    return


def test_new_switch_creates_when_absent():
    runner = MockCommandRunner()
    created = {"Name": "ext-sw", "SwitchType": "External", "Id": "sw-9"}
    runner.seed(contains="Get-VMSwitch", stdout="")
    runner.seed(contains="New-VMSwitch", stdout=json.dumps(created))
    client = HypervClient(runner=runner, credential=_credential())
    spec = HypervSwitchSpec(name="ext-sw", switch_type="External",
                            net_adapter_name="Ethernet")
    switch = client.switches.new_switch(spec=spec)
    assert switch.switch_id == "sw-9"
    return


def test_remove_switch_absent_is_noop():
    runner = MockCommandRunner()
    runner.seed(contains="Get-VMSwitch", stdout="")
    client = HypervClient(runner=runner, credential=_credential())
    client.switches.remove_switch(name="ghost")
    remove_calls = [c for c in runner.invocations if "Remove-VMSwitch" in c]
    assert len(remove_calls) == 0
    return


def test_new_vhdx_idempotent_on_matching_size():
    runner = MockCommandRunner()
    existing = {"Path": "C:\\d.vhdx", "Size": 1024, "VhdType": "Dynamic"}
    runner.seed(contains="Get-VHD", stdout=json.dumps(existing))
    runner.seed(contains="New-VHD", stdout="{}", exit_code=1)
    client = HypervClient(runner=runner, credential=_credential())
    spec = HypervVhdxSpec(path="C:\\d.vhdx", size_bytes=1024,
                          dynamic=True)
    info = client.vhdx.new_vhdx(spec=spec)
    assert info.size_bytes == 1024
    new_calls = [c for c in runner.invocations if "New-VHD" in c]
    assert len(new_calls) == 0
    return


def test_new_vm_idempotent_when_present():
    runner = MockCommandRunner()
    vm_record = {"Name": "vm01", "Id": "vm-1", "State": "Off",
                 "Generation": 2, "ProcessorCount": 2,
                 "MemoryStartup": 2147483648, "Notes": ""}
    runner.seed(contains="Get-VM -Name 'vm01'",
                stdout=json.dumps(vm_record))
    runner.seed(contains="New-VM", stdout="{}", exit_code=1)
    client = HypervClient(runner=runner, credential=_credential())
    spec = HypervVmCreateSpec(name="vm01",
                              memory_startup_bytes=2147483648)
    vm = client.vms.new_vm(spec=spec)
    assert vm.name == "vm01"
    new_calls = [c for c in runner.invocations
                 if c.startswith("New-VM")]
    assert len(new_calls) == 0
    return


def test_set_vm_processor_noop_when_already_matching():
    runner = MockCommandRunner()
    vm_record = {"Name": "vm01", "Id": "vm-1", "State": "Off",
                 "Generation": 2, "ProcessorCount": 4,
                 "MemoryStartup": 2147483648, "Notes": ""}
    runner.seed(contains="Get-VM -Name 'vm01'",
                stdout=json.dumps(vm_record))
    client = HypervClient(runner=runner, credential=_credential())
    client.hardware.set_vm_processor(name="vm01", count=4)
    set_calls = [c for c in runner.invocations
                 if "Set-VMProcessor" in c]
    assert len(set_calls) == 0
    return


def test_set_vm_processor_dispatches_when_drifted():
    runner = MockCommandRunner()
    vm_record = {"Name": "vm01", "Id": "vm-1", "State": "Off",
                 "Generation": 2, "ProcessorCount": 2,
                 "MemoryStartup": 2147483648, "Notes": ""}
    runner.seed(contains="Get-VM -Name 'vm01'",
                stdout=json.dumps(vm_record))
    runner.seed(contains="Set-VMProcessor", stdout="")
    client = HypervClient(runner=runner, credential=_credential())
    client.hardware.set_vm_processor(name="vm01", count=8)
    set_calls = [c for c in runner.invocations
                 if "Set-VMProcessor" in c]
    assert len(set_calls) == 1
    assert "-Count 8" in set_calls[0]
    return


def test_cmdlet_error_reclassification_on_nonzero_exit():
    runner = MockCommandRunner()
    runner.seed(contains="Get-VMHost", stdout="",
                stderr="Access denied", exit_code=1)
    client = HypervClient(runner=runner, credential=_credential())
    with pytest.raises(HypervCmdletError) as excinfo:
        client.host.host_info()
    assert excinfo.value.exit_code == 1
    assert "Access denied" in str(excinfo.value)
    return


def test_cmdlet_error_on_timeout():
    runner = MockCommandRunner()
    runner.seed(contains="Get-VMHost", stdout="", timed_out=True)
    client = HypervClient(runner=runner, credential=_credential())
    with pytest.raises(HypervCmdletError):
        client.host.host_info()
    return
