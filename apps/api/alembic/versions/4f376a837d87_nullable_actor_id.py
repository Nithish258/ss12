"""nullable_actor_id

Revision ID: 4f376a837d87
Revises: 5daeec5e8ebe
Create Date: 2026-03-20 18:49:28.358907

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f376a837d87'
down_revision: Union[str, Sequence[str], None] = '5daeec5e8ebe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    op.alter_column('audit_logs', 'actor_id', existing_type=postgresql.UUID(as_uuid=True), nullable=True)

def downgrade() -> None:
    op.alter_column('audit_logs', 'actor_id', existing_type=postgresql.UUID(as_uuid=True), nullable=False)
