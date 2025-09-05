import logging
from typing import List

from src.core.db_settings import get_session
from src.crud.package_types import PackageTypesCRUD
from src.schemas.packagetypes import PackageTypeRead


logger = logging.getLogger(__name__)


class PackageTypeService:
    async def get_all_types(self) -> List[PackageTypeRead]:
        logger.info("Listing package types")
        async for session in get_session():
            rows = await PackageTypesCRUD.get_all(session)
        return [PackageTypeRead.model_validate(row) for row in rows]


package_type_service = PackageTypeService()
