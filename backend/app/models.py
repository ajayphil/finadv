from pydantic import BaseModel
from typing import List, Optional

class DebtItem(BaseModel):
    name: str
    balance: float
    rate: Optional[float]
    min_payment: Optional[float]

class UserFinancials(BaseModel):
    income: float
    recurring_spending: float
    discretionary_spending: Optional[float] = 0
    debts: List[DebtItem] = []
    savings: Optional[float] = 0

class AnalysisRequest(BaseModel):
    user: UserFinancials
    doc_ids: Optional[List[str]] = None

class AnalysisResponse(BaseModel):
    summary: str
    details: Optional[dict] = None
