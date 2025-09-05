"""Insert types

Revision ID: b3b68d68bce8
Revises: b273aa443897
Create Date: 2025-09-05 12:38:57.582493

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b3b68d68bce8"
down_revision: Union[str, Sequence[str], None] = "b273aa443897"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        INSERT INTO packagetypes (name, description)
        VALUES ('одежда', NULL), ('электроника', NULL), ('разное', NULL)
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DELETE FROM packagetypes
        WHERE name IN ('одежда', 'электроника', 'разное')
        """
    )
