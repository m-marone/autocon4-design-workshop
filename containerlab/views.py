"""Views for containerlab."""
from nautobot.apps.views import NautobotUIViewSet

from containerlab import filters, forms, models, tables
from containerlab.api import serializers


class TopologyUIViewSet(NautobotUIViewSet):
    """ViewSet for Topology views."""

    bulk_update_form_class = forms.TopologyBulkEditForm
    filterset_class = filters.TopologyFilterSet
    filterset_form_class = forms.TopologyFilterForm
    form_class = forms.TopologyForm
    lookup_field = "pk"
    queryset = models.Topology.objects.all()
    serializer_class = serializers.TopologySerializer
    table_class = tables.TopologyTable


class CLKindUIViewSet(NautobotUIViewSet):
    """ViewSet for ContainerLab Kind"""

    bulk_update_form_class = forms.CLKindBulkEditForm
    filterset_class = filters.CLKindFilterSet
    filterset_form_class = forms.CLKindFilterForm
    form_class = forms.CLKindForm
    queryset = models.CLKind.objects.all()
    serializer_class = serializers.CLKindSerializer
    table_class = tables.CLKindTable
