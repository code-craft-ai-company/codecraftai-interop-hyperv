"""
    .. module:: hypervtaskfailederror
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`HypervTaskFailedError`
                   exception type.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Optional


class HypervTaskFailedError(RuntimeError):
    """
        Raised when a background Hyper-V job tracked by a
        :class:`HypervTaskHandle` reaches a failed terminal state and the
        caller asked for an exception rather than a terminal result.
    """

    def __init__(self, message: str, *,
                 job_id: Optional[str] = None,
                 reason: Optional[str] = None) -> None:
        """
            Initialise a HypervTaskFailedError.

            :param message: The summary error message.
            :param job_id: The identifier of the failed job.
            :param reason: The provider-reported failure reason.
        """
        super().__init__(message)
        self.job_id: Optional[str] = job_id
        self.reason: Optional[str] = reason
        return
