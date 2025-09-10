"""
Unit tests for nw_hierarchy module.

This module contains comprehensive tests for the nw_hierarchy class and its components,
including nw_node, nw_instrument, and nw_asset classes.
"""

# run with:
# python -m unittest test_nw_hierarchy.py -v

import unittest
from pydantic import ValidationError
from nwater.nw_hierarchy import nw_node, nw_instrument, nw_asset, nw_hierarchy


class TestNwNode(unittest.TestCase):
    """Test cases for nw_node class."""

    def test_valid_node_creation(self):
        """Test creating a valid nw_node."""
        node = nw_node(id=1, name="Test Node", type="location")
        self.assertEqual(node.id, 1)
        self.assertEqual(node.name, "Test Node")
        self.assertEqual(node.type, "location")
        self.assertEqual(len(node.subnodes), 0)

    def test_default_values(self):
        """Test nw_node with default values."""
        node = nw_node()
        self.assertEqual(node.id, 0)
        self.assertEqual(node.name, "")
        self.assertEqual(node.type, "")
        self.assertEqual(len(node.subnodes), 0)

    def test_root_node_id_validation(self):
        """Test that -1 id is accepted for root node."""
        node = nw_node(id=-1, name="Root", type="NW_root")
        self.assertEqual(node.id, -1)

    def test_invalid_id_validation(self):
        """Test that invalid IDs are rejected."""
        with self.assertRaises(ValidationError):
            nw_node(id=-2, name="Invalid", type="location")
        
        with self.assertRaises(ValidationError):
            nw_node(id="string", name="Invalid", type="location")

    def test_node_equality(self):
        """Test node equality based on ID."""
        node1 = nw_node(id=1, name="Node1", type="location")
        node2 = nw_node(id=1, name="Node2", type="application")  # Different name/type, same ID
        node3 = nw_node(id=2, name="Node1", type="location")     # Same name/type, different ID
        
        self.assertEqual(node1, node2)  # Same ID
        self.assertNotEqual(node1, node3)  # Different ID

    def test_node_hash(self):
        """Test node hashing based on ID."""
        node1 = nw_node(id=1, name="Node1", type="location")
        node2 = nw_node(id=1, name="Node2", type="application")
        node3 = nw_node(id=2, name="Node1", type="location")
        
        self.assertEqual(hash(node1), hash(node2))  # Same ID
        self.assertNotEqual(hash(node1), hash(node3))  # Different ID

    def test_node_str_representation(self):
        """Test string representation of node."""
        node = nw_node(id=1, name="Test Node", type="location")
        expected = "(1, 'Test Node', location)"
        self.assertEqual(str(node), expected)


class TestNwInstrument(unittest.TestCase):
    """Test cases for nw_instrument class."""

    def test_instrument_creation(self):
        """Test creating a valid nw_instrument."""
        inst = nw_instrument(
            id=100,
            name="Flow Meter",
            type="Flow",
            primary_val_key="flow_rate",
            value_keys=["flow_rate", "temperature"],
            thresholds=[{"name": "high_flow", "value": 100}]
        )
        
        self.assertEqual(inst.id, 100)
        self.assertEqual(inst.name, "Flow Meter")
        self.assertEqual(inst.type, "Flow")
        self.assertEqual(inst.primary_val_key, "flow_rate")
        self.assertEqual(inst.value_keys, ["flow_rate", "temperature"])
        self.assertEqual(len(inst.thresholds), 1)

    def test_instrument_tag_property(self):
        """Test that tag property returns the name."""
        inst = nw_instrument(id=100, name="Flow Meter", type="Flow")
        self.assertEqual(inst.tag, "Flow Meter")

    def test_instrument_assets_property(self):
        """Test that assets property returns subnodes."""
        inst = nw_instrument(id=100, name="Flow Meter", type="Flow")
        asset = nw_asset(id=200, name="12345", type="FM001", prod_name="FlowMaster")
        inst.subnodes.append(asset)
        
        self.assertEqual(len(inst.assets), 1)
        self.assertEqual(inst.assets[0], asset)

    def test_instrument_defaults(self):
        """Test nw_instrument with default values."""
        inst = nw_instrument(id=100, name="Test", type="Flow")
        self.assertIsNone(inst.primary_val_key)
        self.assertEqual(inst.value_keys, [])
        self.assertEqual(inst.thresholds, [])


class TestNwAsset(unittest.TestCase):
    """Test cases for nw_asset class."""

    def test_asset_creation(self):
        """Test creating a valid nw_asset."""
        asset = nw_asset(id=200, name="12345", type="FM001", prod_name="FlowMaster")
        
        self.assertEqual(asset.id, 200)
        self.assertEqual(asset.name, "12345")
        self.assertEqual(asset.type, "FM001")
        self.assertEqual(asset.prod_name, "FlowMaster")

    def test_asset_serial_property(self):
        """Test that serial property returns the name."""
        asset = nw_asset(id=200, name="12345", type="FM001", prod_name="FlowMaster")
        self.assertEqual(asset.serial, "12345")

    def test_asset_prod_code_property(self):
        """Test that prod_code property returns the type."""
        asset = nw_asset(id=200, name="12345", type="FM001", prod_name="FlowMaster")
        self.assertEqual(asset.prod_code, "FM001")


class TestNwHierarchy(unittest.TestCase):
    """Test cases for nw_hierarchy class."""

    def setUp(self):
        """Set up test data for hierarchy tests."""
        # Sample node information
        self.node_info = {
            1: {
                'name': 'Main Location',
                'type': 'location',
                'parent_id': -1,
                'instrumentations': []
            },
            2: {
                'name': 'Water Abstraction',
                'type': 'water_abstraction',
                'parent_id': 1,
                'instrumentations': [100]
            },
            3: {
                'name': 'Source Module',
                'type': 'source_module',
                'parent_id': 2,
                'instrumentations': [101]
            }
        }
        
        # Sample instrumentation information
        self.instrumentation_info = {
            100: {
                'tag': 'Main Flow Meter',
                'type': 'Flow',
                'value_keys': ['flow_rate', 'temperature'],
                'specifications': 'flow_rate',
                'thresholds': [
                    {
                        'name': 'high_flow',
                        'key': 'flow_rate',
                        'threshold_type': 'upper',
                        'value': 100.0
                    }
                ],
                'assets': [
                    {
                        'id': 200,
                        'serial': 'FM-001',
                        'prod_code': 'FLOW-MASTER',
                        'product_name': 'FlowMaster Pro'
                    }
                ]
            },
            101: {
                'tag': 'Pressure Sensor',
                'type': 'Pressure',
                'value_keys': ['pressure'],
                'specifications': 'pressure',
                'thresholds': [],
                'assets': []
            }
        }

    def test_hierarchy_creation(self):
        """Test creating a hierarchy from node and instrumentation info."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        
        self.assertIsNotNone(hierarchy.root)
        self.assertEqual(hierarchy.root.type, "NW_root")
        self.assertEqual(hierarchy.root.id, -1)

    def test_node_categorization(self):
        """Test that nodes are correctly categorized during initialization."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        
        self.assertEqual(len(hierarchy.all_locations), 1)
        self.assertEqual(len(hierarchy.all_applications), 1)
        self.assertEqual(len(hierarchy.all_modules), 1)
        self.assertEqual(len(hierarchy.all_instrumentations), 2)
        self.assertEqual(len(hierarchy.all_assets), 1)

    def test_get_node_counts(self):
        """Test node count statistics."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        counts = hierarchy.get_node_counts()
        
        expected_counts = {
            'locations': 1,
            'applications': 1,
            'modules': 1,
            'instrumentations': 2,
            'assets': 1,
            'total': 6
        }
        
        self.assertEqual(counts, expected_counts)

    def test_get_applications(self):
        """Test retrieving applications for a location."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        location = hierarchy.all_locations[0]
        applications = hierarchy.get_applications(location)
        
        self.assertEqual(len(applications), 1)
        self.assertEqual(applications[0].type, 'water_abstraction')

    def test_get_modules(self):
        """Test retrieving modules for an application."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        application = hierarchy.all_applications[0]
        modules = hierarchy.get_modules(application)
        
        # Application has 2 subnodes: 1 module + 1 instrumentation
        self.assertEqual(len(modules), 2)
        
        # Find the module among the subnodes
        module_found = False
        for subnode in modules:
            if subnode.type == 'source_module':
                module_found = True
                break
        self.assertTrue(module_found, "Source module should be found among application's subnodes")

    def test_get_instrumentations(self):
        """Test retrieving instrumentations for a module."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        module = hierarchy.all_modules[0]
        instrumentations = hierarchy.get_instrumentations(module)
        
        self.assertEqual(len(instrumentations), 1)
        self.assertEqual(instrumentations[0].type, 'Pressure')

    def test_get_assets(self):
        """Test retrieving assets for an instrumentation."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        
        # Find the instrumentation with assets
        instrumentation_with_assets = None
        for inst in hierarchy.all_instrumentations:
            if inst.subnodes:  # Has assets
                instrumentation_with_assets = inst
                break
        
        self.assertIsNotNone(instrumentation_with_assets)
        assets = hierarchy.get_assets(instrumentation_with_assets)
        
        self.assertEqual(len(assets), 1)
        self.assertEqual(assets[0].serial, 'FM-001')

    def test_get_node_by_id(self):
        """Test fast node lookup by ID."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        
        # Test existing node
        node = hierarchy.get_node_by_id(1)
        self.assertIsNotNone(node)
        self.assertEqual(node.name, 'Main Location')
        
        # Test non-existing node
        node = hierarchy.get_node_by_id(999)
        self.assertIsNone(node)

    def test_get_nodes_by_name(self):
        """Test finding nodes by name."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        
        # Test existing name
        nodes = hierarchy.get_nodes_by_name('Main Location')
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].id, 1)
        
        # Test non-existing name
        nodes = hierarchy.get_nodes_by_name('Non-existent')
        self.assertEqual(len(nodes), 0)

    def test_get_nodes_by_type(self):
        """Test finding nodes by type."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        
        # Test location type
        locations = hierarchy.get_nodes_by_type('location')
        self.assertEqual(len(locations), 1)
        
        # Test application type
        applications = hierarchy.get_nodes_by_type('water_abstraction')
        self.assertEqual(len(applications), 1)

    def test_search_hierarchy(self):
        """Test hierarchy search functionality."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        
        # Test case-insensitive search
        results = hierarchy.search_hierarchy('main', case_sensitive=False)
        self.assertEqual(len(results['locations']), 1)
        self.assertEqual(len(results['instrumentations']), 1)
        
        # Test case-sensitive search
        results = hierarchy.search_hierarchy('Main', case_sensitive=True)
        self.assertEqual(len(results['locations']), 1)
        self.assertEqual(len(results['instrumentations']), 1)
        
        # Test no matches
        results = hierarchy.search_hierarchy('nonexistent')
        for category in results.values():
            self.assertEqual(len(category), 0)

    def test_get_instrumentations_by_value_key(self):
        """Test finding instrumentations by value key."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        
        # Test existing value key
        instruments = hierarchy.get_instrumentations_by_value_key('flow_rate')
        self.assertEqual(len(instruments), 1)
        self.assertEqual(instruments[0].name, 'Main Flow Meter')
        
        # Test non-existing value key
        instruments = hierarchy.get_instrumentations_by_value_key('humidity')
        self.assertEqual(len(instruments), 0)

    def test_get_instrumentations_without_thresholds(self):
        """Test finding instrumentations without thresholds."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        
        instruments_without_thresholds = hierarchy.get_instrumentations_without_thresholds()
        self.assertEqual(len(instruments_without_thresholds), 1)
        self.assertEqual(instruments_without_thresholds[0].name, 'Pressure Sensor')

    def test_get_detailed_statistics(self):
        """Test detailed statistics generation."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        stats = hierarchy.get_detailed_statistics()
        
        # Check basic counts
        self.assertEqual(stats['locations'], 1)
        self.assertEqual(stats['applications'], 1)
        self.assertEqual(stats['modules'], 1)
        self.assertEqual(stats['instrumentations'], 2)
        self.assertEqual(stats['assets'], 1)
        
        # Check type distributions
        self.assertIn('instrument_types', stats)
        self.assertIn('application_types', stats)
        self.assertIn('module_types', stats)
        
        # Check threshold statistics
        self.assertEqual(stats['instruments_with_thresholds'], 1)
        self.assertEqual(stats['instruments_without_thresholds'], 1)
        self.assertEqual(stats['threshold_coverage'], 50.0)

    def test_get_asset_by_serial(self):
        """Test finding asset by serial number."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        
        # Test existing serial
        asset = hierarchy.get_asset_by_serial('FM-001')
        self.assertIsNotNone(asset)
        self.assertEqual(asset.prod_name, 'FlowMaster Pro')
        
        # Test non-existing serial
        asset = hierarchy.get_asset_by_serial('NON-EXISTENT')
        self.assertIsNone(asset)

    def test_print_summary(self):
        """Test summary printing."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        summary = hierarchy.print_summary()
        
        self.assertIsInstance(summary, str)
        self.assertIn('NW HIERARCHY SUMMARY', summary)
        self.assertIn('Locations:', summary)
        self.assertIn('Applications:', summary)

    def test_print_md_summary(self):
        """Test markdown summary printing."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        summary = hierarchy.print_md_summary()
        
        self.assertIsInstance(summary, str)
        self.assertIn('# 📊 NW Hierarchy Summary', summary)
        self.assertIn('| Component Type | Count |', summary)

    def test_pprint(self):
        """Test pretty printing of hierarchy."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        pprint_output = hierarchy.pprint(show_summary=True)
        
        self.assertIsInstance(pprint_output, str)
        self.assertIn('NW Hierarchy Pretty Print', pprint_output)
        self.assertIn('Main Location', pprint_output)

    def test_pprint_md(self):
        """Test markdown pretty printing of hierarchy."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        pprint_output = hierarchy.pprint_md(show_summary=True)
        
        self.assertIsInstance(pprint_output, str)
        self.assertIn('# 🏗️ NW Hierarchy Structure', pprint_output)
        self.assertIn('Main Location', pprint_output)

    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        hierarchy = nw_hierarchy(self.node_info, self.instrumentation_info)
        
        # Test None inputs
        with self.assertRaises(ValueError):
            hierarchy.get_applications(None)
        
        with self.assertRaises(ValueError):
            hierarchy.get_modules(None)
        
        with self.assertRaises(ValueError):
            hierarchy.get_instrumentations(None)
        
        with self.assertRaises(ValueError):
            hierarchy.get_assets(None)

    def test_empty_hierarchy(self):
        """Test creating hierarchy with empty data."""
        empty_hierarchy = nw_hierarchy({}, {})
        
        self.assertEqual(len(empty_hierarchy.all_locations), 0)
        self.assertEqual(len(empty_hierarchy.all_applications), 0)
        self.assertEqual(len(empty_hierarchy.all_modules), 0)
        self.assertEqual(len(empty_hierarchy.all_instrumentations), 0)
        self.assertEqual(len(empty_hierarchy.all_assets), 0)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
