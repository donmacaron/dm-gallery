"""add album_media junction table

Revision ID: 20250506_0001
Revises:
Create Date: 2025-05-06
"""
from alembic import op
import sqlalchemy as sa

revision = '20250506_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'album_media',
        sa.Column('album_id',   sa.Integer(), sa.ForeignKey('albums.id',  ondelete='CASCADE'), primary_key=True),
        sa.Column('media_id',   sa.Integer(), sa.ForeignKey('media.id',   ondelete='CASCADE'), primary_key=True),
        sa.Column('sort_order', sa.Integer(), nullable=True, default=0),
        sa.Column('added_at',   sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    # Back-fill: copy existing album_id FK into the junction table
    op.execute("""
        INSERT INTO album_media (album_id, media_id, sort_order)
        SELECT album_id, id, sort_order
        FROM media
        WHERE album_id IS NOT NULL
    """)


def downgrade() -> None:
    op.drop_table('album_media')
