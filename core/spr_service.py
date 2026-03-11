import asyncio
from asyncio import Semaphore
from typing import Any, Callable

from core.client import SarvamClient
from core.config import BASE_URL, get_env_config

MAX_CONCURRENT = 5


async def _get_spr_with_semaphore(
    client: SarvamClient,
    semaphore: Semaphore,
    org_id: str,
    workspace_id: str,
    app_id: str,
    user_identifier: str,
) -> tuple[str, Any]:
    async with semaphore:
        return await client.get_spr(org_id, workspace_id, app_id, user_identifier)


async def _update_spr_with_semaphore(
    client: SarvamClient,
    semaphore: Semaphore,
    org_id: str,
    workspace_id: str,
    app_id: str,
    user_identifier: str,
    payload: dict,
) -> tuple[str, str]:
    async with semaphore:
        return await client.update_spr(org_id, workspace_id, app_id, user_identifier, payload)


async def _get_multiple(
    env_name: str,
    phone_numbers: list[str],
    progress_callback: Callable[[int, int], None] | None = None,
) -> dict[str, Any]:
    cfg = get_env_config(env_name)
    client = SarvamClient(BASE_URL)
    try:
        await client.login(cfg["org_id"], cfg["user_id"], cfg["password"])
        semaphore = Semaphore(MAX_CONCURRENT)
        results: dict[str, Any] = {}
        total = len(phone_numbers)

        tasks = [
            _get_spr_with_semaphore(
                client, semaphore,
                cfg["org_id"], cfg["workspace_id"], cfg["app_id"],
                phone,
            )
            for phone in phone_numbers
        ]

        for i, coro in enumerate(asyncio.as_completed(tasks)):
            phone, data = await coro
            results[phone] = data
            if progress_callback:
                progress_callback(i + 1, total)

        return results
    finally:
        await client.close()


async def _get_single(env_name: str, phone_number: str) -> tuple[str, Any]:
    cfg = get_env_config(env_name)
    client = SarvamClient(BASE_URL)
    try:
        await client.login(cfg["org_id"], cfg["user_id"], cfg["password"])
        return await client.get_spr(
            cfg["org_id"], cfg["workspace_id"], cfg["app_id"], phone_number,
        )
    finally:
        await client.close()


async def _update_single(env_name: str, phone_number: str, payload: dict) -> tuple[str, str]:
    cfg = get_env_config(env_name)
    client = SarvamClient(BASE_URL)
    try:
        await client.login(cfg["org_id"], cfg["user_id"], cfg["password"])
        return await client.update_spr(
            cfg["org_id"], cfg["workspace_id"], cfg["app_id"], phone_number, payload,
        )
    finally:
        await client.close()


async def _update_multiple(
    env_name: str,
    phone_configs: dict[str, dict],
    progress_callback: Callable[[int, int], None] | None = None,
) -> dict[str, str]:
    cfg = get_env_config(env_name)
    client = SarvamClient(BASE_URL)
    try:
        await client.login(cfg["org_id"], cfg["user_id"], cfg["password"])
        semaphore = Semaphore(MAX_CONCURRENT)
        results: dict[str, str] = {}
        total = len(phone_configs)

        tasks = [
            _update_spr_with_semaphore(
                client, semaphore,
                cfg["org_id"], cfg["workspace_id"], cfg["app_id"],
                phone, payload,
            )
            for phone, payload in phone_configs.items()
        ]

        for i, coro in enumerate(asyncio.as_completed(tasks)):
            phone, status = await coro
            results[phone] = status
            if progress_callback:
                progress_callback(i + 1, total)

        return results
    finally:
        await client.close()


def _run_async(coro):
    """Bridge from sync Streamlit world into async."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, coro).result()
    return asyncio.run(coro)


# ── Public sync API (called by Streamlit pages) ─────────────────────────

def get_spr(env_name: str, phone_number: str) -> tuple[str, Any]:
    """Fetch SPR for a single phone number."""
    return _run_async(_get_single(env_name, phone_number))


def get_multiple_sprs(
    env_name: str,
    phone_numbers: list[str],
    progress_callback: Callable[[int, int], None] | None = None,
) -> dict[str, Any]:
    """Fetch SPRs for multiple phone numbers."""
    return _run_async(_get_multiple(env_name, phone_numbers, progress_callback))


def update_spr(env_name: str, phone_number: str, payload: dict) -> tuple[str, str]:
    """Update SPR for a single phone number."""
    return _run_async(_update_single(env_name, phone_number, payload))


def update_multiple_sprs(
    env_name: str,
    phone_configs: dict[str, dict],
    progress_callback: Callable[[int, int], None] | None = None,
) -> dict[str, str]:
    """Update SPRs for multiple phone numbers."""
    return _run_async(_update_multiple(env_name, phone_configs, progress_callback))
