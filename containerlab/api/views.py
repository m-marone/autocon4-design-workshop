"""API views for containerlab."""

from nautobot.apps.api import NautobotModelViewSet

from containerlab import filters, models
from containerlab.api import serializers


class TopologyViewSet(NautobotModelViewSet):  # pylint: disable=too-many-ancestors
    """Topology viewset."""

    queryset = models.Topology.objects.all()
    serializer_class = serializers.TopologySerializer
    filterset_class = filters.TopologyFilterSet

    # Option for modifying the default HTTP methods:
    # http_method_names = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]


class CLKindViewSet(NautobotModelViewSet):
    """CLKind viewset."""

    queryset = models.CLKind.objects.all()
    serializer_class = serializers.CLKindSerializer
    filterset_class = filters.CLKindFilterSet
