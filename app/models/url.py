from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.db.database import Base

class URLMapping(Base):
    __tablename__ = "url_mappings"

    id = Column(Integer, primary_key=True, index=True)
    
    # The short alias (e.g., '15FT0g')
    short_url = Column(String(50), unique=True, index=True, nullable=False)
    
    # The destination URL
    original_url = Column(String(2048), nullable=False)
    
    # When it was created
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    # NEW: When it expires (nullable because some links might be permanent)
    expires_at = Column(DateTime(timezone=True), nullable=True)