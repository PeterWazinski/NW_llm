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

    prod_name: str

    @property
    def serial(self) -> str:
        """Return the same value as the name"""
        return self.name
    
    @property
    def prod_code(self) -> str:
        """Return the same value as the type"""
        return self.type

###############################



class nw_hierarchy:

    """Class to represent the hierarchy of Netilion Water components.
    - retrieve all locations, applications, modules, instrumentations, assets in total via all_locations, all_applications, all_modules, all_instrumentations, all_assets
    - retrieve locations, applications, modules, instrumentations for each parent element , assets via get_locations(), get_applications(location), get_modules(water_app), get_instrumentations(module), get_assets(instrumentation)
    - pretty print or show the entire hierarchy with emojis and indentation via pprint()
    """
    
    application_types = ['water_abstraction', 'water_distribution', 'effluent_discharge']
    module_types = ['source_module', 'disinfection_module', 'storage_module', 'outlet_module', "inlet_module", "transfer_module","quality_control_module"]

    def __init__(self, node_info, instrumentation_info):
        self.nodes = {} # to be set by nw_hierarchy_from_node_instrumentation
        self.root = self.nw_hierarchy_from_node_instrumentation(node_info, instrumentation_info)
        self.all_locations = []
        self.all_applications = []
        self.all_modules = []
        self.all_instrumentations = []
        self.all_assets = []
        self.__post_init__()
    
    def __post_init__(self):
        """
        Post-initialization method that traverses the entire hierarchy 
        and populates lists for all different node types.
        """
        self._traverse_and_categorize(self.root)
    
    def _traverse_and_categorize(self, node: nw_node):
        """
        Recursively traverse the hierarchy and categorize nodes into appropriate lists.
        
        Args:
            node: The current node to process
        """
        # Categorize based on actual class type
        if isinstance(node, nw_instrument):
            self.all_instrumentations.append(node)
        elif isinstance(node, nw_asset):
            self.all_assets.append(node)
        else:
            # This is a regular nw_node - categorize by type
            if node.type == 'location':
                self.all_locations.append(node)
            elif node.type in self.application_types:
                self.all_applications.append(node)
            elif node.type in self.module_types:
                self.all_modules.append(node)
        
        # Recursively process all subnodes
        if hasattr(node, 'subnodes') and node.subnodes:
            for subnode in node.subnodes:
                self._traverse_and_categorize(subnode)
    
    def get_node_counts(self):
        """
        Return a dictionary with counts of all node types.
        
        Returns:
            dict: Dictionary with counts for each node type
        """
        return {
            'locations': len(self.all_locations),
            'applications': len(self.all_applications),
            'modules': len(self.all_modules),
            'instrumentations': len(self.all_instrumentations),
            'assets': len(self.all_assets),
            'total': len(self.all_locations) + len(self.all_applications) + 
                    len(self.all_modules) + len(self.all_instrumentations) + len(self.all_assets)
        }
    
    def print_summary(self):
        """Return a summary of the hierarchy with node counts as a string."""
        counts = self.get_node_counts()
        lines = []
        lines.append("=" * 50)
        lines.append("📊 NW HIERARCHY SUMMARY")
        lines.append("=" * 50)
        lines.append(f"🏢 Locations:        {counts['locations']:3d}")
        lines.append(f"💧 Applications:     {counts['applications']:3d}")
        lines.append(f"📦 Modules:          {counts['modules']:3d}")
        lines.append(f"🔧 Instrumentations: {counts['instrumentations']:3d}")
        lines.append(f"📦 Assets:           {counts['assets']:3d}")
        lines.append("-" * 50)
        lines.append(f"📋 Total Nodes:      {counts['total']:3d}")
        lines.append("=" * 50)
        return "\n".join(lines)

    def print_md_summary(self):
        """Return a summary of the hierarchy with node counts in markdown format."""
        counts = self.get_node_counts()
        lines = []
        lines.append("# 📊 NW Hierarchy Summary")
        lines.append("")
        lines.append("| Component Type | Count |")
        lines.append("|---------------|-------|")
        lines.append(f"| 🏢 Locations | {counts['locations']} |")
        lines.append(f"| 💧 Applications | {counts['applications']} |")
        lines.append(f"| 📦 Modules | {counts['modules']} |")
        lines.append(f"| 🔧 Instrumentations | {counts['instrumentations']} |")
        lines.append(f"| 📦 Assets | {counts['assets']} |")
        lines.append(f"| **📋 Total Nodes** | **{counts['total']}** |")
        lines.append("")
        return "\n".join(lines)


    def get_applications(self, location):
        """Return all nw_node objects with type == 'water_application'."""
        return location.subnodes
    
    def get_modules(self, water_app):
        """Return all Module objects for WATER APP."""
        return water_app.subnodes 
    
    def get_instrumentations(self, module):
        """Return all nw_instrumentation objects for a given module."""
        return module.subnodes

    def get_assets(self, instrumentation):
        """Return all nw_asset objects for a given instrumentation."""
        return instrumentation.subnodes

    def get_asset_by_serial(self, serial):
        """Return nw_asset object by serial number."""
        for asset in self.all_assets:
            if asset.serial == serial:
                return asset
        return None

    def pprint(self, show_summary=True):
        """
        Return a pretty-printed string of the entire hierarchy with emojis and indentation.
        
        Args:
            show_summary (bool): Whether to include the summary at the end
            
        Returns:
            str: Pretty-printed hierarchy as a string
        """
        lines = []
        lines.append("=== NW Hierarchy Pretty Print ===")
        hierarchy_lines = self._pprint_node(self.root, level=0)
        lines.extend(hierarchy_lines)
        
        if show_summary:
            lines.append("")
            lines.append(self.print_summary())
            
        return "\n".join(lines)

    def pprint_md(self, show_summary=True):
        """
        Return a pretty-printed string of the entire hierarchy in markdown format.
        
        Args:
            show_summary (bool): Whether to include the summary at the end
            
        Returns:
            str: Pretty-printed hierarchy in markdown format
        """
        lines = []
        lines.append("# 🏗️ NW Hierarchy Structure")
        lines.append("")
        hierarchy_lines = self._pprint_node_md(self.root, level=0)
        lines.extend(hierarchy_lines)
        
        if show_summary:
            lines.append("")
            lines.append(self.print_md_summary())
            
        return "\n".join(lines)
    
    def _pprint_node(self, node, level=0):
        """
        Recursively format a node and its subnodes with appropriate formatting.
        
        Args:
            node: The node to format
            level (int): The indentation level
            
        Returns:
            list: List of formatted lines
        """
        lines = []
        
        # Emoji mapping for different node types
        emoji_map = {
            'NW_root': '📍',
            'location': '🏢',
            'water_abstraction': '💧',
            'water_distribution': '🚰',
            'effluent_discharge': '🌊',
            'source_module': '🏔️',
            'disinfection_module': '🧽',
            'storage_module': '🏪',
            'outlet_module': '🚪',
            'asset': '📦'
        }
        
        # Determine the appropriate emoji and display format
        if isinstance(node, nw_instrument):
            emoji = '🔧'
            primary_info = f", Primary: {node.primary_val_key}" if node.primary_val_key else ", Primary: None"
            display_name = f"{emoji} {node.name} (ID: {node.id}, Type: {node.type}{primary_info})"
        elif isinstance(node, nw_asset):
            emoji = '📦'
            display_name = f"{emoji} {node.name} (ID: {node.id}, Product: {node.type})"
        else:
            emoji = emoji_map.get(node.type, '📋')
            display_name = f"{emoji} {node.name} (ID: {node.id}, Type: {node.type})"
        
        # Format with appropriate indentation
        indent = "     " * level
        lines.append(f"{indent}{display_name}")
        
        # Recursively format subnodes
        if hasattr(node, 'subnodes') and node.subnodes:
            for subnode in node.subnodes:
                lines.extend(self._pprint_node(subnode, level + 1))
                
        return lines

    def _pprint_node_md(self, node, level=0):
        """
        Recursively format a node and its subnodes in markdown format.
        
        Args:
            node: The node to format
            level (int): The hierarchy level (for markdown headers)
            
        Returns:
            list: List of formatted markdown lines
        """
        lines = []
        
        # Emoji mapping for different node types
        emoji_map = {
            'NW_root': '📍',
            'location': '🏢',
            'water_abstraction': '💧',
            'water_distribution': '🚰',
            'effluent_discharge': '🌊',
            'source_module': '🏔️',
            'disinfection_module': '🧽',
            'storage_module': '🏪',
            'outlet_module': '🚪',
            'asset': '📦'
        }
        
        # Determine markdown level (## for level 1, ### for level 2, etc.)
        # But use bullet points for deeper levels to avoid too many header levels
        if level <= 3:
            header_prefix = "#" * (level + 2)  # Start with ## for level 0
        else:
            header_prefix = "  " * (level - 3) + "-"  # Use indented bullet points for deeper levels
        
        # Determine the appropriate emoji and display format
        if isinstance(node, nw_instrument):
            emoji = '🔧'
            primary_info = f", Primary: {node.primary_val_key}" if node.primary_val_key else ""
            if level <= 3:
                display_name = f"{header_prefix} {emoji} {node.name}\n- **ID**: {node.id}\n- **Type**: {node.type}{primary_info}"
            else:
                display_name = f"{header_prefix} {emoji} **{node.name}** (ID: {node.id}, Type: {node.type}{primary_info})"
        elif isinstance(node, nw_asset):
            emoji = '📦'
            if level <= 3:
                display_name = f"{header_prefix} {emoji} {node.name}\n- **ID**: {node.id}\n- **Product**: {node.type}"
            else:
                display_name = f"{header_prefix} {emoji} **{node.name}** (ID: {node.id}, Product: {node.type})"
        else:
            emoji = emoji_map.get(node.type, '📋')
            if level <= 3:
                display_name = f"{header_prefix} {emoji} {node.name}\n- **ID**: {node.id}\n- **Type**: {node.type}"
            else:
                display_name = f"{header_prefix} {emoji} **{node.name}** (ID: {node.id}, Type: {node.type})"
        
        lines.append(display_name)
        lines.append("")  # Add blank line for better markdown formatting
        
        # Recursively format subnodes
        if hasattr(node, 'subnodes') and node.subnodes:
            for subnode in node.subnodes:
                lines.extend(self._pprint_node_md(subnode, level + 1))
                
        return lines

    def nw_hierarchy_from_node_instrumentation(self, n_info, i_info):

        # Create nw_node instances for each node in nodeinfo

        nodes = {}
        for node_id, info in n_info.items():
            node = nw_node(id=node_id, name=info['name'], type=info['type'])
            nodes[node_id] = node

        # Create nw_instrument instances for each instrumentation
        for inst_id, info in i_info.items():

            thresholds = []
            for t in info.get('thresholds', []):
                thresholds.append(dict(name=t.get('name', None),
                                       key=t.get('key', None),
                                       type=t.get('threshold_type', None),
                                       value=t.get('value', None)))

            inst = nw_instrument(id=inst_id, name=info['tag'], type=info['type'],
                                value_keys=info['value_keys'],
                                primary_val_key=info['specifications'],
                                thresholds=thresholds)

            nodes[inst_id] = inst

            # create nw_asset instances for each asset under this instrumentation
            assets = info.get('assets', [])
            for asset_attribs in assets:
                asset = nw_asset(id=asset_attribs["id"], name=asset_attribs['serial'], 
                        type=asset_attribs['prod_code'], prod_name=asset_attribs['product_name'])
                nodes[asset_attribs["id"]] = asset

                #print(f"{inst_id} has asset {asset_attribs['id']}")
                nodes[inst_id].subnodes.append(nodes[asset_attribs["id"]])

        # Build the hierarchy from nodeinfo
        for node_id, info in n_info.items():
            parent_id = info['parent_id']
            if parent_id in nodes:
                #print(f"{parent_id} has child {node_id}")
                nodes[parent_id].subnodes.append(nodes[node_id])

        # Add instruments to their parent modules based on the 'instrumentations' list
        for node_id, info in n_info.items():
            for i_id in info.get('instrumentations', []):
                if i_id in nodes:
                    #print(f"{node_id} has instrument {i_id}"   )
                    nodes[node_id].subnodes.append(nodes[i_id])

        # there can be multiple root nodes, lets create exactly one artifical node for all
        roots = [node for node in nodes.values() if node.type == "location"]
        root_node = nw_node(id=-1, name="NW_root", type="NW_root", subnodes=roots)
        self.nodes = nodes
            
        return root_node