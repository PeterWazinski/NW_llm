from pydantic import BaseModel, Field
from typing import Optional


class NWnode(BaseModel):
    # Base class for all NW elements
    id: int = 0
    name: str = ""
    type: str = ""
    subnodes: list["NWnode"] = []

    def __post_init__(self):
        if not isinstance(self.id, int) or self.id < 0:
            raise ValueError("id must be a non-negative integer")
        
    def __str__(self):
        return f"({self.id}, '{self.name}', {self.type})"
    
    def __hash__(self):
        return hash(self.id)        
    
    def __eq__(self, other):
        return isinstance(other, NWnode) and self.id == other.id

class NWinstrument(NWnode):
    """
    Class to represent a Netilion Water instrumentation.
    """

    assets: list["NMFasset"] = Field(default_factory=list)
    primary_val_key: Optional[str] = None
    value_keys: list[str] = Field(default_factory=list)
    thresholds: list[dict] = Field(default_factory=list)
    
    @property
    def tag(self) -> str:
        """Return the same value as the name"""
        return self.name

class NMFasset(NWnode):  
    """
    Class to represent a Netilion Water asset.
    """

    @property
    def serial(self) -> str:
        """Return the same value as the name"""
        return self.name
    
    prod_code: str
    prod_name: str



