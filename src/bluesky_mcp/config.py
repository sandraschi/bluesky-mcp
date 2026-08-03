"""bluesky-mcp configuration."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _default_data_dir() -> str:
    if getattr(sys, "frozen", False):
        # PyInstaller onefile: repo-relative paths resolve into the throwaway
        # _MEIPASS temp dir. Persist under %LOCALAPPDATA%/{identifier} instead.
        return str(Path(os.environ.get("LOCALAPPDATA", Path.home())) / "ai.fleet.bluesky-mcp")
    return str(Path(__file__).resolve().parents[2] / "data")


@dataclass
class Settings:
    server_name: str = "bluesky-mcp"
    backend_port: int = 10760
    # PDS base URL (default Bluesky AppView/PDS entry)
    instance: str = "https://bsky.social"
    handle: str = ""
    app_password: str = ""
    # Optional pre-issued session JWT (skips createSession when set with did)
    access_token: str = ""
    did: str = ""
    dry_run: bool = True
    require_outbox_approval: bool = True
    data_dir: str = ""
    log_level: str = "INFO"
    webhook_secret: str = ""

    def __post_init__(self) -> None:
        self.backend_port = int(os.getenv("BLUESKY_BACKEND_PORT", self.backend_port))
        pds = os.getenv("BLUESKY_PDS") or os.getenv("BLUESKY_INSTANCE") or self.instance
        self.instance = (pds or "").rstrip("/")
        self.handle = (os.getenv("BLUESKY_HANDLE", self.handle) or "").lstrip("@")
        self.app_password = os.getenv("BLUESKY_APP_PASSWORD", self.app_password) or ""
        self.access_token = os.getenv("BLUESKY_ACCESS_TOKEN", self.access_token) or ""
        self.did = os.getenv("BLUESKY_DID", self.did) or ""
        dry = os.getenv("BLUESKY_DRY_RUN", "1")
        self.dry_run = dry not in ("0", "false", "False", "no")
        req = os.getenv("BLUESKY_REQUIRE_OUTBOX_APPROVAL", "1")
        self.require_outbox_approval = req not in ("0", "false", "False", "no")
        self.data_dir = os.getenv("BLUESKY_DATA_DIR", "") or _default_data_dir()
        self.log_level = os.getenv("BLUESKY_LOG_LEVEL", self.log_level)
        self.webhook_secret = os.getenv("BLUESKY_WEBHOOK_SECRET", "") or ""

    @property
    def credentials_ready(self) -> bool:
        if self.access_token and self.did:
            return True
        return bool(self.handle and self.app_password)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
