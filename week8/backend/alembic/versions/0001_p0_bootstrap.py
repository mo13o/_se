"""P0 database bootstrap."""
from alembic import op
import sqlalchemy as sa
revision="0001_p0"; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
    op.create_table("system_metadata",sa.Column("key",sa.String(100),primary_key=True),sa.Column("value",sa.String(500),nullable=False))
    op.execute("INSERT INTO system_metadata (key,value) VALUES ('schema_stage','P0')")
def downgrade(): op.drop_table("system_metadata")
