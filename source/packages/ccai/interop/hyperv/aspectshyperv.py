"""
    .. module:: aspectshyperv
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`AspectsRunner` behaviour
                   bundle and the :data:`DEFAULT_HYPERV_ASPECTS` singleton
                   consumed by every behaviour-bearing :class:`HypervClient`
                   method.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import os

from typing import Optional

from ccai.aspects.aspects import Aspects


class AspectsRunner(Aspects):
    """
        Aspect bundle for runner-driven Hyper-V operations.

        Extends the minimal contract-layer :class:`Aspects` carrier with
        the parameters a PowerShell-over-WinRM runner needs: whether the
        cmdlet should run with elevation, and how many idempotent retry
        attempts a caller may make while reconciling host state.
    """

    def __init__(self, *,
                 completion_interval: float = 5.0,
                 completion_timeout: float = 600.0,
                 connection_timeout: float = 60.0,
                 max_attempts: int = 1,
                 elevated: bool = True,
                 logger_name: Optional[str] = None) -> None:
        """
            Initialise an AspectsRunner.

            :param completion_interval: Seconds between completion-poll
                iterations for waiter loops.
            :param completion_timeout: Maximum seconds to wait for a
                completion before raising :class:`TimeoutError`.
            :param connection_timeout: Maximum seconds for a single
                runner attempt.
            :param max_attempts: Maximum idempotent retry attempts a
                caller may perform.
            :param elevated: Whether dispatched cmdlets request an
                elevated (Administrator) token from the runner.
            :param logger_name: Optional logger name for routing.
        """
        super().__init__(completion_interval=completion_interval,
                         completion_timeout=completion_timeout,
                         connection_timeout=connection_timeout,
                         max_attempts=max_attempts,
                         logger_name=logger_name)
        object.__setattr__(self, "elevated", elevated)
        object.__setattr__(self, "_frozen", True)
        return

    def __setattr__(self, name: str, value: object) -> None:
        """
            Reject post-construction mutation.

            :class:`AspectsRunner` is an immutable behaviour value object so
            that the shared :data:`DEFAULT_HYPERV_ASPECTS` instance can be
            used as a default parameter without the shared-mutation hazard
            of a mutable default. Construct a new instance to vary
            behaviour.

            :param name: The attribute name.
            :param value: The attribute value.

            :raises: AttributeError
        """
        already_frozen = getattr(self, "_frozen", False)
        if already_frozen is True:
            err_msg_lines = [
                "AspectsRunner is immutable; construct a new instance "
                "to vary behaviour."
            ]
            err_msg_lines.append("ATTRIBUTE: {}".format(name))
            err_msg = os.linesep.join(err_msg_lines)
            raise AttributeError(err_msg)

        object.__setattr__(self, name, value)
        return


DEFAULT_HYPERV_ASPECTS: AspectsRunner = AspectsRunner()


__all__ = ["AspectsRunner", "DEFAULT_HYPERV_ASPECTS"]
