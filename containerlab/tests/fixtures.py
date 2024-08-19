"""Create fixtures for tests."""

from containerlab.models import Topology


def create_topology():
    """Fixture to create necessary number of Topology for tests."""
    Topology.objects.create(name="Test One")
    Topology.objects.create(name="Test Two")
    Topology.objects.create(name="Test Three")
