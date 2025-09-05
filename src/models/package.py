from decimal import Decimal
from typing import TYPE_CHECKING
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy import String, Float, ForeignKey, DECIMAL

from .base import Base


if TYPE_CHECKING:
    from .package_types import PackageType


class Package(Base):
    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("packagetypes.id"))
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    value_of_contents_usd: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    package_delivery_cost_rub: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    user_session_uid: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), default=uuid.uuid4
    )

    type: Mapped["PackageType"] = relationship(back_populates="packages")
