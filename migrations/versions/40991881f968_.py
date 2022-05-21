"""empty message

Revision ID: 40991881f968
Revises: c309ed781715
Create Date: 2022-05-21 15:37:19.800664

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '40991881f968'
down_revision = 'c309ed781715'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('roles', sa.Column('default', sa.Boolean(), nullable=True))
    op.add_column('roles', sa.Column('permissions', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_roles_default'), 'roles', ['default'], unique=False)
    op.drop_column('roles', 'test')
    op.add_column('users', sa.Column('email', sa.String(length=64), nullable=True))
    op.add_column('users', sa.Column('password_hash', sa.String(length=128), nullable=True))
    op.add_column('users', sa.Column('confirmed', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_column('users', 'confirmed')
    op.drop_column('users', 'password_hash')
    op.drop_column('users', 'email')
    op.add_column('roles', sa.Column('test', sa.VARCHAR(length=64), nullable=True))
    op.drop_index(op.f('ix_roles_default'), table_name='roles')
    op.drop_column('roles', 'permissions')
    op.drop_column('roles', 'default')
    # ### end Alembic commands ###
