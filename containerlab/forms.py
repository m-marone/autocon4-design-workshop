"""Forms for containerlab."""
from django import forms
from nautobot.apps.forms import (
    DynamicModelChoiceField,
    NautobotBulkEditForm,
    NautobotFilterForm,
    NautobotModelForm,
    TagsBulkEditFormMixin,
)
from nautobot.extras.models import DynamicGroup

from containerlab import models


class TopologyForm(NautobotModelForm):  # pylint: disable=too-many-ancestors
    """Topology creation/edit form."""

    dynamic_group = DynamicModelChoiceField(
        queryset=DynamicGroup.objects.all(), label="Dynamic Group"
    )

    class Meta:
        """Meta attributes."""

        model = models.Topology
        fields = [
            "name",
            "description",
            "dynamic_group",
            "custom_template",
        ]


class TopologyBulkEditForm(
    TagsBulkEditFormMixin, NautobotBulkEditForm
):  # pylint: disable=too-many-ancestors
    """Topology bulk edit form."""

    pk = forms.ModelMultipleChoiceField(
        queryset=models.Topology.objects.all(), widget=forms.MultipleHiddenInput
    )
    description = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
        ]


class TopologyFilterForm(NautobotFilterForm):  # pylint: disable=too-many-ancestors
    """Filter form to filter searches."""

    model = models.Topology
    field_order = ["q", "name"]

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Slug.",
    )
    name = forms.CharField(required=False, label="Name")


class CLKindForm(NautobotModelForm):
    """ContainerLab Kind create/edit form."""

    class Meta:
        """Meta atributes."""

        model = models.CLKind
        fields = [
            "platform",
            "kind",
            "image",
            "exposed_ports",
            "node_extras",
        ]


class CLKindBulkEditForm(NautobotBulkEditForm):
    """ContinaerLab Kind bulk edit form."""

    pk = forms.ModelMultipleChoiceField(
        queryset=models.CLKind.objects.all(), widget=forms.MultipleHiddenInput
    )
    image = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = ["image"]


class CLKindFilterForm(NautobotFilterForm):
    """Filter form to filter ContainerLab Kind searches."""

    model = models.CLKind
    field_order = ["q", "kind"]

    q = forms.CharField(
        required=False, label="Search", help_text="Search within 'kind'."
    )
    kind = forms.CharField(required=False, label="kind")
