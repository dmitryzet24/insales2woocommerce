from pydantic import BaseModel, Field
from typing import List, Optional

class InsalesVariant(BaseModel):
    id: int
    product_id: int
    sku: Optional[str] = Field(default_None, description="Product SKU")
    price: