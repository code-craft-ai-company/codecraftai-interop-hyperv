"""
    .. module:: hypervwinrmcredential
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`HypervWinrmCredential`
                   container describing the WinRM endpoint and authentication
                   material a :class:`HypervClient` uses.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import os

from typing import Optional

from ccai.errors.exceptions import ConfigurationError


_SUPPORTED_TRANSPORTS = ("winrm", "ssh")


class HypervWinrmCredential:
    """
        Container for the WinRM endpoint and authentication material used
        by a :class:`HypervClient`.

        Hyper-V has no REST surface; the credential names the endpoint a
        PowerShell-over-WinRM (or OpenSSH-for-Windows) runner targets, the
        username, and either a password or an NTLM hash.
    """

    def __init__(self, *, endpoint: str, username: str,
                 password: Optional[str] = None,
                 ntlm_hash: Optional[str] = None,
                 transport: str = "winrm") -> None:
        """
            Initialise a HypervWinrmCredential.

            :param endpoint: The WinRM / SSH endpoint of the Hyper-V host.
            :param username: The account used to authenticate.
            :param password: The account password (optional when an NTLM
                hash is supplied instead).
            :param ntlm_hash: An NTLM hash used for pass-the-hash auth
                (optional when a password is supplied instead).
            :param transport: One of ``winrm`` or ``ssh``.

            :raises: ConfigurationError
        """
        if endpoint is None or len(endpoint) == 0:
            raise ConfigurationError(
                "HypervWinrmCredential requires a non-empty 'endpoint'."
            )

        if username is None or len(username) == 0:
            raise ConfigurationError(
                "HypervWinrmCredential requires a non-empty 'username'."
            )

        has_password = password is not None and len(password) > 0
        has_hash = ntlm_hash is not None and len(ntlm_hash) > 0
        if not has_password and not has_hash:
            raise ConfigurationError(
                "HypervWinrmCredential requires either a 'password' or "
                "an 'ntlm_hash' for authentication."
            )

        if transport not in _SUPPORTED_TRANSPORTS:
            err_msg_lines = ["HypervWinrmCredential 'transport' is invalid."]
            err_msg_lines.append("SUPPORTED: {}".format(
                ", ".join(_SUPPORTED_TRANSPORTS)
            ))
            err_msg_lines.append("ACTUAL: {!r}".format(transport))
            err_msg = os.linesep.join(err_msg_lines)
            raise ConfigurationError(err_msg)

        self._endpoint: str = endpoint
        self._username: str = username
        self._password: Optional[str] = password
        self._ntlm_hash: Optional[str] = ntlm_hash
        self._transport: str = transport
        return

    @property
    def endpoint(self) -> str:
        """
            Return the Hyper-V host endpoint.

            :returns: The endpoint string.
        """
        rtnval = self._endpoint
        return rtnval

    @property
    def username(self) -> str:
        """
            Return the authentication username.

            :returns: The username string.
        """
        rtnval = self._username
        return rtnval

    @property
    def password(self) -> Optional[str]:
        """
            Return the authentication password, if any.

            :returns: The password string or None.
        """
        rtnval = self._password
        return rtnval

    @property
    def ntlm_hash(self) -> Optional[str]:
        """
            Return the NTLM hash, if any.

            :returns: The NTLM hash string or None.
        """
        rtnval = self._ntlm_hash
        return rtnval

    @property
    def transport(self) -> str:
        """
            Return the configured transport preference.

            :returns: One of ``winrm`` or ``ssh``.
        """
        rtnval = self._transport
        return rtnval
