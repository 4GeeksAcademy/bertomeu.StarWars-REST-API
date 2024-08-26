"""empty message

Revision ID: 90885827fd55
Revises: 70ff9c6a8b27
Create Date: 2024-08-23 19:22:20.372816

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90885827fd55'
down_revision = '70ff9c6a8b27'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('character', schema=None) as batch_op:
        batch_op.drop_constraint('character_planet_id_fkey', type_='foreignkey')
        batch_op.drop_column('planet_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('character', schema=None) as batch_op:
        batch_op.add_column(sa.Column('planet_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('character_planet_id_fkey', 'planet', ['planet_id'], ['planet_id'])

    # ### end Alembic commands ###