"""Models for Containerlab."""

import os

# Django imports
from django.db import models
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
import jsonschema
from jsonschema import validate

# Nautobot imports
from nautobot.apps.models import PrimaryModel
from nautobot.apps.utils import render_jinja2

# from nautobot.extras.utils import extras_features
# If you want to use the extras_features decorator please reference the following documentation
# https://docs.nautobot.com/projects/core/en/latest/plugins/development/#using-the-extras_features-decorator-for-graphql
# Then based on your reading you may decide to put the following decorator before the declaration of your class
# @extras_features("custom_fields", "custom_validators", "relationships", "graphql")


# If you want to choose a specific model to overload in your class declaration, please reference the following documentation:
# how to chose a database model: https://docs.nautobot.com/projects/core/en/stable/plugins/development/#database-models
class Topology(PrimaryModel):  # pylint: disable=too-many-ancestors
    """Base model for Containerlab app."""

    name = models.CharField(
        max_length=255, unique=True, help_text="Name of Containerlab Topology"
    )
    description = models.CharField(max_length=255, blank=True)
    dynamic_group = models.ForeignKey(
        to="extras.DynamicGroup",
        on_delete=models.CASCADE,
        related_name="containerlab_topologies",
        help_text="DynamicGroup from which to build the topology file",
        blank=True,
        null=True,
    )

    class Meta:
        """Meta class."""

        ordering = ["name"]
        verbose_name = "Containerlab Topology"
        verbose_name_plural = "Containerlab Topologies"

    def __str__(self):
        """Stringify instance."""
        return self.name

    def generate_topology_file(self):
        """Generate a containerlab topology file."""
        with open(
            os.path.join(
                os.path.dirname(__file__),
                "templates",
                "containerlab_templates",
                "topology.yml.j2",
            )
        ) as handle:
            template = handle.read()
        topology_data = render_jinja2(
            template_code=template, context={"topology": self}
        )
        return topology_data

    def get_member_cables(self):
        cables = set()
        for device in self.dynamic_group.members.all():
            for intf in device.interfaces.all():
                if intf.cable:
                    cables.add(intf.cable)
        return cables


class CLKind(PrimaryModel):
    """Model for ContainerLab attributes."""

    kind = models.CharField(max_length=25)
    image = models.CharField(max_length=100)
    node_extras = models.JSONField(
        default=dict,
        encoder=DjangoJSONEncoder,
        blank=True,
        help_text="These configurations are flattened an applied to each node. This field has access to obj object which represents each device.",
    )
    platform = models.ForeignKey(
        to="dcim.Platform", on_delete=models.PROTECT, related_name="clkind"
    )
    exposed_ports = models.CharField(max_length=100, blank=True)

    class Meta:
        """Meta class."""

        ordering = ["kind"]
        unique_together = ("kind", "image")
        verbose_name = "ContainerLab Kind"
        verbose_name_plural = "ContainerLab Kinds"

    def _clean_exposed_ports(self):
        """Perform validation of the `exposed_ports` field."""
        # Split the string by commas

        values = self.exposed_ports.split(",")

        # Check if any value is empty (e.g., ",," or leading/trailing commas)
        if any(not v.strip() for v in values):
            raise ValidationError({"exposed_ports": "Invalid Comma-Separated string."})

    def _clean_node_extras(self):
        """Perform validation of the `node_extras` field."""

        # Ensure ports isn't defined in Extra Node configuration. While it is valid, we use the exposed ports field.
        if "ports" in self.node_extras.keys():
            raise ValidationError(
                {
                    "node_extras": "Node Extras must not define ports. Please use the 'Exposed Ports' field."
                }
            )

    def clean(self):
        """Clean method for CLKind model."""
        super().clean()

        self._clean_exposed_ports()
        self._clean_node_extras()
