"""add duration_minutes to charging_sessions

Revision ID: 753814236265
Revises: previous_revision_id
Create Date: 2024-02-27 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = '753814236265'
down_revision: Union[str, None] = None  # Replace with your previous revision ID
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add duration_minutes column
    op.add_column('charging_sessions',
        sa.Column('duration_minutes', sa.Integer(), nullable=False, server_default='30')
    )

def downgrade() -> None:
    # Remove duration_minutes column
    op.drop_column('charging_sessions', 'duration_minutes')