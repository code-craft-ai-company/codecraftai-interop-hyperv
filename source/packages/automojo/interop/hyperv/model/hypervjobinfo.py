"""
    .. module:: hypervjobinfo
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`HypervJobInfo` record.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from dataclasses import dataclass
from typing import Any, Dict, Optional

from automojo.interfaces.itaskhandle import TaskState


# Mapping from the PowerShell job state string to the neutral TaskState.
_JOB_STATE_MAP: Dict[str, TaskState] = {
    "notstarted": TaskState.PENDING,
    "running": TaskState.RUNNING,
    "completed": TaskState.SUCCEEDED,
    "failed": TaskState.FAILED,
    "stopped": TaskState.CANCELLED,
    "blocked": TaskState.RUNNING,
    "suspended": TaskState.RUNNING,
}


@dataclass
class HypervJobInfo:
    """
        Typed record describing a background PowerShell job as reported by
        ``Get-Job``.
    """
    job_id: str
    name: str
    state: str
    progress: int
    error: Optional[str]

    @classmethod
    def from_json(cls, record: Dict[str, Any]) -> "HypervJobInfo":
        """
            Build a HypervJobInfo from a ``Get-Job`` JSON record.

            :param record: The parsed JSON object.

            :returns: A HypervJobInfo instance.
        """
        job_id = str(record.get("Id", ""))
        name = str(record.get("Name", ""))
        state = str(record.get("State", ""))
        progress = int(record.get("PercentComplete", 0))
        error = record.get("Error", None)
        normalized_error = str(error) if error is not None else None

        rtnval = cls(job_id=job_id, name=name, state=state,
                     progress=progress, error=normalized_error)
        return rtnval

    @property
    def task_state(self) -> TaskState:
        """
            Map the PowerShell job state onto the neutral TaskState.

            :returns: A TaskState value (RUNNING for unknown states).
        """
        rtnval = _JOB_STATE_MAP.get(self.state.lower(), TaskState.RUNNING)
        return rtnval

    @property
    def is_terminal(self) -> bool:
        """
            Report whether this job has reached a terminal state.

            :returns: True when the mapped state is terminal.
        """
        terminal_states = (TaskState.SUCCEEDED, TaskState.FAILED,
                           TaskState.CANCELLED)
        rtnval = self.task_state in terminal_states
        return rtnval
