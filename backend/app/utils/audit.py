"""
Audit logging utility.

Provides a function to record audit trail entries for administrative
and security-relevant actions performed in the system.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.core.logging import get_logger
from app.core.supabase_client import get_supabase_admin

logger = get_logger(__name__)


async def log_audit(
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> None:
    """
    Write an audit log entry to the audit_logs table.

    Records administrative and security-relevant actions for compliance
    and troubleshooting purposes.

    Args:
        user_id: ID of the user who performed the action.
        action: Description of the action (e.g., 'user_verified', 'request_created').
        resource_type: Type of resource affected (e.g., 'user', 'blood_request', 'blood_bank').
        resource_id: ID of the affected resource.
        details: Additional context about the action.
        ip_address: Client IP address.
    """
    supabase = get_supabase_admin()

    audit_entry = {
        "user_id": user_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "details": details or {},
        "ip_address": ip_address,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        supabase.table("audit_logs").insert(audit_entry).execute()
        logger.info(
            "audit_logged",
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
        )
    except Exception as e:
        # Audit logging should never block the main operation
        logger.error(
            "audit_log_failed",
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            error=str(e),
        )
