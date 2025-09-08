from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.package_types import PackageType


class PackageTypesCRUD:
    @staticmethod
    async def get_all(session: AsyncSession) -> Sequence[PackageType]:
        stmt = select(PackageType).order_by(PackageType.id.asc())
        result = await session.execute(stmt)
        return result.scalars().all()
