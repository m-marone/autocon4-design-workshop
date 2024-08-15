"""API serializers for containerlab."""
from nautobot.apps.api import NautobotModelSerializer, TaggedModelSerializerMixin

from containerlab import models


class TopologySerializer(
    NautobotModelSerializer, TaggedModelSerializerMixin
):  # pylint: disable=too-many-ancestors
    """Topology Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.Topology
        fields = "__all__"

        # Option for disabling write for certain fields:
        # read_only_fields = []


class CLKindSerializer(NautobotModelSerializer):
    """CLKind Serializer."""

    class Meta:
        """Meta class."""

        model = models.CLKind
        fields = "__all__"
