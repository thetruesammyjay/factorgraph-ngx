from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import Company

def list_companies(session: Session) -> list[Company]:
    return list(session.scalars(select(Company).order_by(Company.ticker)))