"""Add is_public column to rooms table

Revision ID: 001_add_room_is_public
Revises: 
Create Date: 2026-03-03

Adds a boolean `is_public` flag to rooms.
Existing rooms default to True (public) to preserve current behaviour.
Private rooms (is_public=False) are only visible to their creator and
users with an explicit RoomPermission row.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_add_room_is_public'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_public column — server_default='1' keeps existing rows public
    op.add_column(
        'rooms',
        sa.Column(
            'is_public',
            sa.Boolean(),
            nullable=False,
            server_default=sa.true()   # all existing rooms stay public
        )
    )
    # Add index for fast filtering in list endpoints
    op.create_index(
        op.f('ix_rooms_is_public'),
        'rooms',
        ['is_public'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_rooms_is_public'), table_name='rooms')
    op.drop_column('rooms', 'is_public')
