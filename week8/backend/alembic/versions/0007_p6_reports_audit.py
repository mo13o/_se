"""P6 reports audit."""
from alembic import op
import sqlalchemy as sa
revision="0007_p6_reports_audit";down_revision="0006_p5_board_gantt";branch_labels=None;depends_on=None
def upgrade():
 op.create_table("audit_logs",sa.Column("id",sa.String(36),primary_key=True),sa.Column("actor_id",sa.String(36),sa.ForeignKey("users.id")),sa.Column("team_id",sa.String(36),sa.ForeignKey("teams.id",ondelete="SET NULL")),sa.Column("action",sa.String(50)),sa.Column("entity_type",sa.String(30)),sa.Column("entity_id",sa.String(36)),sa.Column("created_at",sa.DateTime(timezone=True)));op.execute("UPDATE system_metadata SET value='P6' WHERE key='schema_stage'")
def downgrade():op.drop_table("audit_logs")
