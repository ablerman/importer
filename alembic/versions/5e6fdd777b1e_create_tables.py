"""create tables

Revision ID: 5e6fdd777b1e
Revises: 
Create Date: 2020-03-20 11:20:37.085584

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e6fdd777b1e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'census',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('path', sa.Text, unique=True, nullable=False),
        sa.Column('created_at', sa.DateTime),
    )
    op.create_table(
        'raw_member',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('census_id', sa.BigInteger, sa.ForeignKey('census.id'), nullable=False),
        sa.Column('unique_key', sa.Text, nullable=False),
        sa.Column('data', sa.JSON),
    )
    op.create_index('raw_member_census_key_uq', 'raw_member', ('census_id', 'unique_key', ), unique=True)

    event_type_table = op.create_table(
        'event_type',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('description', sa.Text),
    )
    op.bulk_insert(
        event_type_table,
        [
            dict(name='CREATE_MEMBER', description='Create a new member.'),
            dict(name='DEACTIVATE_MEMBER', description='Deactivate an existing member'),
        ],
        multiinsert=False,
    )
    op.create_table(
        'member',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('unique_key', sa.Text, unique=True, nullable=False),
        sa.Column('first_name', sa.Text),
        sa.Column('last_name', sa.Text),
        sa.Column('ssn', sa.Text),
        sa.Column('deactivated_at', sa.DateTime),
    )
    op.create_table(
        'event',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('event_type_id', sa.BigInteger, sa.ForeignKey('event_type.id'), nullable=False),
        sa.Column('census_id', sa.BigInteger, sa.ForeignKey('census.id'), nullable=False),
        sa.Column('unique_key', sa.Text, nullable=False),
        sa.Column('applied_at', sa.DateTime),
        sa.Column('data', sa.JSON),
    )



def downgrade():
    op.drop_table('event')
    op.drop_table('member')
    op.drop_table('event_type')
    op.drop_table('raw_member')
    op.drop_table('census')
