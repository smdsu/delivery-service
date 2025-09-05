from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.package import Package
from src.models.package_types import PackageType


class PackagesCRUD:
    @staticmethod
    async def create(session: AsyncSession, package: Package) -> Package:
        session.add(package)
        await session.flush()
        return package

    @staticmethod
    async def get_by_id_for_session(
        session: AsyncSession, package_id: UUID, session_uid: UUID
    ) -> Optional[Package]:
        stmt = (
            select(Package)
            .where(
                and_(Package.id == package_id, Package.user_session_uid == session_uid)
            )
            .options()
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_for_session(
        session: AsyncSession,
        session_uid: UUID,
        *,
        type_id: Optional[int] = None,
        has_delivery_cost: Optional[bool] = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[Sequence[tuple[Package, PackageType]], int]:
        filters = [Package.user_session_uid == session_uid]
        if type_id is not None:
            filters.append(Package.type_id == type_id)
        if has_delivery_cost is True:
            filters.append(Package.package_delivery_cost_rub.is_not(None))
        elif has_delivery_cost is False:
            filters.append(Package.package_delivery_cost_rub.is_(None))

        base_stmt: Select = (
            select(Package, PackageType)
            .join(PackageType, Package.type_id == PackageType.id)
            .where(and_(*filters))
            .order_by(Package.created_at.desc())
        )

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = (await session.execute(count_stmt)).scalar_one()

        stmt = base_stmt.offset((page - 1) * size).limit(size)
        result = await session.execute(stmt)
        fetched = result.all()
        rows: list[tuple[Package, PackageType]] = [(row[0], row[1]) for row in fetched]
        return rows, int(total)
