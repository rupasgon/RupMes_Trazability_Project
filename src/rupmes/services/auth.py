from datetime import datetime, timedelta
import secrets

from sqlalchemy.orm import Session

from rupmes.controllers.sessions_controller import create_session, delete_session, get_session, update_last_seen
from rupmes.models import TbSessions, TbUsers
from rupmes.services.security import verify_password
from rupmes.core.config import get_session_ttl_minutes


def authenticate_user(session: Session, user: TbUsers, password: str) -> bool:
    return verify_password(password, user.pass_hash)


def create_user_session(
    session: Session,
    id_user: str,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> TbSessions:
    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=get_session_ttl_minutes())
    session_row = TbSessions(
        session_id=secrets.token_urlsafe(32),
        id_user=id_user,
        csrf_token=secrets.token_urlsafe(32),
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return create_session(session, session_row)


def get_valid_session(session: Session, session_id: str) -> TbSessions | None:
    row = get_session(session, session_id)
    if not row:
        return None
    now = datetime.utcnow()
    if row.expires_at <= now:
        delete_session(session, row)
        return None
    update_last_seen(session, row, now)
    return row
