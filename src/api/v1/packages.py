import uuid
import fastapi

from src.schemas import package as package_schemas
from src.services.packages import package_service as service


router = fastapi.APIRouter(prefix="/packages", tags=["packages"])


def _ensure_session_cookie(
    request: fastapi.Request, response: fastapi.Response
) -> uuid.UUID:
    sid = request.cookies.get("session_id")
    if sid:
        try:
            return uuid.UUID(sid)
        except Exception:
            pass
    new_sid = uuid.uuid4()
    response.set_cookie(
        key="session_id",
        value=str(new_sid),
        httponly=True,
        samesite="lax",
    )
    return new_sid


@router.post(
    "",
    name="packages:create",
    response_model=package_schemas.PackageCreateResponse,
    status_code=fastapi.status.HTTP_201_CREATED,
)
async def create_package(
    request: fastapi.Request,
    response: fastapi.Response,
    package_data: package_schemas.PackageCreate,
) -> package_schemas.PackageCreateResponse:
    session_uid = _ensure_session_cookie(request, response)
    return await service.register_package(session_uid=session_uid, data=package_data)


@router.get(
    "",
    name="packages:list",
    response_model=package_schemas.PaginatedPackages,
)
async def list_packages(
    request: fastapi.Request,
    response: fastapi.Response,
    page: int = fastapi.Query(1, ge=1),
    size: int = fastapi.Query(20, ge=1, le=100),
    type_id: int | None = fastapi.Query(None),
    has_delivery_cost: bool | None = fastapi.Query(None),
) -> package_schemas.PaginatedPackages:
    session_uid = _ensure_session_cookie(request, response)
    return await service.list_packages(
        session_uid=session_uid,
        type_id=type_id,
        has_delivery_cost=has_delivery_cost,
        page=page,
        size=size,
    )


@router.get(
    "/{package_id}",
    name="packages:get",
    response_model=package_schemas.PackageDetailRead,
)
async def get_package(
    package_id: uuid.UUID,
    request: fastapi.Request,
    response: fastapi.Response,
) -> package_schemas.PackageDetailRead:
    session_uid = _ensure_session_cookie(request, response)
    return await service.get_package_by_id(
        session_uid=session_uid, package_id=package_id
    )
