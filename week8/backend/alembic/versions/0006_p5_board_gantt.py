"""P5 board gantt comments."""
from alembic import op
import sqlalchemy as sa
revision="0006_p5_board_gantt";down_revision="0005_p4_teams_projects";branch_labels=None;depends_on=None
def upgrade():
 op.create_table("project_tasks",sa.Column("id",sa.String(36),primary_key=True),sa.Column("project_id",sa.String(36),sa.ForeignKey("projects.id",ondelete="CASCADE")),sa.Column("created_by",sa.String(36),sa.ForeignKey("users.id")),sa.Column("assignee_id",sa.String(36),sa.ForeignKey("users.id",ondelete="SET NULL")),sa.Column("title",sa.String(100)),sa.Column("description",sa.Text()),sa.Column("priority",sa.String(10)),sa.Column("status",sa.String(20)),sa.Column("start_date",sa.Date()),sa.Column("due_date",sa.Date()),sa.Column("estimated_hours",sa.Float()),sa.Column("created_at",sa.DateTime(timezone=True)),sa.Column("updated_at",sa.DateTime(timezone=True)),sa.Column("completed_at",sa.DateTime(timezone=True)));op.create_index("ix_project_tasks_project_id","project_tasks",["project_id"])
 op.create_table("task_comments",sa.Column("id",sa.String(36),primary_key=True),sa.Column("task_id",sa.String(36),sa.ForeignKey("project_tasks.id",ondelete="CASCADE")),sa.Column("author_id",sa.String(36),sa.ForeignKey("users.id")),sa.Column("body",sa.Text()),sa.Column("created_at",sa.DateTime(timezone=True)));op.create_index("ix_task_comments_task_id","task_comments",["task_id"]);op.execute("UPDATE system_metadata SET value='P5' WHERE key='schema_stage'")
def downgrade():op.drop_table("task_comments");op.drop_table("project_tasks")
