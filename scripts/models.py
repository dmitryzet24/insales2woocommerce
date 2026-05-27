from pydantic import BaseModel, Field
from typing import List, Optional

class InsalesVariant(BaseModel):
    id: int
    product_id: int
    sku: Optional[str] = Field(default_None, description="Product SKU")
    price: float  = Field(description="Цена продажи")
    old_price: Optional[float] = Field(default=None, descrition="Старая цена (без скидки)")
    quantity: int = Field(default=0, description="Остаток на складе")
    weight: Oprional[float] = Field(default=None, description=" Вест товара")

