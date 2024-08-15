"""Test topology forms."""
from django.test import TestCase

from containerlab import forms


class TopologyTest(TestCase):
    """Test Topology forms."""

    def test_specifying_all_fields_success(self):
        form = forms.TopologyForm(
            data={
                "name": "Development",
                "description": "Development Testing",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_specifying_only_required_success(self):
        form = forms.TopologyForm(
            data={
                "name": "Development",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_validate_name_topology_is_required(self):
        form = forms.TopologyForm(data={"description": "Development Testing"})
        self.assertFalse(form.is_valid())
        self.assertIn("This field is required.", form.errors["name"])
