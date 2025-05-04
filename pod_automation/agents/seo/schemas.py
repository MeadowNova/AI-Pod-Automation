from pydantic import BaseModel
from typing import List, Union, Optional

class ListingInput(BaseModel):
    title: str
    description: Optional[str] = ""
    tags: Union[str, List[str]] = ""
    product_type: str = "tshirt"

class ListingOutput(BaseModel):
    title: str
    description: str
    tags: List[str]
    base_keyword: str
    product_type: str
    timestamp: str
