from datetime import datetime

from sqlalchemy.orm import Session

from rupmes.repositories.portal_settings_repository import PortalSettingsRepository


def get_portal_settings(session: Session, tenant_id: str):
    repo = PortalSettingsRepository(session)
    return repo.get_by_tenant(tenant_id)


def save_portal_settings(session: Session, settings):
    repo = PortalSettingsRepository(session)
    settings.update_date = datetime.utcnow()
    if getattr(settings, "id_row", None):
        settings = repo.update_settings(settings)
    else:
        settings = repo.create_settings(settings)
    session.commit()
    session.refresh(settings)
    return settings
