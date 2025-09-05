from typing import TYPE_CHECKING, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from .base import Base
from .annotations import int_pk, str_null_true


if TYPE_CHECKING:
    from .package import Package


class PackageType(Base):
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str_null_true]

    packages: Mapped[List["Package"]] = relationship(back_populates="type")
