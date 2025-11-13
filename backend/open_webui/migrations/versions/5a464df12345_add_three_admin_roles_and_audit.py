"""Add three admin roles and audit logging tables

Revision ID: 5a464df12345
Revises: 1af9b942657b
Create Date: 2025-11-12 02:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

revision = "5a464df12345"
down_revision = "1af9b942657b"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    # Create audit_log table
    if "audit_log" not in tables:
        op.create_table(
            "audit_log",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("user_id", sa.String(), nullable=True),
            sa.Column("user_name", sa.String(), nullable=True),
            sa.Column("user_email", sa.String(), nullable=True),
            sa.Column("user_role", sa.String(), nullable=True),
            sa.Column("action", sa.String(), nullable=True),
            sa.Column("resource_type", sa.String(), nullable=True),
            sa.Column("resource_id", sa.String(), nullable=True),
            sa.Column("method", sa.String(), nullable=True),
            sa.Column("endpoint", sa.String(), nullable=True),
            sa.Column("request_body", sa.Text(), nullable=True),
            sa.Column("response_status", sa.Integer(), nullable=True),
            sa.Column("response_body", sa.Text(), nullable=True),
            sa.Column("ip_address", sa.String(), nullable=True),
            sa.Column("user_agent", sa.String(), nullable=True),
            sa.Column("timestamp", sa.BigInteger(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

        # Create indexes for audit_log
        op.create_index("idx_audit_user_id", "audit_log", ["user_id"])
        op.create_index("idx_audit_timestamp", "audit_log", ["timestamp"])
        op.create_index("idx_audit_action", "audit_log", ["action"])
        op.create_index("idx_audit_resource_type", "audit_log", ["resource_type"])
        op.create_index("idx_audit_user_role", "audit_log", ["user_role"])

    # Create login_log table
    if "login_log" not in tables:
        op.create_table(
            "login_log",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("user_id", sa.String(), nullable=True),
            sa.Column("user_email", sa.String(), nullable=True),
            sa.Column("login_type", sa.String(), nullable=True),
            sa.Column("status", sa.String(), nullable=True),
            sa.Column("failure_reason", sa.String(), nullable=True),
            sa.Column("ip_address", sa.String(), nullable=True),
            sa.Column("user_agent", sa.String(), nullable=True),
            sa.Column("timestamp", sa.BigInteger(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

        # Create indexes for login_log
        op.create_index("idx_login_user_id", "login_log", ["user_id"])
        op.create_index("idx_login_timestamp", "login_log", ["timestamp"])
        op.create_index("idx_login_status", "login_log", ["status"])
        op.create_index("idx_login_user_email", "login_log", ["user_email"])


def downgrade():
    # Drop indexes first
    op.drop_index("idx_audit_user_id", table_name="audit_log")
    op.drop_index("idx_audit_timestamp", table_name="audit_log")
    op.drop_index("idx_audit_action", table_name="audit_log")
    op.drop_index("idx_audit_resource_type", table_name="audit_log")
    op.drop_index("idx_audit_user_role", table_name="audit_log")

    op.drop_index("idx_login_user_id", table_name="login_log")
    op.drop_index("idx_login_timestamp", table_name="login_log")
    op.drop_index("idx_login_status", table_name="login_log")
    op.drop_index("idx_login_user_email", table_name="login_log")

    # Drop tables
    op.drop_table("audit_log")
    op.drop_table("login_log")
