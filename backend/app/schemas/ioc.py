from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime


class IOCCreate(BaseModel):
    ioc_type: str  # ip, domain, url, hash, file, user
    value: str
    confidence: float = 0.9
    classification: str = "suspicious"  # malicious, suspicious, benign, scanner
    source: str = "local-threat-intel"
    metadata: Optional[Dict[str, Any]] = None


class IOCLookupRequest(BaseModel):
    values: List[str]


class IOCMatch(BaseModel):
    matched: bool
    ioc_id: Optional[str] = None
    ioc_type: Optional[str] = None
    value: str
    confidence: float = 0.0
    classification: Optional[str] = None
    source: Optional[str] = None


class IOCResponse(BaseModel):
    id: str
    ioc_type: str
    value: str
    confidence: float
    classification: str
    source: str
    first_seen: datetime
    last_seen: datetime
    metadata_json: Dict[str, Any]
