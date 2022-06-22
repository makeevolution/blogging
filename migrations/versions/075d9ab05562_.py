"""empty message

Revision ID: 075d9ab05562
Revises: 98a6a60f6c4d
Create Date: 2022-06-01 11:01:38.565254

"""
from alembic import op
import sqlalchemy as sa
from config import Config


# revision identifiers, used by Alembic.
revision = '075d9ab05562'
down_revision = '98a6a60f6c4d'
branch_labels = None
depends_on = None

# This migration fixes the issue in the previous migration, where the primary key for following_id was not created
# due to the automigration not working properly. The edits were done manually.
# Please look at documentation of batch_alter_table on how to create your own alter table commands.

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    #with op.batch_alter_table('follows', schema=None, naming_convention=Config.NAMING_CONVENTION) as batch_op:
    #    batch_op.add_column(sa.Column('trigger', sa.Text(), nullable=True))
    #    batch_op.drop_constraint(constraint_name = "pk_follows", type_ = 'primary')
    #    batch_op.create_primary_key(constraint_name = "pk_follows", columns = ["follower_id","following_id"])
    op.create_table('follows',
    sa.Column('follower_id', sa.Integer(), nullable=False),
    sa.Column('following_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('follower_id', 'following_id', name=op.f('pk_follows'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    #with op.batch_alter_table('follows', schema=None, naming_convention=Config.NAMING_CONVENTION) as batch_op:
    #    batch_op.drop_column('trigger')
    #    batch_op.drop_constraint(constraint_name = "pk_follows", type_ = 'primary')
    #    batch_op.create_primary_key(constraint_name = "pk_follows", columns = ["follower_id"])
    op.drop_table('follows')
    # ### end Alembic commands ###
