from sqlalchemy import select

from rupmes.models import TbPortalSettings
from .base import BaseRepository


class PortalSettingsRepository(BaseRepository):
    def get_by_tenant(self, tenant_id: str) -> TbPortalSettings | None:
        stmt = select(TbPortalSettings).where(TbPortalSettings.tenant_id == tenant_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_settings(self, settings: TbPortalSettings) -> TbPortalSettings:
        self.session.add(settings)
        return settings

    def update_settings(self, settings: TbPortalSettings) -> TbPortalSettings:
        self.session.add(settings)
        return settings
