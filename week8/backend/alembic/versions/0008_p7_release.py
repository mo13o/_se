"""P7 release marker."""
from alembic import op
revision="0008_p7_release";down_revision="0007_p6_reports_audit";branch_labels=None;depends_on=None
def upgrade():op.execute("UPDATE system_metadata SET value='P7' WHERE key='schema_stage'")
def downgrade():op.execute("UPDATE system_metadata SET value='P6' WHERE key='schema_stage'")
