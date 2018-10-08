"""add set task and bot instance logging

Revision ID: 19eabf5fe31f
Revises: c90dd14cf037
Create Date: 2018-10-08 19:37:51.352667

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19eabf5fe31f'
down_revision = 'c90dd14cf037'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('inline_search', sa.Column('bot', sa.String(), nullable=True))
    op.add_column('task', sa.Column('chat_id', sa.BigInteger(), nullable=True))
    op.create_index(op.f('ix_task_chat_id'), 'task', ['chat_id'], unique=False)
    op.create_foreign_key(None, 'task', 'chat', ['chat_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'task', type_='foreignkey')
    op.drop_index(op.f('ix_task_chat_id'), table_name='task')
    op.drop_column('task', 'chat_id')
    op.drop_column('inline_search', 'bot')
    # ### end Alembic commands ###
