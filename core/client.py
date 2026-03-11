import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class SarvamClient:
    """Async HTTP client for Sarvam app-authoring API."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60)
        self.token: str | None = None

    async def login(self, org_id: str, user_id: str, password: str) -> None:
        response = await self.client.post(
            f"{self.base_url}/api/auth/login",
            json={
                "org_id": org_id,
                "user_id": user_id,
                "password": password,
            },
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]
        self.client.headers.update({"Authorization": f"Bearer {self.token}"})

    def _spr_url(self, org_id: str, workspace_id: str, app_id: str, user_identifier: str) -> str:
        return (
            f"{self.base_url}/api/app-authoring/orgs/{org_id}/workspaces/"
            f"{workspace_id}/apps/{app_id}/users/{user_identifier}/spr"
        )

    async def get_spr(
        self,
        org_id: str,
        workspace_id: str,
        app_id: str,
        user_identifier: str,
    ) -> tuple[str, Any]:
        """Fetch SPR for a single user. Returns (identifier, data_or_error)."""
        endpoint = self._spr_url(org_id, workspace_id, app_id, user_identifier)
        try:
            response = await self.client.get(endpoint)
            if response.status_code == 200:
                return user_identifier, response.json()
            return user_identifier, f"Error: HTTP {response.status_code} - {response.text}"
        except Exception as e:
            logger.error(f"Error getting SPR for {user_identifier}: {e}")
            return user_identifier, f"Error: {str(e)}"

    async def update_spr(
        self,
        org_id: str,
        workspace_id: str,
        app_id: str,
        user_identifier: str,
        payload: dict,
    ) -> tuple[str, str]:
        """Update SPR for a single user. Returns (identifier, status_message)."""
        endpoint = self._spr_url(org_id, workspace_id, app_id, user_identifier)
        try:
            response = await self.client.put(endpoint, json=payload)
            if response.status_code == 200:
                return user_identifier, "Success"
            return user_identifier, f"Error: HTTP {response.status_code} - {response.text}"
        except Exception as e:
            logger.error(f"Error updating {user_identifier}: {e}")
            return user_identifier, f"Error: {str(e)}"

    async def close(self) -> None:
        await self.client.aclose()
