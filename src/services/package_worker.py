import logging
from decimal import Decimal
from uuid import UUID
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError

from src.core.db_settings import db_manager
from src.crud.packages import PackagesCRUD
from src.models.package import Package

logger = logging.getLogger(__name__)


class PackageWorkerService:
    async def update_package_delivery_cost(
        self, package_id: UUID, delivery_cost: Decimal
    ) -> Optional[Package]:
        try:
            async with db_manager.session_factory() as session:
                package = await PackagesCRUD.update_delivery_cost(
                    session, package_id, delivery_cost
                )
                if package:
                    await session.commit()
                    logger.info(
                        "Updated delivery cost for package %s: %s RUB",
                        package_id,
                        delivery_cost,
                    )
                else:
                    logger.warning(
                        "Package %s not found for delivery cost update", package_id
                    )
                return package
        except SQLAlchemyError as e:
            logger.error(
                "Failed to update delivery cost for package %s: %s", package_id, e
            )
            raise RuntimeError(f"Database operation failed: {e}") from e
        except Exception as e:
            logger.error(
                "Unexpected error updating delivery cost for package %s: %s",
                package_id,
                e,
            )
            raise


package_worker_service = PackageWorkerService()
