"""Unit tests for views."""
from nautobot.apps.testing import ViewTestCases

from containerlab import models
from containerlab.tests import fixtures


class TopologyViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    # pylint: disable=too-many-ancestors
    """Test the Topology views."""

    model = models.Topology
    bulk_edit_data = {"description": "Bulk edit views"}
    form_data = {
        "name": "Test 1",
        "description": "Initial model",
    }
    csv_data = (
        "name",
        "Test csv1",
        "Test csv2",
        "Test csv3",
    )

    @classmethod
    def setUpTestData(cls):
        fixtures.create_topology()
