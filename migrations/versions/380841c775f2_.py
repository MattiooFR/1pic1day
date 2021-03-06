"""empty message

Revision ID: 380841c775f2
Revises: 
Create Date: 2020-07-02 19:02:18.870906

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '380841c775f2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('album',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('url', sa.String(length=500), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.String(length=50), nullable=True),
    sa.Column('last_time_viewed', sa.DateTime(), nullable=True),
    sa.Column('last_photo_viewed', sa.String(length=300), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_album_name'), 'album', ['name'], unique=False)
    op.create_index(op.f('ix_album_timestamp'), 'album', ['timestamp'], unique=False)
    op.create_table('image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(length=300), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('viewed', sa.Boolean(), nullable=True),
    sa.Column('album_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['album_id'], ['album.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_image_timestamp'), 'image', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_image_timestamp'), table_name='image')
    op.drop_table('image')
    op.drop_index(op.f('ix_album_timestamp'), table_name='album')
    op.drop_index(op.f('ix_album_name'), table_name='album')
    op.drop_table('album')
    # ### end Alembic commands ###
