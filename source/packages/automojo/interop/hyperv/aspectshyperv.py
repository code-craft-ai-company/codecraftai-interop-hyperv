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
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Optional

from automojo.aspects.aspects import Aspects


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
        self.elevated: bool = elevated
        return


DEFAULT_HYPERV_ASPECTS: AspectsRunner = AspectsRunner()


__all__ = ["AspectsRunner", "DEFAULT_HYPERV_ASPECTS"]
