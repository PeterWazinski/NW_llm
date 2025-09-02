from pydantic import BaseModel, Field
from typing import Optional

class nw_node(BaseModel):
    # Base class for all NW elements
    id: int = 0
    name: str = ""
    type: str = ""
    subnodes: list["nw_node"] = Field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.id, int) or self.id < 0:
            raise ValueError("id must be a non-negative integer")
        
    def __str__(self):
        return f"({self.id}, '{self.name}', {self.type})"
    
    def __hash__(self):
        return hash(self.id)        
    
    def __eq__(self, other):
        return isinstance(other, nw_node) and self.id == other.id

class nw_instrument(nw_node):
    """
    Class to represent a Netilion Water instrumentation.
    """

    primary_val_key: Optional[str] = None
    value_keys: list[str] = Field(default_factory=list)
    thresholds: list[dict] = Field(default_factory=list)
    
    @property
    def tag(self) -> str:
        """Return the same value as the name"""
        return self.name

    @property
    def assets(self) -> list["nw_asset"]:
        """Return the list of assets"""
        return self.subnodes

class nw_asset(nw_node):  
    """
    Class to represent a Netilion Water asset.
    """

    prod_code: str
    prod_name: str

    @property
    def serial(self) -> str:
        """Return the same value as the name"""
        return self.name
    
###############################


from Guwahati import nodeinfo, instrumentation_asset_info
inst_info, asset_info = instrumentation_asset_info

def NW_hierarchy_from_Guwahati(n_info, i_info, a_info):

    # Create nw_node instances for each node in nodeinfo
    nodes = {}
    for node_id, info in n_info.items():
        node = nw_node(id=node_id, name=info['name'], type=info['type'])
        nodes[node_id] = node

    # Create nw_instrument instances for each instrumentation
    for inst_id, info in i_info.items():
        inst = nw_instrument(id=inst_id, name=info['tag'], type=info['type'],
                            value_keys=info['value_keys'],
                            primary_val_key=info['specifications'],
                            thresholds=info['thresholds'])

        nodes[inst_id] = inst

        assets = info.get('assets', [])
        for asset_attribs in assets:
            asset = nw_asset(id=asset_attribs["id"], name=asset_attribs['serial'], type="asset",
                       prod_code=asset_attribs['prod_code'], prod_name=asset_attribs['product_name'])
            nodes[asset_attribs["id"]] = asset

            #print(f"{inst_id} has asset {asset_attribs['id']}")
            nodes[inst_id].subnodes.append(nodes[asset_attribs["id"]])

    # Build the hierarchy from nodeinfo
    for node_id, info in nodeinfo.items():
        parent_id = info['parent_id']
        if parent_id in nodes:
            #print(f"{parent_id} has child {node_id}")
            nodes[parent_id].subnodes.append(nodes[node_id])

    # Add instruments to their parent modules based on the 'instrumentations' list
    for node_id, info in nodeinfo.items():
        for i_id in info.get('instrumentations', []):
            if i_id in nodes:
                #print(f"{node_id} has instrument {i_id}"   )
                nodes[node_id].subnodes.append(nodes[i_id])

    # there can be multiple root nodes
    roots = [node for node in nodes.values() if node.type == "location"]
    return roots