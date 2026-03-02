"""ENGIE Belgium API client implementing OAuth2/PKCE with MFA (SMS or email)."""

from __future__ import annotations

import asyncio
import hashlib
import os
import re
import socket
from base64 import urlsafe_b64encode
from dataclasses import dataclass
from typing import Any

import aiohttp

from .const import (
    API_BASE_URL,
    AUTH_BASE_URL,
    LOGGER,
    MFA_METHOD_SMS,
    OAUTH_AUDIENCE,
    OAUTH_SCOPES,
    PREMISES_BASE_URL,
    REDIRECT_URI,
    USER_AGENT_BROWSER,
    USER_AGENT_NATIVE,
)

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class EngieBeApiClientError(Exception):
    """Base exception for ENGIE Belgium API client errors."""


class EngieBeApiClientCommunicationError(EngieBeApiClientError):
    """Exception for communication errors (timeout, network)."""


class EngieBeApiClientAuthenticationError(EngieBeApiClientError):
    """Exception for authentication errors (bad credentials, expired token)."""


class EngieBeApiClientMfaError(EngieBeApiClientError):
    """Exception for MFA-related errors (invalid code)."""


# ---------------------------------------------------------------------------
# Auth flow intermediate state
# ---------------------------------------------------------------------------


@dataclass
class AuthFlowState:
    """Intermediate state kept between config-flow steps."""

    session: aiohttp.ClientSession
    authorize_state: str
    login_state: str
    mfa_challenge_state: str
    code_verifier: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BROWSER_HEADERS: dict[str, str] = {
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8,"
        "application/signed-exchange;v=b3;q=0.7"
    ),
    "User-Agent": USER_AGENT_BROWSER,
    "sec-ch-ua": ('"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"'),
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
}


def _base64url(data: bytes) -> str:
    """Encode bytes to a Base64-URL string (no padding)."""
    return urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _generate_pkce() -> tuple[str, str, str, str]:
    """
    Generate PKCE parameters.

    Returns (state, nonce, code_verifier, code_challenge).
    """
    state = os.urandom(16).hex()
    nonce = os.urandom(16).hex()
    code_verifier = _base64url(os.urandom(32))
    code_challenge = _base64url(hashlib.sha256(code_verifier.encode("ascii")).digest())
    return state, nonce, code_verifier, code_challenge


def _extract_from_body(body: str, pattern: str) -> str | None:
    """Extract a value from an HTML body using a regex pattern."""
    match = re.search(pattern, body)
    return match.group(1) if match else None


# ---------------------------------------------------------------------------
# API Client
# ---------------------------------------------------------------------------


class EngieBeApiClient:
    """
    ENGIE Belgium API client.

    Handles the full OAuth2/PKCE + MFA authentication flow (SMS or email)
    and subsequent token refresh / data retrieval.
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        client_id: str,
        access_token: str | None = None,
        refresh_token: str | None = None,
    ) -> None:
        """Initialise the client."""
        self._session = session
        self._client_id = client_id
        self.access_token = access_token
        self.refresh_token = refresh_token

    # ------------------------------------------------------------------
    # Phase 1: start authentication (config-flow step 1 triggers this)
    # Runs auth steps 1-7, returns intermediate state so the config flow
    # can ask the user for the MFA code.
    # ------------------------------------------------------------------

    async def async_start_authentication(
        self,
        username: str,
        password: str,
        mfa_method: str = MFA_METHOD_SMS,
    ) -> AuthFlowState:
        """
        Execute auth steps 1-7 and return intermediate state.

        When *mfa_method* is ``sms`` (default) step 7 triggers an SMS.
        When it is ``email`` the ALT authenticator-switching detour runs
        instead (no SMS is sent).  The caller must then collect the code
        and pass it to ``async_complete_authentication``.
        """
        auth_session = aiohttp.ClientSession()
        try:
            return await self._run_auth_steps_1_to_7(
                auth_session, username, password, mfa_method
            )
        except Exception:
            await auth_session.close()
            raise

    # ------------------------------------------------------------------
    # Phase 2: complete authentication (config-flow step 2 triggers this)
    # Runs auth steps 8-13.
    # ------------------------------------------------------------------

    async def async_complete_authentication(
        self,
        flow_state: AuthFlowState,
        mfa_code: str,
        mfa_method: str = MFA_METHOD_SMS,
    ) -> tuple[str, str]:
        """
        Submit the MFA code and exchange the authorisation code for tokens.

        Returns (access_token, refresh_token).
        The temporary auth session is closed on success or on non-recoverable
        errors.  On ``EngieBeApiClientMfaError`` the session is kept open so
        the caller can retry with a corrected code.
        """
        try:
            access_token, refresh_token = await self._run_auth_steps_8_to_13(
                flow_state, mfa_code, mfa_method=mfa_method
            )
        except EngieBeApiClientMfaError:
            # Keep session open — user can retry with a new code
            raise
        except BaseException:
            await flow_state.session.close()
            raise
        else:
            await flow_state.session.close()
            self.access_token = access_token
            self.refresh_token = refresh_token
            return access_token, refresh_token

    # ------------------------------------------------------------------
    # Token refresh  (runs on a 60-second timer after setup)
    # ------------------------------------------------------------------

    async def async_refresh_token(self) -> tuple[str, str]:
        """
        Refresh the access token using the refresh token.

        Returns (new_access_token, new_refresh_token).
        The refresh token is rotated on every call.
        """
        if not self.refresh_token:
            msg = "No refresh token available"
            raise EngieBeApiClientAuthenticationError(msg)

        data = {
            "refresh_token": self.refresh_token,
            "audience": OAUTH_AUDIENCE,
            "grant_type": "refresh_token",
            "scope": OAUTH_SCOPES,
            "redirect_uri": REDIRECT_URI,
            "client_id": self._client_id,
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": USER_AGENT_NATIVE,
        }

        result = await self._api_wrapper(
            session=self._session,
            method="POST",
            url=f"{AUTH_BASE_URL}/oauth/token",
            data=data,
            headers=headers,
            json_response=True,
        )

        self.access_token = result["access_token"]
        self.refresh_token = result["refresh_token"]
        return self.access_token, self.refresh_token

    # ------------------------------------------------------------------
    # Data retrieval
    # ------------------------------------------------------------------

    async def async_get_prices(self, customer_number: str) -> Any:
        """
        Fetch energy prices for a customer.

        Returns the parsed JSON response.
        """
        url = (
            f"{API_BASE_URL}/business-agreements/"
            f"{customer_number}/supplier-energy-prices"
        )
        headers = {
            "User-Agent": USER_AGENT_BROWSER,
            "Accept": "application/json, application/problem+json",
            "authorization": f"Bearer {self.access_token}",
        }
        return await self._api_wrapper(
            session=self._session,
            method="GET",
            url=url,
            headers=headers,
            params={"maxGranularity": "MONTHLY"},
            json_response=True,
        )

    async def async_get_service_point(self, ean: str) -> dict[str, Any]:
        """
        Fetch service-point metadata for a single EAN.

        Returns the parsed JSON response which includes a ``division``
        field (``"ELECTRICITY"`` or ``"GAS"``).
        """
        url = f"{PREMISES_BASE_URL}/service-points/{ean}"
        headers = {
            "User-Agent": USER_AGENT_BROWSER,
            "Accept": "application/json, application/problem+json",
            "authorization": f"Bearer {self.access_token}",
        }
        return await self._api_wrapper(
            session=self._session,
            method="GET",
            url=url,
            headers=headers,
            json_response=True,
        )

    # ------------------------------------------------------------------
    # Internal: auth flow step implementations
    # ------------------------------------------------------------------

    async def _run_auth_steps_1_to_7(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
        mfa_method: str,
    ) -> AuthFlowState:
        """
        Run auth steps 1-7 (authorize -> MFA triggered).

        When *mfa_method* is ``sms``, step 7 fires an SMS.  When it is
        ``email``, step 7 is skipped and the ALT authenticator-switching
        detour runs instead so the user receives an email code.
        """
        state, nonce, code_verifier, code_challenge = _generate_pkce()

        # Step 1: GET /authorize
        authorize_params = {
            "redirect_uri": REDIRECT_URI,
            "client_id": self._client_id,
            "response_type": "code",
            "ui_locales": "nl",
            "state": state,
            "nonce": nonce,
            "scope": OAUTH_SCOPES,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "audience": OAUTH_AUDIENCE,
            "app_scheme": "be-engie-smart",
            "cancel_redirect": "be-engie-smart://cancel-registration-redirect",
        }
        body = await self._api_wrapper(
            session=session,
            method="GET",
            url=f"{AUTH_BASE_URL}/authorize",
            params=authorize_params,
            headers=_BROWSER_HEADERS,
            allow_redirects=False,
        )
        authorize_state = _extract_from_body(body, r"state=([a-zA-Z0-9_-]+)")
        if not authorize_state:
            msg = "Failed to extract authorize state from response"
            raise EngieBeApiClientAuthenticationError(msg)

        LOGGER.debug("Auth step 1 complete: got authorizeState")

        # Step 2: GET /u/login/identifier (load login page)
        await self._api_wrapper(
            session=session,
            method="GET",
            url=f"{AUTH_BASE_URL}/u/login/identifier",
            params={"state": authorize_state, "ui_locales": "nl"},
            headers=_BROWSER_HEADERS,
            allow_redirects=False,
        )
        LOGGER.debug("Auth step 2 complete: loaded login page")

        # Step 3: POST /u/login/identifier (submit username)
        await self._api_wrapper(
            session=session,
            method="POST",
            url=f"{AUTH_BASE_URL}/u/login/identifier",
            params={"state": authorize_state, "ui_locales": "nl"},
            headers=_BROWSER_HEADERS,
            data={
                "state": authorize_state,
                "allow-passkeys": "true",
                "username": username,
                "js-available": "true",
                "webauthn-available": "true",
                "is-brave": "false",
                "webauthn-platform-available": "true",
                "ulp-remember-me-present": "true",
                "ulp-remember-me": "on",
            },
            allow_redirects=False,
        )
        LOGGER.debug("Auth step 3 complete: submitted username")

        # Step 4: GET /u/login/password (load password page)
        await self._api_wrapper(
            session=session,
            method="GET",
            url=f"{AUTH_BASE_URL}/u/login/password",
            params={"state": authorize_state, "ui_locales": "nl"},
            headers=_BROWSER_HEADERS,
            allow_redirects=False,
        )
        LOGGER.debug("Auth step 4 complete: loaded password page")

        # Step 5: POST /u/login/password (submit credentials)
        body = await self._api_wrapper(
            session=session,
            method="POST",
            url=f"{AUTH_BASE_URL}/u/login/password",
            params={"state": authorize_state, "ui_locales": "nl"},
            headers=_BROWSER_HEADERS,
            data={
                "state": authorize_state,
                "username": username,
                "password": password,
                "js-available": "true",
                "webauthn-available": "true",
                "is-brave": "false",
                "webauthn-platform-available": "true",
            },
            allow_redirects=False,
        )
        login_state = _extract_from_body(body, r"state=([a-zA-Z0-9_-]+)")
        if not login_state:
            msg = "Login failed: could not extract login state (bad credentials?)"
            raise EngieBeApiClientAuthenticationError(msg)

        LOGGER.debug("Auth step 5 complete: got loginState")

        # Step 6: GET /authorize/resume (triggers MFA)
        body = await self._api_wrapper(
            session=session,
            method="GET",
            url=f"{AUTH_BASE_URL}/authorize/resume",
            params={"state": login_state},
            headers=_BROWSER_HEADERS,
            allow_redirects=False,
        )
        mfa_challenge_state = _extract_from_body(body, r"state=([a-zA-Z0-9_-]+)")
        if not mfa_challenge_state:
            msg = "Failed to extract MFA challenge state"
            raise EngieBeApiClientAuthenticationError(msg)

        LOGGER.debug("Auth step 6 complete: got mfaChallengeState")

        if mfa_method == MFA_METHOD_SMS:
            # Step 7: GET /u/mfa-sms-challenge (triggers SMS send)
            await self._api_wrapper(
                session=session,
                method="GET",
                url=f"{AUTH_BASE_URL}/u/mfa-sms-challenge",
                params={"state": mfa_challenge_state, "ui_locales": "nl"},
                headers=_BROWSER_HEADERS,
                allow_redirects=False,
            )
            LOGGER.debug("Auth step 7 complete: SMS sent to user")
        else:
            # Email MFA: run ALT steps 1-4 to switch authenticator and
            # trigger the email send (skips step 7 entirely so no SMS
            # is sent).
            await self._switch_to_email_mfa(session, mfa_challenge_state)

        return AuthFlowState(
            session=session,
            authorize_state=authorize_state,
            login_state=login_state,
            mfa_challenge_state=mfa_challenge_state,
            code_verifier=code_verifier,
        )

    async def _run_auth_steps_8_to_13(
        self,
        flow_state: AuthFlowState,
        mfa_code: str,
        *,
        mfa_method: str = MFA_METHOD_SMS,
    ) -> tuple[str, str]:
        """Run auth steps 8-13 (submit MFA -> get tokens)."""
        session = flow_state.session

        if mfa_method == MFA_METHOD_SMS:
            body = await self._submit_sms_mfa(flow_state, mfa_code)
        else:
            body = await self._submit_email_mfa(flow_state, mfa_code)

        # The response should contain a new state; if it doesn't the
        # code was most likely wrong (server returned 400 with the MFA
        # form again).
        another_state = _extract_from_body(body, r"state=([a-zA-Z0-9_-]+)")
        if not another_state:
            msg = "Invalid MFA code or failed to proceed after MFA submission"
            raise EngieBeApiClientMfaError(msg)

        LOGGER.debug("Auth step 8 complete: MFA code accepted")

        # Step 9: GET /authorize/resume (post-MFA)
        body = await self._api_wrapper(
            session=session,
            method="GET",
            url=f"{AUTH_BASE_URL}/authorize/resume",
            params={"state": flow_state.login_state},
            headers=_BROWSER_HEADERS,
            allow_redirects=False,
        )
        passkey_state = _extract_from_body(body, r"state=([a-zA-Z0-9_-]+)")
        if not passkey_state:
            msg = "Failed to extract passkey enrollment state"
            raise EngieBeApiClientAuthenticationError(msg)

        LOGGER.debug("Auth step 9 complete: got passKeyState")

        # Step 10: GET /u/passkey-enrollment (load passkey page)
        await self._api_wrapper(
            session=session,
            method="GET",
            url=f"{AUTH_BASE_URL}/u/passkey-enrollment",
            params={"state": passkey_state, "ui_locales": "nl"},
            headers=_BROWSER_HEADERS,
            allow_redirects=False,
        )
        LOGGER.debug("Auth step 10 complete: loaded passkey page")

        # Step 11: POST /u/passkey-enrollment (abort enrollment)
        # The Auth0 flow uses followRedirects=true, but the redirect chain
        # ends at a non-HTTP app-scheme URL that aiohttp cannot follow.
        # We skip following redirects here since the code is extracted in
        # step 12.
        await self._api_wrapper(
            session=session,
            method="POST",
            url=f"{AUTH_BASE_URL}/u/passkey-enrollment",
            params={"state": passkey_state, "ui_locales": "nl"},
            headers=_BROWSER_HEADERS,
            data={
                "state": passkey_state,
                "action": "abort-passkey-enrollment",
            },
            allow_redirects=False,
        )
        LOGGER.debug("Auth step 11 complete: passkey enrollment aborted")

        # Step 12: GET /authorize/resume (final — extract auth code)
        # Uses loginState (not passKeyState), exactly as in the API
        # auth flow.  The response body contains the authorization code.
        body = await self._api_wrapper(
            session=session,
            method="GET",
            url=f"{AUTH_BASE_URL}/authorize/resume",
            params={"state": flow_state.login_state},
            headers=_BROWSER_HEADERS,
            allow_redirects=False,
        )
        auth_code = _extract_from_body(body, r"code=([a-zA-Z0-9_-]+)")
        if not auth_code:
            msg = "Failed to extract authorization code"
            raise EngieBeApiClientAuthenticationError(msg)

        LOGGER.debug("Auth step 12 complete: got authorization code")

        # Step 13: POST /oauth/token (exchange code for tokens)
        token_result = await self._api_wrapper(
            session=session,
            method="POST",
            url=f"{AUTH_BASE_URL}/oauth/token",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": USER_AGENT_NATIVE,
            },
            data={
                "code": auth_code,
                "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI,
                "code_verifier": flow_state.code_verifier,
                "client_id": self._client_id,
            },
            json_response=True,
            allow_redirects=False,
        )

        access_token: str = token_result["access_token"]
        refresh_token: str = token_result["refresh_token"]

        LOGGER.debug("Auth step 13 complete: tokens obtained")
        return access_token, refresh_token

    # ------------------------------------------------------------------
    # Internal: MFA submission methods (SMS vs email)
    # ------------------------------------------------------------------

    async def _submit_sms_mfa(
        self,
        flow_state: AuthFlowState,
        mfa_code: str,
    ) -> str:
        """Submit an SMS MFA code (auth step 8)."""
        # Step 8: POST /u/mfa-sms-challenge (submit SMS code)
        # A wrong code returns HTTP 400; we suppress the automatic error
        # handling so we can raise a specific MfaError instead.
        return await self._api_wrapper(
            session=flow_state.session,
            method="POST",
            url=f"{AUTH_BASE_URL}/u/mfa-sms-challenge",
            params={
                "state": flow_state.mfa_challenge_state,
                "ui_locales": "nl",
            },
            headers=_BROWSER_HEADERS,
            data={
                "state": flow_state.mfa_challenge_state,
                "code": mfa_code,
            },
            allow_redirects=False,
            raise_on_error=False,
        )

    async def _submit_email_mfa(
        self,
        flow_state: AuthFlowState,
        mfa_code: str,
    ) -> str:
        """
        Submit an email MFA code (auth step 8.ALT-5).

        The authenticator switch (ALT steps 1-4) has already been
        performed during ``_run_auth_steps_1_to_7`` so only the code
        POST is needed here.
        """
        return await self._api_wrapper(
            session=flow_state.session,
            method="POST",
            url=f"{AUTH_BASE_URL}/u/mfa-email-challenge",
            params={
                "state": flow_state.mfa_challenge_state,
                "ui_locales": "nl",
            },
            headers=_BROWSER_HEADERS,
            data={
                "state": flow_state.mfa_challenge_state,
                "code": mfa_code,
                "action": "default",
            },
            allow_redirects=False,
            raise_on_error=False,
        )

    # ------------------------------------------------------------------
    # Internal: email MFA authenticator switch (ALT steps 1-4)
    # ------------------------------------------------------------------

    async def _switch_to_email_mfa(
        self,
        session: aiohttp.ClientSession,
        challenge_state: str,
    ) -> None:
        """
        Run the authenticator-switching detour (auth ALT steps 1-4).

        This is called from ``_run_auth_steps_1_to_7`` when the user
        chose email MFA instead of SMS.  It navigates the Auth0 UI from
        the SMS challenge screen to the email challenge screen, which
        triggers the email send.
        """
        # ALT-1: POST /u/mfa-sms-challenge with action=pick-authenticator
        await self._api_wrapper(
            session=session,
            method="POST",
            url=f"{AUTH_BASE_URL}/u/mfa-sms-challenge",
            params={"state": challenge_state, "ui_locales": "nl"},
            headers=_BROWSER_HEADERS,
            data={
                "state": challenge_state,
                "action": "pick-authenticator",
            },
            allow_redirects=False,
        )
        LOGGER.debug("Auth ALT-1 complete: picked authenticator")

        # ALT-2: GET /u/mfa-login-options (load MFA method selection)
        await self._api_wrapper(
            session=session,
            method="GET",
            url=f"{AUTH_BASE_URL}/u/mfa-login-options",
            params={"state": challenge_state, "ui_locales": "nl"},
            headers=_BROWSER_HEADERS,
            allow_redirects=False,
        )
        LOGGER.debug("Auth ALT-2 complete: loaded login options")

        # ALT-3: POST /u/mfa-login-options with action=email::1
        await self._api_wrapper(
            session=session,
            method="POST",
            url=f"{AUTH_BASE_URL}/u/mfa-login-options",
            params={"state": challenge_state, "ui_locales": "nl"},
            headers=_BROWSER_HEADERS,
            data={
                "state": challenge_state,
                "action": "email::1",
            },
            allow_redirects=False,
        )
        LOGGER.debug("Auth ALT-3 complete: selected email MFA")

        # ALT-4: GET /u/mfa-email-challenge (triggers email send)
        await self._api_wrapper(
            session=session,
            method="GET",
            url=f"{AUTH_BASE_URL}/u/mfa-email-challenge",
            params={"state": challenge_state, "ui_locales": "nl"},
            headers=_BROWSER_HEADERS,
            allow_redirects=False,
        )
        LOGGER.debug("Auth ALT-4 complete: email challenge triggered")

    # ------------------------------------------------------------------
    # Generic request wrapper
    # ------------------------------------------------------------------

    async def _api_wrapper(  # noqa: PLR0913
        self,
        *,
        session: aiohttp.ClientSession,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        data: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        json_response: bool = False,
        allow_redirects: bool = False,
        raise_on_error: bool = True,
    ) -> Any:
        """
        Execute an HTTP request with error handling.

        When *raise_on_error* is ``False`` the caller is responsible for
        interpreting non-success status codes (useful when a 400 has
        semantic meaning, e.g. an invalid MFA code).
        """
        try:
            async with asyncio.timeout(30):
                response = await session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                    params=params,
                    allow_redirects=allow_redirects,
                )
                if raise_on_error:
                    if response.status in (401, 403):
                        msg = f"Authentication failed ({response.status})"
                        raise EngieBeApiClientAuthenticationError(msg)  # noqa: TRY301

                    # For auth-flow HTML pages, non-200/302 is likely an
                    # error but we don't raise_for_status on 3xx since we
                    # handle redirects manually.
                    if response.status >= 400:  # noqa: PLR2004
                        response.raise_for_status()

                if json_response:
                    return await response.json()
                return await response.text()

        except EngieBeApiClientError:
            raise
        except TimeoutError as exception:
            msg = f"Timeout communicating with Engie API - {exception}"
            raise EngieBeApiClientCommunicationError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error communicating with Engie API - {exception}"
            raise EngieBeApiClientCommunicationError(msg) from exception
        except Exception as exception:
            msg = f"Unexpected error communicating with Engie API - {exception}"
            raise EngieBeApiClientError(msg) from exception
