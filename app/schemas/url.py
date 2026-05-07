from pydantic import BaseModel
from typing import Optional


class URLRequest(BaseModel):

    long_url: str

    custom_alias: Optional[str] = None

    expires_in_hours: Optional[int] = None