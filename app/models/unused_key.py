from sqlalchemy import Column, Integer, String
from app.db.database import Base

class UnusedKey(Base):
    __tablename__ = "unused_keys"

    id = Column(Integer, primary_key=True, index=True)
    
    # The pre-computed Base62 string (e.g., '15FT0g')
    key = Column(String(10), unique=True, index=True, nullable=False)