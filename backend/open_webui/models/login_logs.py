import time
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, String, Index

from open_webui.internal.db import Base, get_db


####################
# Login Log DB Schema
####################


class LoginLog(Base):
    __tablename__ = "login_log"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True)  # Nullable for failed logins
    user_email = Column(String)

    login_type = Column(String)  # password, oauth, ldap, api_key
    status = Column(String)  # success, failed
    failure_reason = Column(String, nullable=True)

    ip_address = Column(String)
    user_agent = Column(String, nullable=True)

    timestamp = Column(BigInteger)

    __table_args__ = (
        Index("idx_login_user_id", "user_id"),
        Index("idx_login_timestamp", "timestamp"),
        Index("idx_login_status", "status"),
        Index("idx_login_user_email", "user_email"),
    )


class LoginLogModel(BaseModel):
    id: str
    user_id: Optional[str] = None
    user_email: str

    login_type: str
    status: str
    failure_reason: Optional[str] = None

    ip_address: str
    user_agent: Optional[str] = None

    timestamp: int

    model_config = ConfigDict(from_attributes=True)


####################
# Login Log Forms
####################


class LoginLogFilterForm(BaseModel):
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    login_type: Optional[str] = None
    status: Optional[str] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    ip_address: Optional[str] = None


class LoginLogSummary(BaseModel):
    total_logins: int
    successful_logins: int
    failed_logins: int
    logins_by_type: dict
    unique_users: int


####################
# Login Log Table
####################


class LoginLogsTable:
    def insert_login_log(
        self,
        id: str,
        user_email: str,
        login_type: str,
        status: str,
        ip_address: str,
        user_id: Optional[str] = None,
        failure_reason: Optional[str] = None,
        user_agent: Optional[str] = None,
        timestamp: Optional[int] = None,
    ) -> Optional[LoginLogModel]:
        if timestamp is None:
            timestamp = int(time.time())

        with get_db() as db:
            login_log = LoginLogModel(
                **{
                    "id": id,
                    "user_id": user_id,
                    "user_email": user_email,
                    "login_type": login_type,
                    "status": status,
                    "failure_reason": failure_reason,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "timestamp": timestamp,
                }
            )
            result = LoginLog(**login_log.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            return login_log if result else None

    def get_login_logs(
        self,
        skip: int = 0,
        limit: int = 50,
        filters: Optional[LoginLogFilterForm] = None,
    ) -> List[LoginLogModel]:
        with get_db() as db:
            query = db.query(LoginLog)

            if filters:
                if filters.user_id:
                    query = query.filter(LoginLog.user_id == filters.user_id)
                if filters.user_email:
                    query = query.filter(LoginLog.user_email == filters.user_email)
                if filters.login_type:
                    query = query.filter(LoginLog.login_type == filters.login_type)
                if filters.status:
                    query = query.filter(LoginLog.status == filters.status)
                if filters.start_time:
                    query = query.filter(LoginLog.timestamp >= filters.start_time)
                if filters.end_time:
                    query = query.filter(LoginLog.timestamp <= filters.end_time)
                if filters.ip_address:
                    query = query.filter(LoginLog.ip_address == filters.ip_address)

            query = query.order_by(LoginLog.timestamp.desc())
            query = query.offset(skip).limit(limit)

            logs = query.all()
            return [LoginLogModel.model_validate(log) for log in logs]

    def get_login_logs_by_user_id(
        self, user_id: str, skip: int = 0, limit: int = 50
    ) -> List[LoginLogModel]:
        with get_db() as db:
            logs = (
                db.query(LoginLog)
                .filter(LoginLog.user_id == user_id)
                .order_by(LoginLog.timestamp.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            return [LoginLogModel.model_validate(log) for log in logs]

    def get_failed_login_logs(
        self, skip: int = 0, limit: int = 50
    ) -> List[LoginLogModel]:
        """Get all failed login attempts"""
        with get_db() as db:
            logs = (
                db.query(LoginLog)
                .filter(LoginLog.status == "failed")
                .order_by(LoginLog.timestamp.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            return [LoginLogModel.model_validate(log) for log in logs]

    def get_login_summary(
        self, start_time: int, end_time: int
    ) -> Optional[LoginLogSummary]:
        """Generate login summary report"""
        with get_db() as db:
            from sqlalchemy import func, distinct

            query = db.query(LoginLog).filter(
                LoginLog.timestamp >= start_time, LoginLog.timestamp <= end_time
            )

            total_logins = query.count()

            successful_logins = query.filter(LoginLog.status == "success").count()
            failed_logins = query.filter(LoginLog.status == "failed").count()

            # Logins by type
            logins_by_type = {}
            type_stats = (
                query.with_entities(LoginLog.login_type, func.count(LoginLog.id))
                .group_by(LoginLog.login_type)
                .all()
            )
            for login_type, count in type_stats:
                logins_by_type[login_type] = count

            # Unique users
            unique_users = (
                query.filter(LoginLog.user_id.isnot(None))
                .with_entities(func.count(distinct(LoginLog.user_id)))
                .scalar()
            )

            return LoginLogSummary(
                total_logins=total_logins,
                successful_logins=successful_logins,
                failed_logins=failed_logins,
                logins_by_type=logins_by_type,
                unique_users=unique_users,
            )

    def get_count(self, filters: Optional[LoginLogFilterForm] = None) -> int:
        """Get total count of login logs matching filters"""
        with get_db() as db:
            query = db.query(LoginLog)

            if filters:
                if filters.user_id:
                    query = query.filter(LoginLog.user_id == filters.user_id)
                if filters.user_email:
                    query = query.filter(LoginLog.user_email == filters.user_email)
                if filters.login_type:
                    query = query.filter(LoginLog.login_type == filters.login_type)
                if filters.status:
                    query = query.filter(LoginLog.status == filters.status)
                if filters.start_time:
                    query = query.filter(LoginLog.timestamp >= filters.start_time)
                if filters.end_time:
                    query = query.filter(LoginLog.timestamp <= filters.end_time)
                if filters.ip_address:
                    query = query.filter(LoginLog.ip_address == filters.ip_address)

            return query.count()


LoginLogs = LoginLogsTable()
