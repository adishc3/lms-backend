from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PaymentCreate(BaseModel):
    payment_method: Optional[str] = None
    currency: str = "USD"


class PaymentRead(BaseModel):
    id: int
    user_id: int
    course_id: int
    amount: int
    currency: str
    status: str
    payment_method: Optional[str] = None
    transaction_reference: Optional[str] = None
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }
