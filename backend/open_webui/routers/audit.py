import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from open_webui.models.audit_logs import (
    AuditLogs,
    AuditLogModel,
    AuditLogFilterForm,
    AuditLogSummary,
)
from open_webui.models.login_logs import (
    LoginLogs,
    LoginLogModel,
    LoginLogFilterForm,
    LoginLogSummary,
)
from open_webui.utils.auth import get_audit_admin
from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

router = APIRouter()

############################
# Get Audit Logs
############################


@router.get("/logs", response_model=list[AuditLogModel])
async def get_audit_logs(
    skip: int = 0,
    limit: int = 50,
    user_id: Optional[str] = None,
    user_role: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    ip_address: Optional[str] = None,
    user=Depends(get_audit_admin),
):
    """
    Query audit logs with filters.
    Only accessible by audit administrators.
    """
    filters = AuditLogFilterForm(
        user_id=user_id,
        user_role=user_role,
        action=action,
        resource_type=resource_type,
        start_time=start_time,
        end_time=end_time,
        ip_address=ip_address,
    )
    return AuditLogs.get_audit_logs(skip=skip, limit=limit, filters=filters)


@router.get("/logs/count")
async def get_audit_logs_count(
    user_id: Optional[str] = None,
    user_role: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    ip_address: Optional[str] = None,
    user=Depends(get_audit_admin),
):
    """Get total count of audit logs matching filters"""
    filters = AuditLogFilterForm(
        user_id=user_id,
        user_role=user_role,
        action=action,
        resource_type=resource_type,
        start_time=start_time,
        end_time=end_time,
        ip_address=ip_address,
    )
    return {"count": AuditLogs.get_count(filters=filters)}


############################
# Get User Audit Logs
############################


@router.get("/users/{user_id}", response_model=list[AuditLogModel])
async def get_user_audit_logs(
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    user=Depends(get_audit_admin),
):
    """
    Get audit logs for a specific user.
    Only accessible by audit administrators.
    """
    return AuditLogs.get_audit_logs_by_user_id(user_id, skip=skip, limit=limit)


############################
# Get Admin Audit Logs
############################


@router.get("/admins", response_model=list[AuditLogModel])
async def get_admin_audit_logs(
    skip: int = 0,
    limit: int = 50,
    user=Depends(get_audit_admin),
):
    """
    Get audit logs for all administrator users.
    Only accessible by audit administrators.
    """
    return AuditLogs.get_admin_audit_logs(skip=skip, limit=limit)


############################
# Get Audit Summary
############################


@router.get("/summary", response_model=AuditLogSummary)
async def get_audit_summary(
    start_time: int,
    end_time: int,
    user=Depends(get_audit_admin),
):
    """
    Generate audit summary report for a time range.
    Only accessible by audit administrators.
    """
    summary = AuditLogs.get_audit_summary(start_time, end_time)
    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate audit summary",
        )
    return summary


############################
# Get Login Logs
############################


@router.get("/logins", response_model=list[LoginLogModel])
async def get_login_logs(
    skip: int = 0,
    limit: int = 50,
    user_id: Optional[str] = None,
    user_email: Optional[str] = None,
    login_type: Optional[str] = None,
    status: Optional[str] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    ip_address: Optional[str] = None,
    user=Depends(get_audit_admin),
):
    """
    Query login logs with filters.
    Only accessible by audit administrators.
    """
    filters = LoginLogFilterForm(
        user_id=user_id,
        user_email=user_email,
        login_type=login_type,
        status=status,
        start_time=start_time,
        end_time=end_time,
        ip_address=ip_address,
    )
    return LoginLogs.get_login_logs(skip=skip, limit=limit, filters=filters)


@router.get("/logins/count")
async def get_login_logs_count(
    user_id: Optional[str] = None,
    user_email: Optional[str] = None,
    login_type: Optional[str] = None,
    status: Optional[str] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    ip_address: Optional[str] = None,
    user=Depends(get_audit_admin),
):
    """Get total count of login logs matching filters"""
    filters = LoginLogFilterForm(
        user_id=user_id,
        user_email=user_email,
        login_type=login_type,
        status=status,
        start_time=start_time,
        end_time=end_time,
        ip_address=ip_address,
    )
    return {"count": LoginLogs.get_count(filters=filters)}


############################
# Get User Login Logs
############################


@router.get("/logins/users/{user_id}", response_model=list[LoginLogModel])
async def get_user_login_logs(
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    user=Depends(get_audit_admin),
):
    """
    Get login logs for a specific user.
    Only accessible by audit administrators.
    """
    return LoginLogs.get_login_logs_by_user_id(user_id, skip=skip, limit=limit)


############################
# Get Failed Login Logs
############################


@router.get("/logins/failed", response_model=list[LoginLogModel])
async def get_failed_login_logs(
    skip: int = 0,
    limit: int = 50,
    user=Depends(get_audit_admin),
):
    """
    Get all failed login attempts.
    Only accessible by audit administrators.
    """
    return LoginLogs.get_failed_login_logs(skip=skip, limit=limit)


############################
# Get Login Summary
############################


@router.get("/logins/summary", response_model=LoginLogSummary)
async def get_login_summary(
    start_time: int,
    end_time: int,
    user=Depends(get_audit_admin),
):
    """
    Generate login summary report for a time range.
    Only accessible by audit administrators.
    """
    summary = LoginLogs.get_login_summary(start_time, end_time)
    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate login summary",
        )
    return summary
