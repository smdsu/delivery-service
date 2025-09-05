import logging
import uuid
from typing import Optional

from fastapi import HTTPException, status

from src.core.db_settings import get_session
from src.crud.packages import PackagesCRUD
from src.schemas.package import (
    PackageCreate,
    PackageCreateResponse,
    PackageDetailRead,
    PaginatedPackages,
)
from src.models.package import Package


logger = logging.getLogger(__name__)


class PackageService:
    async def register_package(
        self, *, session_uid: uuid.UUID, data: PackageCreate
    ) -> PackageCreateResponse:
        # Note: In production we would publish to RabbitMQ here instead of direct DB writes
        logger.info("Registering package for session %s", session_uid)
        new_package = Package(
            id=uuid.uuid4(),
            name=data.name,
            type_id=data.type_id,
            weight=data.weight,
            value_of_contents_usd=data.value_of_contents_usd,
            package_delivery_cost_rub=None,
            user_session_uid=session_uid,
        )

        async for session in get_session():
            await PackagesCRUD.create(session, new_package)
            await session.commit()

        return PackageCreateResponse(id=new_package.id)

    async def get_package_by_id(
        self, *, session_uid: uuid.UUID, package_id: uuid.UUID
    ) -> PackageDetailRead:
        async for session in get_session():
            pkg = await PackagesCRUD.get_by_id_for_session(
                session, package_id, session_uid
            )
        if pkg is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Package not found"
            )
        return PackageDetailRead(
            id=pkg.id,
            name=pkg.name,
            type_id=pkg.type_id,
            type_name=pkg.type.name if pkg.type else "",
            weight=pkg.weight,
            value_of_contents_usd=pkg.value_of_contents_usd,
            package_delivery_cost_rub=pkg.package_delivery_cost_rub,
        )

    async def list_packages(
        self,
        *,
        session_uid: uuid.UUID,
        type_id: Optional[int],
        has_delivery_cost: Optional[bool],
        page: int,
        size: int,
    ) -> PaginatedPackages:
        async for session in get_session():
            rows, total = await PackagesCRUD.list_for_session(
                session,
                session_uid,
                type_id=type_id,
                has_delivery_cost=has_delivery_cost,
                page=page,
                size=size,
            )

        items = [
            PackageDetailRead(
                id=p.id,
                name=p.name,
                type_id=p.type_id,
                type_name=t.name,
                weight=p.weight,
                value_of_contents_usd=p.value_of_contents_usd,
                package_delivery_cost_rub=p.package_delivery_cost_rub,
            )
            for p, t in rows
        ]
        return PaginatedPackages(items=items, total=total, page=page, size=size)


package_service = PackageService()
