"""Added content to the device model view for config compliance."""

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q
from django.urls import reverse
from nautobot.extras.plugins import PluginTemplateExtension

from containerlab.models import Topology


class GuacamoleConnection(PluginTemplateExtension):  # pylint: disable=abstract-method
    """App extension class for config compliance."""

    model = "dcim.device"

    @property
    def device(self):
        """Device presented in detail view."""
        return self.context["object"]

    def right_page(self):
        """Content to add to the configuration compliance."""
        # TODO: Ensure this query will not slow things as this scales
        topologies = Topology.objects.filter(dynamic_group__in=self.device.dynamic_groups)
        if not topologies:
            return ""
        extra_context = {
            "device": self.device,
            "template_type": "devicetab",
            "topologies": topologies,
        }
        return self.render(
            "containerlab/guacamole_connection.html",
            extra_context=extra_context,
        )


template_extensions = [GuacamoleConnection]
