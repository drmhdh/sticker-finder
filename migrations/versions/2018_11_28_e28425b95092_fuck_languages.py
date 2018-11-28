"""Fuck languages

Revision ID: e28425b95092
Revises: fd5458abc68a
Create Date: 2018-11-28 23:31:40.641853

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

import os
import sys
from sqlalchemy.orm.session import Session
# Set system path, so alembic is capable of finding the stickerfinder module
parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", "stickerfinder"))
sys.path.append(parent_dir)

from stickerfinder.models import Change, Task, Tag, User, StickerSet # noqa

# revision identifiers, used by Alembic.
revision = 'e28425b95092'
down_revision = 'fd5458abc68a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('language')
    op.add_column('change', sa.Column('reviewed', sa.Boolean(), nullable=False, server_default='False'))
    op.alter_column('change', 'reviewed', server_default=None)

    op.add_column('change', sa.Column('default_language', sa.Boolean(), nullable=False, server_default='True'))
    op.add_column('sticker_set', sa.Column('default_language', sa.Boolean(), nullable=False, server_default='True'))
    op.add_column('tag', sa.Column('default_language', sa.Boolean(), nullable=False, server_default='True'))
    op.add_column('user', sa.Column('default_language', sa.Boolean(), nullable=False, server_default='True'))

    op.alter_column('change', 'default_language', server_default=None)
    op.alter_column('sticker_set', 'default_language', server_default=None)
    op.alter_column('tag', 'default_language', server_default=None)
    op.alter_column('user', 'default_language', server_default=None)

    op.drop_index('ix_change_language', table_name='change')
    op.drop_constraint('change_language_fkey', 'change', type_='foreignkey')
    op.drop_index('ix_sticker_set_language', table_name='sticker_set')
    op.drop_constraint('sticker_set_language_fkey', 'sticker_set', type_='foreignkey')
    op.drop_index('ix_tag_language', table_name='tag')
    op.drop_constraint('tag_language_fkey', 'tag', type_='foreignkey')
    op.drop_index('ix_user_language', table_name='user')
    op.drop_constraint('user_language_fkey', 'user', type_='foreignkey')

    session = Session(bind=op.get_bind())

    # Set all changes to reviewed, where an task exists
    session.query(Change) \
        .filter(Change.language != 'english') \
        .join(Change.check_task) \
        .join(Task.user) \
        .filter(Task.reviewed.is_(True))  \
        .filter(User.banned.is_(False))  \
        .update({'reviewed': True})

    # Set all entities to default_language = False, where the language is not english
    session.query(Change) \
        .filter(Change.language != 'english') \
        .update({'default_language': False})

    session.query(StickerSet) \
        .filter(StickerSet.language != 'english') \
        .update({'default_language': False})

    session.query(Tag) \
        .filter(User.language != 'english') \
        .update({'default_language': False})

    session.query(User) \
        .filter(User.language != 'english') \
        .update({'default_language': False})


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
