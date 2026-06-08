"""
    .. module:: hypervtaskhandle
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`HypervTaskHandle` which
                   implements :class:`ITaskHandle` over a background
                   PowerShell job.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import os
import time

from ccai.aspects.aspects import Aspects
from ccai.interfaces.itaskhandle import TaskResult, TaskState

from ccai.interop.hyperv.aspectshyperv import AspectsRunner


class HypervTaskHandle:
    """
        Synchronous-poll handle over a background PowerShell job.

        Implements the :class:`ITaskHandle` protocol.  The poll loop calls
        ``Get-Job <id>`` via the owning :class:`JobsGroup` per the
        completion interval and distinguishes "timed out waiting"
        (raises :class:`TimeoutError`) from "task finished but failed"
        (returns a terminal :class:`TaskResult`).
    """

    def __init__(self, *, job_id: str, jobs_group: object) -> None:
        """
            Initialise a HypervTaskHandle.

            :param job_id: The PowerShell job identifier.
            :param jobs_group: The JobsGroup used to poll ``Get-Job``.
        """
        self._job_id: str = job_id
        self._jobs_group: object = jobs_group
        self._last_state: TaskState = TaskState.PENDING
        return

    def wait(self, *, aspects: Aspects) -> TaskResult:
        """
            Block until the job reaches a terminal state.

            :param aspects: Behaviour control; the poll loop is driven
                from ``completion_interval`` / ``completion_timeout``.

            :returns: A terminal TaskResult.
            :raises: TimeoutError
        """
        if isinstance(aspects, AspectsRunner):
            poll_aspects = aspects
        else:
            poll_aspects = AspectsRunner(
                completion_interval=aspects.completion_interval,
                completion_timeout=aspects.completion_timeout,
                connection_timeout=aspects.connection_timeout,
            )

        deadline = time.monotonic() + aspects.completion_timeout

        while True:
            job_info = self._jobs_group.get(job_id=self._job_id,
                                            aspects=poll_aspects)
            self._last_state = job_info.task_state

            if job_info.is_terminal is True:
                rtnval = TaskResult(task_id=self._job_id,
                                    state=job_info.task_state,
                                    progress=job_info.progress,
                                    error=job_info.error)
                return rtnval

            now = time.monotonic()
            if now >= deadline:
                err_msg_lines = ["Timed out waiting for Hyper-V job."]
                err_msg_lines.append("JOB-ID: {}".format(self._job_id))
                err_msg_lines.append("TIMEOUT: {}".format(
                    aspects.completion_timeout
                ))
                err_msg_lines.append("LAST-STATE: {}".format(
                    job_info.state
                ))
                err_msg = os.linesep.join(err_msg_lines)
                raise TimeoutError(err_msg)

            time.sleep(aspects.completion_interval)

    def cancel(self, *, aspects: Aspects) -> None:
        """
            Request cancellation of the in-flight job.

            :param aspects: Behaviour control for the call.

            :raises: NotImplementedError
        """
        raise NotImplementedError(
            "HypervTaskHandle.cancel is not supported; stop the job on the "
            "host with Stop-Job if cancellation is required."
        )

    def is_done(self) -> bool:
        """
            Report whether the last observed state is terminal.

            :returns: True when the last observed state is terminal.
        """
        terminal_states = (TaskState.SUCCEEDED, TaskState.FAILED,
                           TaskState.CANCELLED)
        rtnval = self._last_state in terminal_states
        return rtnval

    def task_id(self) -> str:
        """
            Return the PowerShell job identifier.

            :returns: The job id string.
        """
        rtnval = self._job_id
        return rtnval


__all__ = ["HypervTaskHandle"]
