"""Thin Bluesky AT Proto client — always respects dry_run."""

from __future__ import annotations

import logging
import mimetypes
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from bluesky_mcp.config import get_settings

log = logging.getLogger(__name__)

_session_jwt: str | None = None
_session_did: str | None = None


def _iso_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _configured() -> dict[str, Any] | None:
    cfg = get_settings()
    if not cfg.credentials_ready:
        return {
            "success": False,
            "error": (
                "Bluesky credentials required: set BLUESKY_HANDLE + BLUESKY_APP_PASSWORD "
                "(or BLUESKY_ACCESS_TOKEN + BLUESKY_DID)"
            ),
            "dry_run": False,
        }
    return None


async def _ensure_session(http: httpx.AsyncClient) -> dict[str, Any] | None:
    """Return None on success; error dict on failure. Sets module session cache."""
    global _session_jwt, _session_did
    cfg = get_settings()
    if cfg.access_token and cfg.did:
        _session_jwt = cfg.access_token
        _session_did = cfg.did
        return None
    if _session_jwt and _session_did:
        return None
    if not (cfg.handle and cfg.app_password):
        return _configured()
    url = f"{cfg.instance}/xrpc/com.atproto.server.createSession"
    try:
        resp = await http.post(
            url,
            json={"identifier": cfg.handle, "password": cfg.app_password},
        )
        if resp.status_code >= 400:
            return {
                "success": False,
                "error": f"createSession HTTP {resp.status_code}",
                "detail": resp.text[:300],
            }
        data = resp.json()
        _session_jwt = data.get("accessJwt")
        _session_did = data.get("did")
        if not _session_jwt or not _session_did:
            return {"success": False, "error": "createSession missing accessJwt/did"}
        return None
    except httpx.HTTPError as exc:
        return {"success": False, "error": str(exc)}


def _auth_headers(*, json_body: bool = True) -> dict[str, str]:
    h: dict[str, str] = {"Authorization": f"Bearer {_session_jwt}"}
    if json_body:
        h["Content-Type"] = "application/json"
    return h


async def create_status(
    status_text: str,
    *,
    visibility: str = "public",
    spoiler_text: str | None = None,
    in_reply_to_id: str | None = None,
    reply_root: str | None = None,
    reply_parent_cid: str | None = None,
    reply_root_cid: str | None = None,
    media_ids: list[str] | None = None,
    embed_blobs: list[dict[str, Any]] | None = None,
    dry_run: bool | None = None,
) -> dict[str, Any]:
    """Create an app.bsky.feed.post record. visibility kept for outbox parity (ignored on AP)."""
    _ = visibility
    _ = spoiler_text
    cfg = get_settings()
    use_dry = cfg.dry_run if dry_run is None else dry_run
    if use_dry:
        log.info("DRY RUN post: %s", status_text[:120])
        return {
            "success": True,
            "dry_run": True,
            "message": "dry_run — not posted",
            "status_text": status_text,
            "in_reply_to_id": in_reply_to_id,
            "media_ids": media_ids or [],
            "id": "dry-run",
            "uri": "at://dry-run/app.bsky.feed.post/dry",
        }
    err = _configured()
    if err:
        return err

    record: dict[str, Any] = {
        "$type": "app.bsky.feed.post",
        "text": status_text,
        "createdAt": _iso_now(),
    }
    if in_reply_to_id and in_reply_to_id.startswith("at://"):
        parent_uri = in_reply_to_id
        root_uri = reply_root or parent_uri
        record["reply"] = {
            "parent": {"uri": parent_uri, "cid": reply_parent_cid or ""},
            "root": {"uri": root_uri, "cid": reply_root_cid or reply_parent_cid or ""},
        }
        if not reply_parent_cid:
            return {
                "success": False,
                "error": "reply requires reply_parent_cid (and preferably reply_root/cid)",
            }
    if embed_blobs:
        record["embed"] = {
            "$type": "app.bsky.embed.images",
            "images": embed_blobs,
        }

    try:
        async with httpx.AsyncClient(timeout=30.0) as http:
            sess_err = await _ensure_session(http)
            if sess_err:
                return sess_err
            url = f"{cfg.instance}/xrpc/com.atproto.repo.createRecord"
            body = {
                "repo": _session_did,
                "collection": "app.bsky.feed.post",
                "record": record,
            }
            resp = await http.post(url, headers=_auth_headers(), json=body)
            if resp.status_code >= 400:
                return {
                    "success": False,
                    "error": f"createRecord HTTP {resp.status_code}",
                    "detail": resp.text[:300],
                }
            data = resp.json()
            return {
                "success": True,
                "dry_run": False,
                "id": data.get("uri") or data.get("cid"),
                "uri": data.get("uri"),
                "cid": data.get("cid"),
                "data": data,
            }
    except httpx.HTTPError as exc:
        log.exception("create_status failed")
        return {"success": False, "error": str(exc)}


async def reply_status(
    in_reply_to_id: str,
    status_text: str,
    *,
    visibility: str = "public",
    reply_root: str | None = None,
    reply_parent_cid: str | None = None,
    reply_root_cid: str | None = None,
    dry_run: bool | None = None,
) -> dict[str, Any]:
    if not in_reply_to_id:
        return {"success": False, "error": "in_reply_to_id (at:// URI) required"}
    return await create_status(
        status_text,
        visibility=visibility,
        in_reply_to_id=in_reply_to_id,
        reply_root=reply_root,
        reply_parent_cid=reply_parent_cid,
        reply_root_cid=reply_root_cid,
        dry_run=dry_run,
    )


async def boost_status(
    status_id: str,
    *,
    cid: str = "",
    dry_run: bool | None = None,
) -> dict[str, Any]:
    """Repost (Bluesky equivalent of boost). status_id must be an at:// URI; cid required live."""
    if not status_id:
        return {"success": False, "error": "status_id (at:// URI) required"}
    cfg = get_settings()
    use_dry = cfg.dry_run if dry_run is None else dry_run
    if use_dry:
        return {
            "success": True,
            "dry_run": True,
            "message": "dry_run — repost not sent",
            "status_id": status_id,
            "id": "dry-run-repost",
        }
    err = _configured()
    if err:
        return err
    if not cid:
        return {"success": False, "error": "cid required for live repost"}
    record = {
        "$type": "app.bsky.feed.repost",
        "subject": {"uri": status_id, "cid": cid},
        "createdAt": _iso_now(),
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as http:
            sess_err = await _ensure_session(http)
            if sess_err:
                return sess_err
            url = f"{cfg.instance}/xrpc/com.atproto.repo.createRecord"
            resp = await http.post(
                url,
                headers=_auth_headers(),
                json={
                    "repo": _session_did,
                    "collection": "app.bsky.feed.repost",
                    "record": record,
                },
            )
            if resp.status_code >= 400:
                return {
                    "success": False,
                    "error": f"repost HTTP {resp.status_code}",
                    "detail": resp.text[:300],
                }
            data = resp.json()
            return {
                "success": True,
                "dry_run": False,
                "id": data.get("uri"),
                "uri": data.get("uri"),
                "data": data,
            }
    except httpx.HTTPError as exc:
        return {"success": False, "error": str(exc)}


async def upload_media(
    path: str,
    *,
    description: str = "",
    dry_run: bool | None = None,
) -> dict[str, Any]:
    if not path:
        return {"success": False, "error": "media path required"}
    file_path = Path(path)
    if not file_path.is_file():
        return {"success": False, "error": f"file not found: {path}"}
    cfg = get_settings()
    use_dry = cfg.dry_run if dry_run is None else dry_run
    if use_dry:
        return {
            "success": True,
            "dry_run": True,
            "message": "dry_run — blob not uploaded",
            "path": str(file_path),
            "id": "dry-run-media",
            "description": description,
        }
    err = _configured()
    if err:
        return err
    mime, _ = mimetypes.guess_type(str(file_path))
    mime = mime or "application/octet-stream"
    try:
        async with httpx.AsyncClient(timeout=120.0) as http:
            sess_err = await _ensure_session(http)
            if sess_err:
                return sess_err
            url = f"{cfg.instance}/xrpc/com.atproto.repo.uploadBlob"
            data_bytes = file_path.read_bytes()
            resp = await http.post(
                url,
                headers={
                    "Authorization": f"Bearer {_session_jwt}",
                    "Content-Type": mime,
                },
                content=data_bytes,
            )
            if resp.status_code >= 400:
                return {
                    "success": False,
                    "error": f"uploadBlob HTTP {resp.status_code}",
                    "detail": resp.text[:300],
                }
            body = resp.json()
            blob = body.get("blob") or body
            return {
                "success": True,
                "dry_run": False,
                "id": str(blob.get("ref", {}).get("$link") or blob),
                "blob": blob,
                "alt": description,
                "embed_image": {"alt": description or file_path.name, "image": blob},
                "data": body,
            }
    except OSError as exc:
        return {"success": False, "error": str(exc)}
    except httpx.HTTPError as exc:
        return {"success": False, "error": str(exc)}


async def get_notifications(limit: int = 20) -> dict[str, Any]:
    cfg = get_settings()
    if cfg.dry_run and not cfg.credentials_ready:
        return {
            "success": True,
            "dry_run": True,
            "notifications": [],
            "message": "dry_run — notifications empty without credentials",
        }
    if not cfg.credentials_ready:
        return {"success": False, "error": "not configured"}
    try:
        async with httpx.AsyncClient(timeout=30.0) as http:
            sess_err = await _ensure_session(http)
            if sess_err:
                return sess_err
            url = f"{cfg.instance}/xrpc/app.bsky.notification.listNotifications"
            resp = await http.get(
                url,
                headers=_auth_headers(json_body=False),
                params={"limit": limit},
            )
            if resp.status_code >= 400:
                return {"success": False, "error": f"HTTP {resp.status_code}"}
            data = resp.json()
            return {"success": True, "notifications": data.get("notifications", data)}
    except httpx.HTTPError as exc:
        return {"success": False, "error": str(exc)}


async def get_timeline(timeline: str = "home", limit: int = 20) -> dict[str, Any]:
    cfg = get_settings()
    if not cfg.credentials_ready:
        return {"success": False, "error": "not configured"}
    try:
        async with httpx.AsyncClient(timeout=30.0) as http:
            sess_err = await _ensure_session(http)
            if sess_err:
                return sess_err
            if timeline in ("home", "following"):
                xrpc = "app.bsky.feed.getTimeline"
            else:
                # public/local → author feed of self as a safe default when no feed URI
                xrpc = "app.bsky.feed.getAuthorFeed"
            url = f"{cfg.instance}/xrpc/{xrpc}"
            params: dict[str, Any] = {"limit": limit}
            if xrpc.endswith("getAuthorFeed"):
                params["actor"] = _session_did
            resp = await http.get(
                url,
                headers=_auth_headers(json_body=False),
                params=params,
            )
            if resp.status_code >= 400:
                return {"success": False, "error": f"HTTP {resp.status_code}"}
            data = resp.json()
            feed = data.get("feed", [])
            statuses = []
            for item in feed:
                post = item.get("post") or {}
                record = post.get("record") or {}
                statuses.append(
                    {
                        "uri": post.get("uri"),
                        "cid": post.get("cid"),
                        "text": record.get("text"),
                        "author": (post.get("author") or {}).get("handle"),
                        "createdAt": record.get("createdAt"),
                    }
                )
            return {"success": True, "statuses": statuses, "feed": feed}
    except httpx.HTTPError as exc:
        return {"success": False, "error": str(exc)}


async def push_subscription_get() -> dict[str, Any]:
    """Bluesky has no Mastodon-style Web Push subscription API — declare N/A."""
    cfg = get_settings()
    return {
        "success": True,
        "subscription": None,
        "message": "N/A — Bluesky AT Proto does not expose Mastodon-style Web Push subscriptions",
        "dry_run": cfg.dry_run,
        "na": True,
    }


def clear_session_cache() -> None:
    global _session_jwt, _session_did
    _session_jwt = None
    _session_did = None
