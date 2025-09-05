from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class PackageTypeBase(BaseModel):
    name: str
    description: Optional[str] = None


class PackageTypeCreate(PackageTypeBase):
    pass


class PackageTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class PackageTypeRead(PackageTypeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
