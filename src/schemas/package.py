from __future__ import annotations

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PackageBase(BaseModel):
    name: str
    type_id: int
    weight: float
    value_of_contents_usd: Decimal


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


class PackageDetailRead(PackageRead):
    type_name: str
    package_delivery_cost_rub: Optional[Decimal] = None


class PaginatedPackages(BaseModel):
    items: list[PackageDetailRead]
    total: int
    page: int
    size: int


class PackageCreateResponse(BaseModel):
    id: UUID
