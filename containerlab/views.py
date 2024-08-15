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
