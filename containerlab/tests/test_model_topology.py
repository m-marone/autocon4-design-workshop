"""Test Topology."""

from django.test import TestCase

from containerlab import models


class TestTopology(TestCase):
    """Test Topology."""

    def test_create_topology_only_required(self):
        """Create with only required fields, and validate null description and __str__."""
        topology = models.Topology.objects.create(name="Development")
        self.assertEqual(topology.name, "Development")
        self.assertEqual(topology.description, "")
        self.assertEqual(str(topology), "Development")

    def test_create_topology_all_fields_success(self):
        """Create Topology with all fields."""
        topology = models.Topology.objects.create(name="Development", description="Development Test")
        self.assertEqual(topology.name, "Development")
        self.assertEqual(topology.description, "Development Test")
