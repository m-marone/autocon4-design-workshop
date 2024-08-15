"""Test Topology Filter."""

from django.test import TestCase

from containerlab import filters, models
from containerlab.tests import fixtures


class TopologyFilterTestCase(TestCase):
    """Topology Filter Test Case."""

    queryset = models.Topology.objects.all()
    filterset = filters.TopologyFilterSet

    @classmethod
    def setUpTestData(cls):
        """Setup test data for Topology Model."""
        fixtures.create_topology()

    def test_q_search_name(self):
        """Test using Q search with name of Topology."""
        params = {"q": "Test One"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_invalid(self):
        """Test using invalid Q search for Topology."""
        params = {"q": "test-five"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
