"""init schema

Revision ID: 20250828_230926
Revises: 
Create Date: 2025-08-28 23:09:26
"""

from alembic import op
import sqlalchemy as sa

revision = "20250828_230926"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('videos',
        sa.Column('id', sa.Text, primary_key=True),
        sa.Column('source_url', sa.Text, nullable=False),
        sa.Column('preview_url', sa.Text),
        sa.Column('duration_ms', sa.Integer),
        sa.Column('fps', sa.Float),
        sa.Column('width', sa.Integer),
        sa.Column('height', sa.Integer),
        sa.Column('status', sa.Text, server_default='NEW'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'))
    )
    op.create_table('analysis_jobs',
        sa.Column('id', sa.Text, primary_key=True),
        sa.Column('video_id', sa.Text, sa.ForeignKey('videos.id', ondelete='CASCADE')),
        sa.Column('model_version', sa.Text),
        sa.Column('state', sa.Text),
        sa.Column('log', sa.JSON, server_default='[]'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'))
    )
    op.create_table('segments',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('video_id', sa.Text, sa.ForeignKey('videos.id', ondelete='CASCADE')),
        sa.Column('start_ms', sa.Integer, nullable=False),
        sa.Column('end_ms', sa.Integer, nullable=False),
        sa.Column('move_id', sa.Text, nullable=False),
        sa.Column('confidence', sa.Float),
        sa.Column('mirror', sa.Boolean, server_default=sa.text('false')),
        sa.Column('alts', sa.JSON, server_default='[]'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'))
    )

def downgrade():
    op.drop_table('segments')
    op.drop_table('analysis_jobs')
    op.drop_table('videos')
