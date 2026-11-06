"""P3 calendar notifications."""
from alembic import op
import sqlalchemy as sa
revision="0004_p3_calendar_notifications";down_revision="0003_p2_accounts_courses";branch_labels=None;depends_on=None
def upgrade():
 op.create_table("notifications",sa.Column("id",sa.String(36),primary_key=True),sa.Column("user_id",sa.String(36),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),sa.Column("kind",sa.String(30),nullable=False),sa.Column("entity_type",sa.String(30),nullable=False),sa.Column("entity_id",sa.String(36),nullable=False),sa.Column("dedupe_key",sa.String(200),nullable=False),sa.Column("message",sa.String(300),nullable=False),sa.Column("read_at",sa.DateTime(timezone=True)),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),sa.UniqueConstraint("user_id","dedupe_key",name="uq_notification_dedupe"));op.create_index("ix_notifications_user_id","notifications",["user_id"]);op.execute("UPDATE system_metadata SET value='P3' WHERE key='schema_stage'")
def downgrade(): op.drop_table("notifications")
