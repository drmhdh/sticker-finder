"""Cascade on chat sticker file id

Revision ID: 9fa624eb51ab
Revises: 5333a07d4ea9
Create Date: 2019-04-04 19:01:02.184006

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '9fa624eb51ab'
down_revision = '5333a07d4ea9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('chat_current_sticker_file_id_fkey', 'chat', type_='foreignkey')
    op.create_foreign_key('chat_current_sticker_file_id_fkey', 'chat', 'sticker', ['current_sticker_file_id'], ['file_id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('chat_current_sticker_file_id_fkey', 'chat', type_='foreignkey')
    op.create_foreign_key('chat_current_sticker_file_id_fkey', 'chat', 'sticker', ['current_sticker_file_id'], ['file_id'])
    # ### end Alembic commands ###
