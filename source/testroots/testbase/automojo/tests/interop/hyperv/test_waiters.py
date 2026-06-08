"""
    Example-based and property-based tests for the HypervTaskHandle and
    wait_for_state waiters.
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import json

import pytest

from hypothesis import given, settings, strategies as st

from ccai.interfaces.itaskhandle import TaskState

from ccai.interop.hyperv.aspectshyperv import AspectsRunner
from ccai.interop.hyperv.hypervclient import HypervClient
from ccai.interop.hyperv.hypervwinrmcredential import (
    HypervWinrmCredential
)
from ccai.interop.hyperv.model.hypervtaskhandle import HypervTaskHandle

from ccai.tests.interop.hyperv.mockcommandrunner import MockCommandRunner


def _credential() -> HypervWinrmCredential:
    rtnval = HypervWinrmCredential(
        endpoint="hv-host.local", username="Administrator",
        password="p@ss",
    )
    return rtnval


def _fast_aspects() -> AspectsRunner:
    rtnval = AspectsRunner(completion_interval=0.001,
                           completion_timeout=2.0)
    return rtnval


class _StreamJobsGroup:
    """
        Stand-in JobsGroup yielding a scripted sequence of HypervJobInfo.
    """

    def __init__(self, *, states):
        from ccai.interop.hyperv.model.hypervjobinfo import HypervJobInfo
        self._infos = []
        for index, state in enumerate(states):
            record = {"Id": "job-1", "Name": "j",
                      "State": state, "PercentComplete": index}
            self._infos.append(HypervJobInfo.from_json(record))
        self._cursor = 0
        return

    def get(self, *, job_id, aspects):
        if self._cursor < len(self._infos) - 1:
            info = self._infos[self._cursor]
            self._cursor = self._cursor + 1
        else:
            info = self._infos[-1]
        rtnval = info
        return rtnval


def test_task_handle_returns_terminal_success():
    jobs = _StreamJobsGroup(states=["Running", "Running", "Completed"])
    handle = HypervTaskHandle(job_id="job-1", jobs_group=jobs)
    result = handle.wait(aspects=_fast_aspects())
    assert result.state == TaskState.SUCCEEDED
    assert handle.is_done() is True
    return


def test_task_handle_returns_terminal_failure_not_exception():
    jobs = _StreamJobsGroup(states=["Running", "Failed"])
    handle = HypervTaskHandle(job_id="job-1", jobs_group=jobs)
    result = handle.wait(aspects=_fast_aspects())
    assert result.state == TaskState.FAILED
    return


def test_task_handle_times_out_when_never_terminal():
    jobs = _StreamJobsGroup(states=["Running"])
    handle = HypervTaskHandle(job_id="job-1", jobs_group=jobs)
    aspects = AspectsRunner(completion_interval=0.001,
                            completion_timeout=0.05)
    with pytest.raises(TimeoutError):
        handle.wait(aspects=aspects)
    return


_TERMINAL_STATES = ("Completed", "Failed", "Stopped")


@settings(deadline=None, max_examples=40)
@given(running_count=st.integers(min_value=0, max_value=6),
       terminal=st.sampled_from(_TERMINAL_STATES))
def test_task_handle_terminal_correctness(running_count, terminal):
    states = ["Running"] * running_count + [terminal]
    jobs = _StreamJobsGroup(states=states)
    handle = HypervTaskHandle(job_id="job-1", jobs_group=jobs)
    result = handle.wait(aspects=_fast_aspects())
    expected = {
        "Completed": TaskState.SUCCEEDED,
        "Failed": TaskState.FAILED,
        "Stopped": TaskState.CANCELLED,
    }[terminal]
    assert result.state == expected
    return


def test_wait_for_state_reaches_desired():
    runner = MockCommandRunner()
    vm_record = {"Name": "vm01", "Id": "vm-1", "State": "Running",
                 "Generation": 2, "ProcessorCount": 2,
                 "MemoryStartup": 1, "Notes": ""}
    runner.seed(contains="Get-VM -Name 'vm01'",
                stdout=json.dumps(vm_record))
    client = HypervClient(runner=runner, credential=_credential())
    vm = client.wait_for_state(name="vm01", desired_state="Running",
                               aspects=_fast_aspects())
    assert vm.state == "Running"
    return


def test_wait_for_state_times_out():
    runner = MockCommandRunner()
    vm_record = {"Name": "vm01", "Id": "vm-1", "State": "Off",
                 "Generation": 2, "ProcessorCount": 2,
                 "MemoryStartup": 1, "Notes": ""}
    runner.seed(contains="Get-VM -Name 'vm01'",
                stdout=json.dumps(vm_record))
    client = HypervClient(runner=runner, credential=_credential())
    aspects = AspectsRunner(completion_interval=0.001,
                            completion_timeout=0.05)
    with pytest.raises(TimeoutError):
        client.wait_for_state(name="vm01", desired_state="Running",
                              aspects=aspects)
    return
