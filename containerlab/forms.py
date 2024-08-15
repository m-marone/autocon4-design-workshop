"""Forms for containerlab."""
from django import forms
from nautobot.apps.forms import NautobotBulkEditForm, NautobotFilterForm, NautobotModelForm, TagsBulkEditFormMixin

from containerlab import models


class TopologyForm(NautobotModelForm):  # pylint: disable=too-many-ancestors
    """Topology creation/edit form."""

    class Meta:
        """Meta attributes."""

        model = models.Topology
        fields = [
            "name",
            "description",
        ]


class TopologyBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):  # pylint: disable=too-many-ancestors
    """Topology bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=models.Topology.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
        ]


class TopologyFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    model = models.Topology
    field_order = ["q", "name"]

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Slug.",
    )
    name = forms.CharField(required=False, label="Name")
