import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://apps.sarvam.ai"

ENVIRONMENTS = {
    "UAT": {
        "org_id": "sbilife.co.in",
        "workspace_id": "sbilife-co-in-defa-3cafa6",
        "app_id": "Renewals-UA-108154e9-c4a6",
    },
    "Production": {
        "org_id": "sbilife.co.in",
        "workspace_id": "sbilife-co-in-defa-3cafa6",
        "app_id": "wa-ssp-v2-3465d42d-1b70",
    },
}


def _load_credentials() -> dict:
    user_id = os.getenv("SARVAM_USER_ID")
    password = os.getenv("SARVAM_PASSWORD")
    if not user_id or not password:
        raise RuntimeError(
            "Missing credentials. Set SARVAM_USER_ID and SARVAM_PASSWORD in your .env file."
        )
    return {"user_id": user_id, "password": password}


def get_env_config(env_name: str) -> dict:
    """Return the full config for a given environment, including credentials."""
    if env_name not in ENVIRONMENTS:
        raise ValueError(f"Unknown environment: {env_name}")
    return {**ENVIRONMENTS[env_name], **_load_credentials()}
