"""Title models

Revision ID: 740f1e94dfe9
Revises: 14cee5fc4460
Create Date: 2025-07-08 18:27:04.124520

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '740f1e94dfe9'
down_revision: Union[str, Sequence[str], None] = '14cee5fc4460'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sources', sa.Column('name', sa.String(length=255), nullable=False))
    op.add_column('sources', sa.Column('url', sa.String(length=255), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sources', 'url')
    op.drop_column('sources', 'name')
    # ### end Alembic commands ###
