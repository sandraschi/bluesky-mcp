"""Shared dialogic response helpers — Tool Design §7.1 Pattern 3."""

from __future__ import annotations

import logging
import sys
from typing import Any

log = logging.getLogger(__name__)


def err_response(
    error: str,
    error_type: str = "general",
    **kwargs: Any,
) -> dict[str, Any]:
    """Auto-logging error response — traceback captured when called from an except block.

    ## Return Format
    {"success": False, "error": str, "error_type": str, ...kwargs}

    ## Examples
    err_response("outbox_id required", "validation")
    """
    if sys.exc_info()[0] is not None:
        log.exception("Tool error: %s [%s]", error, error_type)
    else:
        log.error("Tool error: %s [%s]", error, error_type)
    return {"success": False, "error": error, "error_type": error_type, **kwargs}
