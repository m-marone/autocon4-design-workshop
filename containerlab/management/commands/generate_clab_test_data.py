# ruff: noqa: D100, D101, D102, D103, PLR0915

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from nautobot.dcim.choices import InterfaceTypeChoices
from nautobot.dcim.models import (
    Cable,
    Device,
    DeviceType,
    Interface,
    InterfaceTemplate,
    Location,
    LocationType,
    Manufacturer,
    Platform,
)
from nautobot.extras.choices import DynamicGroupTypeChoices
from nautobot.extras.models import DynamicGroup, Role, Status

from containerlab.models import CLKind, Topology


class Command(BaseCommand):
    help = "Generate a couple of connected devices to test containerlab."

    def handle(self, *args, **options):
        manufacturer, _ = Manufacturer.objects.get_or_create(name="Arista")
        device_role, _ = Role.objects.get_or_create(name="Router")
        device_role.content_types.add(ContentType.objects.get_for_model(Device))
        device_type, _ = DeviceType.objects.get_or_create(manufacturer=manufacturer, model="Arista cEOS")
        for i in range(1, 5):
            InterfaceTemplate.objects.get_or_create(
                name=f"eth{i}", device_type=device_type, type=InterfaceTypeChoices.TYPE_1GE_FIXED
            )
        location_type, _ = LocationType.objects.get_or_create(name="Datacenter")
        location_type.content_types.add(ContentType.objects.get_for_model(Device))
        location, _ = Location.objects.get_or_create(
            name="NYC1", location_type=location_type, status=Status.objects.get(name="Active")
        )
        platform, _ = Platform.objects.get_or_create(
            name="Arista EOS", manufacturer=manufacturer, napalm_driver="eos", network_driver="arista_eos"
        )

        rtr1, created = Device.objects.get_or_create(
            name="rtr1",
            device_type=device_type,
            role=device_role,
            platform=platform,
            location=location,
            status=Status.objects.get(name="Active"),
        )
        rtr2, _ = Device.objects.get_or_create(
            name="rtr2",
            device_type=device_type,
            role=device_role,
            platform=platform,
            location=location,
            status=Status.objects.get(name="Active"),
        )
        rtr3, _ = Device.objects.get_or_create(
            name="rtr3",
            device_type=device_type,
            role=device_role,
            platform=platform,
            location=location,
            status=Status.objects.get(name="Active"),
        )

        if created:
            interface_ct = ContentType.objects.get_for_model(Interface)
            Cable.objects.create(
                termination_a_id=rtr1.interfaces.first().id,
                termination_a_type=interface_ct,
                termination_b_id=rtr2.interfaces.first().id,
                termination_b_type=interface_ct,
                status=Status.objects.get(name="Connected"),
            )
            Cable.objects.create(
                termination_a_id=rtr2.interfaces.last().id,
                termination_a_type=interface_ct,
                termination_b_id=rtr3.interfaces.last().id,
                termination_b_type=interface_ct,
                status=Status.objects.get(name="Connected"),
            )

        CLKind.objects.get_or_create(kind="ceos", image="ceos:4.32.1F", platform=platform)
        dynamic_group, _ = DynamicGroup.objects.get_or_create(
            name="lab devices",
            group_type=DynamicGroupTypeChoices.TYPE_STATIC,
            content_type=ContentType.objects.get_for_model(Device),
        )
        dynamic_group.add_members([rtr1, rtr2, rtr3])
        Topology.objects.get_or_create(name="lab devices", dynamic_group=dynamic_group)

        self.stdout.write("Test data generated successfully.")
