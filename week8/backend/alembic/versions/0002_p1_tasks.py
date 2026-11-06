"""P1 Level 1 task schema."""
from alembic import op
import sqlalchemy as sa
revision="0002_p1_tasks"; down_revision="0001_p0"; branch_labels=None; depends_on=None
def upgrade():
    op.create_table("tasks",
        sa.Column("id",sa.String(36),primary_key=True),
        sa.Column("title",sa.String(100),nullable=False),
        sa.Column("description",sa.Text(),nullable=False,server_default=""),
        sa.Column("category",sa.String(20),nullable=False,server_default="assignment"),
        sa.Column("priority",sa.String(10),nullable=False,server_default="medium"),
        sa.Column("status",sa.String(10),nullable=False,server_default="todo"),
        sa.Column("due_date",sa.Date(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("completed_at",sa.DateTime(timezone=True),nullable=True),
        sa.Column("legacy_source_id",sa.Integer(),nullable=True),
        sa.CheckConstraint("category IN ('assignment','exam','project','other')",name="ck_tasks_category"),
        sa.CheckConstraint("priority IN ('high','medium','low')",name="ck_tasks_priority"),
        sa.CheckConstraint("status IN ('todo','done')",name="ck_tasks_status"),
        sa.UniqueConstraint("legacy_source_id",name="uq_tasks_legacy_source_id"))
    op.create_index("ix_tasks_status_due_date","tasks",["status","due_date"])
    op.create_index("ix_tasks_category","tasks",["category"])
    op.execute("UPDATE system_metadata SET value='P1' WHERE key='schema_stage'")
def downgrade():
    op.drop_index("ix_tasks_category",table_name="tasks"); op.drop_index("ix_tasks_status_due_date",table_name="tasks"); op.drop_table("tasks")
    op.execute("UPDATE system_metadata SET value='P0' WHERE key='schema_stage'")
