from __future__ import annotations

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PackageBase(BaseModel):
    name: str
    type_id: int
    weight: float
    value_of_contents_usd: Optional[Decimal] = None
    package_delivery_cost_rub: Optional[Decimal] = None


class PackageCreate(PackageBase):
    pass


class PackageUpdate(BaseModel):
    name: Optional[str] = None
    type_id: Optional[int] = None
    weight: Optional[float] = None
    value_of_contents_usd: Optional[Decimal] = None
    package_delivery_cost_rub: Optional[Decimal] = None


class PackageRead(PackageBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
