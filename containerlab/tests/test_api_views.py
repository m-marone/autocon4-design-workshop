"""Unit tests for containerlab."""

from nautobot.apps.testing import APIViewTestCases

from containerlab import models
from containerlab.tests import fixtures


class TopologyAPIViewTest(APIViewTestCases.APIViewTestCase):
    # pylint: disable=too-many-ancestors
    """Test the API viewsets for Topology."""

    model = models.Topology
    create_data = [
        {
            "name": "Test Model 1",
            "description": "test description",
        },
        {
            "name": "Test Model 2",
        },
    ]
    bulk_update_data = {"description": "Test Bulk Update"}

    @classmethod
    def setUpTestData(cls):
        fixtures.create_topology()
