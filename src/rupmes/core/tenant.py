from fastapi import HTTPException, Request, status

from .config import get_default_tenant_id, is_multi_tenant_enabled


def resolve_tenant_id(request: Request) -> str:
    if not is_multi_tenant_enabled():
        return get_default_tenant_id()

    tenant_id = request.headers.get("X-Tenant-ID")
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-ID header is required",
        )
    return tenant_id.strip()
