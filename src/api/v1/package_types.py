import fastapi

from src.schemas import packagetypes as packagetypes_schemas
from src.services.package_types import package_type_service as service


router = fastapi.APIRouter(prefix="/package_types", tags=["package_types"])


@router.get(
    "",
    name="package_types:list",
    response_model=list[packagetypes_schemas.PackageTypeRead],
)
async def list_package_types() -> list[packagetypes_schemas.PackageTypeRead]:
    types = await service.get_all_types()
    return types
