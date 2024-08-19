"""Models for Containerlab."""

import json
import os

import yaml
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from jsonschema.validators import Draft7Validator
from nautobot.apps.models import BaseModel, PrimaryModel
from nautobot.apps.utils import render_jinja2
from nautobot.dcim.models import Cable

# from nautobot.extras.utils import extras_features
# If you want to use the extras_features decorator please reference the following documentation
# https://docs.nautobot.com/projects/core/en/latest/plugins/development/#using-the-extras_features-decorator-for-graphql
# Then based on your reading you may decide to put the following decorator before the declaration of your class
# @extras_features("custom_fields", "custom_validators", "relationships", "graphql")


# If you want to choose a specific model to overload in your class declaration, please reference the following documentation:
# how to chose a database model: https://docs.nautobot.com/projects/core/en/stable/plugins/development/#database-models
class Topology(PrimaryModel):  # pylint: disable=too-many-ancestors
    """Base model for Containerlab app."""

    name = models.CharField(max_length=255, unique=True, help_text="Name of Containerlab Topology")
    description = models.CharField(max_length=255, blank=True)
    dynamic_group = models.ForeignKey(
        to="extras.DynamicGroup",
        on_delete=models.PROTECT,
        related_name="containerlab_topology",
        help_text="DynamicGroup from which to build the topology file",
        blank=True,
        null=True,
    )
    custom_template = models.ForeignKey(
        to="containerlab.TopologyTemplate",
        on_delete=models.PROTECT,
        related_name="containerlab_topology",
        help_text="Custom template to use for topology file",
        blank=True,
        null=True,
    )
    is_dynamic_group_associable_model = False

    class Meta:
        """Meta class."""

        ordering = ["name"]
        verbose_name = "Containerlab Topology"
        verbose_name_plural = "Containerlab Topologies"

    def __str__(self):
        """Stringify instance."""
        return self.name

    def generate_topology_file_dict(self, **kwargs):
        return yaml.safe_load(self.generate_topology_file())

    def generate_mermaid_diagram(self, **kwargs):
        """Generate mermaid diagram definition."""
        topology = self.generate_topology_file_dict()["topology"]
        endpoints = topology.get("links", [])
        links = [
            f"{ep['endpoints'][0].split(':')[0]}---|"
            f"{ep['endpoints'][0].split(':')[1]}:{ep['endpoints'][1].split(':')[1]}|"
            f"{ep['endpoints'][1].split(':')[0]}"
            for ep in endpoints
        ]
        if not links:
            # Sort by Device name
            return "graph TD\n" + "\n".join(sorted(topology["nodes"].keys()))
        # Sort by termination_a Device name, then termination_a Interface name
        return "graph TD\n" + "\n".join(sorted(links, key=lambda x: (x.split("---")[0], x.split("|")[1].split(":")[0])))

    def generate_topology_file(self, **kwargs):
        """Generate a containerlab topology file."""
        if self.custom_template:
            # Try to find custom template
            template = self.custom_template.template_content
        # Custom Template not found, use default template
        else:
            with open(
                os.path.join(
                    os.path.dirname(__file__),
                    "templates",
                    "containerlab_templates",
                    "topology.yml.j2",
                )
            ) as handle:
                template = handle.read()

        members = []
        kinds = set()
        for member in self.dynamic_group.update_cached_members():
            kind = CLKind.objects.get(platform=member.platform)
            kinds.add(kind)
            members.append(
                {
                    "obj": member,
                    "kind": kind,
                    "node_extras": {
                        k: render_jinja2(template_code=v, context={"obj": member}) for k, v in kind.node_extras.items()
                    },
                }
            )

        topology_data = render_jinja2(
            template_code=template,
            context={"topology": self, "members": members, "kinds": kinds, **kwargs},
        )
        return topology_data

    def get_member_cables(self):  # noqa: D102
        member_devices = self.dynamic_group.update_cached_members()
        return Cable.objects.filter(_termination_a_device__in=member_devices, _termination_b_device__in=member_devices)

    def validate_topology_file(self, **kwargs):
        """Validate generated topology file."""
        topology_yaml = yaml.safe_load(self.generate_topology_file())
        with open(os.path.join(os.path.dirname(__file__), "utils", "topology_schema.json")) as file:
            schema = json.load(file)
            Draft7Validator.check_schema(schema)

            try:
                Draft7Validator(schema).validate(topology_yaml)
                return {"valid": True, "error": ""}
            except JsonSchemaValidationError as err:
                return {"valid": False, "error": err.message}


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
    platform = models.ForeignKey(to="dcim.Platform", on_delete=models.PROTECT, related_name="clkind")
    exposed_ports = models.CharField(max_length=100, blank=True)

    class Meta:
        """Meta class."""

        ordering = ["kind"]
        unique_together = ("kind", "image")
        verbose_name = "ContainerLab Kind"
        verbose_name_plural = "ContainerLab Kinds"

    def __str__(self):
        """Stringify instance."""
        return self.kind

    def _clean_exposed_ports(self):
        """Perform validation of the `exposed_ports` field."""
        # Split the string by commas
        if self.exposed_ports:
            values = self.exposed_ports.split(",")

            # Check if any value is empty (e.g., ",," or leading/trailing commas)
            if any(not v.strip() for v in values):
                raise ValidationError({"exposed_ports": "Invalid Comma-Separated string."})

    def _clean_node_extras(self):
        """Perform validation of the `node_extras` field."""
        # Ensure ports isn't defined in Extra Node configuration. While it is valid, we use the exposed ports field.
        if "ports" in self.node_extras.keys():
            raise ValidationError(
                {"node_extras": "Node Extras must not define ports. Please use the 'Exposed Ports' field."}
            )

    def clean(self):
        """Clean method for CLKind model."""
        super().clean()

        self._clean_exposed_ports()
        self._clean_node_extras()


class TopologyTemplate(BaseModel):  # pylint: disable=too-many-ancestors
    """Base model for Containerlab app."""

    name = models.CharField(max_length=255, unique=True, help_text="Name of Containerlab Topology")
    template_content = models.TextField(blank=True)
    is_dynamic_group_associable_model = False

    class Meta:
        """Meta class."""

        ordering = ["name"]
        verbose_name = "Topology Template"
        verbose_name_plural = "Topology Templates"

    def __str__(self):
        """Stringify instance."""
        return self.name
