from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[Dict[str, Any]] | List[str]] = None

class IssueModel(BaseModel):
    type: str
    field: str
    severity: str
    affectedCount: int
    suggestedFix: Optional[str] = None

class RepairOptions(BaseModel):
    fixMissing: bool = True
    removeDuplicates: bool = True
    fixFormats: bool = True
    fixOutliers: bool = False

class RepairRequest(BaseModel):
    repairOptions: Optional[RepairOptions] = Field(default_factory=RepairOptions)

class RepairLogEntry(BaseModel):
    action: str
    field: Optional[str] = None
    rowIndex: Optional[int] = None
    value: Optional[Any] = None
