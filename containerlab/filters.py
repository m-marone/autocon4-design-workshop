"""Filtering for containerlab."""

from nautobot.apps.filters import NameSearchFilterSet, NautobotFilterSet

from containerlab import models


class TopologyFilterSet(NautobotFilterSet, NameSearchFilterSet):  # pylint: disable=too-many-ancestors
    """Filter for Topology."""

    class Meta:
        """Meta attributes for filter."""

        model = models.Topology

        # add any fields from the model that you would like to filter your searches by using those
        fields = ["id", "name", "description"]
