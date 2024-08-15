"""Tables for containerlab."""

import django_tables2 as tables
from nautobot.apps.tables import BaseTable, ButtonsColumn, ToggleColumn

from containerlab import models


class TopologyTable(BaseTable):
    # pylint: disable=R0903
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    dynamic_group = tables.Column(linkify=True, verbose_name="Dynamic Group")
    actions = ButtonsColumn(
        models.Topology,
        # Option for modifying the default action buttons on each row:
        # buttons=("changelog", "edit", "delete"),
        # Option for modifying the pk for the action buttons:
        pk_field="pk",
    )

    class Meta(BaseTable.Meta):
        # pylint: disable=nb-use-fields-all
        """Meta attributes."""

        model = models.Topology
        fields = (
            "pk",
            "name",
            "dynamic_group",
            "description",
        )

        # Option for modifying the columns that show up in the list view by default:
        # default_columns = (
        #     "pk",
        #     "name",
        #     "description",
        # )


class CLKindTable(BaseTable):
    """Table for CLKind."""

    pk = ToggleColumn()
    kind = tables.Column(linkify=True)

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.CLKind
        fields = ("pk", "kind", "image", "type")
