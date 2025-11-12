import time
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, String, Text, Integer, Index

from open_webui.internal.db import Base, get_db


####################
# Audit Log DB Schema
####################


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(String, primary_key=True)
    user_id = Column(String)
    user_name = Column(String)
    user_email = Column(String)
    user_role = Column(String)

    action = Column(String)  # CREATE, UPDATE, DELETE, READ, LOGIN, LOGOUT
    resource_type = Column(String)  # user, model, config, chat, etc.
    resource_id = Column(String, nullable=True)

    method = Column(String)  # HTTP method
    endpoint = Column(String)  # API endpoint

    request_body = Column(Text, nullable=True)
    response_status = Column(Integer)
    response_body = Column(Text, nullable=True)

    ip_address = Column(String)
    user_agent = Column(String, nullable=True)

    timestamp = Column(BigInteger)

    __table_args__ = (
        Index("idx_audit_user_id", "user_id"),
        Index("idx_audit_timestamp", "timestamp"),
        Index("idx_audit_action", "action"),
        Index("idx_audit_resource_type", "resource_type"),
        Index("idx_audit_user_role", "user_role"),
    )


class AuditLogModel(BaseModel):
    id: str
    user_id: str
    user_name: str
    user_email: str
    user_role: str

    action: str
    resource_type: str
    resource_id: Optional[str] = None

    method: str
    endpoint: str

    request_body: Optional[str] = None
    response_status: int
    response_body: Optional[str] = None

    ip_address: str
    user_agent: Optional[str] = None

    timestamp: int

    model_config = ConfigDict(from_attributes=True)


####################
# Audit Log Forms
####################


class AuditLogFilterForm(BaseModel):
    user_id: Optional[str] = None
    user_role: Optional[str] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    ip_address: Optional[str] = None


class AuditLogSummary(BaseModel):
    total_operations: int
    operations_by_action: dict
    operations_by_user_role: dict
    operations_by_resource_type: dict
    failed_operations: int
    unique_users: int


####################
# Audit Log Table
####################


class AuditLogsTable:
    def insert_audit_log(
        self,
        id: str,
        user_id: str,
        user_name: str,
        user_email: str,
        user_role: str,
        action: str,
        resource_type: str,
        method: str,
        endpoint: str,
        response_status: int,
        ip_address: str,
        resource_id: Optional[str] = None,
        request_body: Optional[str] = None,
        response_body: Optional[str] = None,
        user_agent: Optional[str] = None,
        timestamp: Optional[int] = None,
    ) -> Optional[AuditLogModel]:
        if timestamp is None:
            timestamp = int(time.time())

        with get_db() as db:
            audit_log = AuditLogModel(
                **{
                    "id": id,
                    "user_id": user_id,
                    "user_name": user_name,
                    "user_email": user_email,
                    "user_role": user_role,
                    "action": action,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "method": method,
                    "endpoint": endpoint,
                    "request_body": request_body,
                    "response_status": response_status,
                    "response_body": response_body,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "timestamp": timestamp,
                }
            )
            result = AuditLog(**audit_log.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            return audit_log if result else None

    def get_audit_logs(
        self,
        skip: int = 0,
        limit: int = 50,
        filters: Optional[AuditLogFilterForm] = None,
    ) -> List[AuditLogModel]:
        with get_db() as db:
            query = db.query(AuditLog)

            if filters:
                if filters.user_id:
                    query = query.filter(AuditLog.user_id == filters.user_id)
                if filters.user_role:
                    query = query.filter(AuditLog.user_role == filters.user_role)
                if filters.action:
                    query = query.filter(AuditLog.action == filters.action)
                if filters.resource_type:
                    query = query.filter(AuditLog.resource_type == filters.resource_type)
                if filters.start_time:
                    query = query.filter(AuditLog.timestamp >= filters.start_time)
                if filters.end_time:
                    query = query.filter(AuditLog.timestamp <= filters.end_time)
                if filters.ip_address:
                    query = query.filter(AuditLog.ip_address == filters.ip_address)

            query = query.order_by(AuditLog.timestamp.desc())
            query = query.offset(skip).limit(limit)

            logs = query.all()
            return [AuditLogModel.model_validate(log) for log in logs]

    def get_audit_logs_by_user_id(
        self, user_id: str, skip: int = 0, limit: int = 50
    ) -> List[AuditLogModel]:
        with get_db() as db:
            logs = (
                db.query(AuditLog)
                .filter(AuditLog.user_id == user_id)
                .order_by(AuditLog.timestamp.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            return [AuditLogModel.model_validate(log) for log in logs]

    def get_admin_audit_logs(
        self, skip: int = 0, limit: int = 50
    ) -> List[AuditLogModel]:
        """Get audit logs for all admin users"""
        with get_db() as db:
            logs = (
                db.query(AuditLog)
                .filter(
                    AuditLog.user_role.in_(
                        ["system_admin", "auth_admin", "audit_admin", "admin"]
                    )
                )
                .order_by(AuditLog.timestamp.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            return [AuditLogModel.model_validate(log) for log in logs]

    def get_audit_summary(
        self, start_time: int, end_time: int
    ) -> Optional[AuditLogSummary]:
        """Generate audit summary report"""
        with get_db() as db:
            from sqlalchemy import func, distinct

            query = db.query(AuditLog).filter(
                AuditLog.timestamp >= start_time, AuditLog.timestamp <= end_time
            )

            total_operations = query.count()

            # Operations by action
            operations_by_action = {}
            action_stats = (
                query.with_entities(AuditLog.action, func.count(AuditLog.id))
                .group_by(AuditLog.action)
                .all()
            )
            for action, count in action_stats:
                operations_by_action[action] = count

            # Operations by user role
            operations_by_user_role = {}
            role_stats = (
                query.with_entities(AuditLog.user_role, func.count(AuditLog.id))
                .group_by(AuditLog.user_role)
                .all()
            )
            for role, count in role_stats:
                operations_by_user_role[role] = count

            # Operations by resource type
            operations_by_resource_type = {}
            resource_stats = (
                query.with_entities(AuditLog.resource_type, func.count(AuditLog.id))
                .group_by(AuditLog.resource_type)
                .all()
            )
            for resource_type, count in resource_stats:
                operations_by_resource_type[resource_type] = count

            # Failed operations (status >= 400)
            failed_operations = query.filter(AuditLog.response_status >= 400).count()

            # Unique users
            unique_users = (
                query.with_entities(func.count(distinct(AuditLog.user_id)))
                .scalar()
            )

            return AuditLogSummary(
                total_operations=total_operations,
                operations_by_action=operations_by_action,
                operations_by_user_role=operations_by_user_role,
                operations_by_resource_type=operations_by_resource_type,
                failed_operations=failed_operations,
                unique_users=unique_users,
            )

    def get_count(self, filters: Optional[AuditLogFilterForm] = None) -> int:
        """Get total count of audit logs matching filters"""
        with get_db() as db:
            query = db.query(AuditLog)

            if filters:
                if filters.user_id:
                    query = query.filter(AuditLog.user_id == filters.user_id)
                if filters.user_role:
                    query = query.filter(AuditLog.user_role == filters.user_role)
                if filters.action:
                    query = query.filter(AuditLog.action == filters.action)
                if filters.resource_type:
                    query = query.filter(AuditLog.resource_type == filters.resource_type)
                if filters.start_time:
                    query = query.filter(AuditLog.timestamp >= filters.start_time)
                if filters.end_time:
                    query = query.filter(AuditLog.timestamp <= filters.end_time)
                if filters.ip_address:
                    query = query.filter(AuditLog.ip_address == filters.ip_address)

            return query.count()


AuditLogs = AuditLogsTable()
