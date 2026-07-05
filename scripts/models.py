from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

# Modification Model of SCU from Insales
class InsalesVariant(BaseModel):
    id: int
    product_id: int
    sku: Optional[str] = Field(default=None, description="Product SKU")
    price: float  = Field(description="Sell price")
    old_price: Optional[float] = Field(default=None, description="Old price (before discount)")
    quantity: int = Field(default=0, description="Whats left in the Wharehouse")
    weight: Optional[float] = Field(default=None, description=" Product weight")

    @field_validator('old_price', mode='before')
    @classmethod
    def prevent_none_prices(cls, v):
        return 0.0 if v is None else v

#Product Model of SCU from Insales
class InSalesProduct(BaseModel):
    id: int
    title: str = Field(description="Product Name")
    category_id: int = Field(description="Main Proguc Category ID")
    short_description: Optional[str] = Field(default=None, description="Short description")
    description: Optional[str] = Field(default=None, description="Full description")
    variants: List[InsalesVariant] = Field(default=[], description="List of Product modifications")

    images: List[dict] = Field(default=[], description="Raw list of product images")

    # URL helper
    @property
    def main_image_url(self) -> Optional[str]:
        if self.images and 'original_url' in self.images[0]:
            return self.images[0]['original_url']
        return None

