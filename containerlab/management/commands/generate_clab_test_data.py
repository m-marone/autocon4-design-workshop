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
    help = "Generate a topology of connected devices to test containerlab."

    def add_arguments(self, parser):
        parser.add_argument(
            "--size",
            help="Topology size. Defaults to small.",
            choices=["small", "medium", "large"],
            default="small",
        )

    def handle(self, *args, **options):
        common_data = self.common_data()

        devices = self.small_topology(**common_data)
        common_data["dynamic_group"].add_members(devices)

        if options["size"] in ["medium", "large"]:
            devices = self.medium_topology(**common_data)
            common_data["dynamic_group"].add_members(devices)

        if options["size"] == "large":
            devices = self.large_topology(**common_data)
            common_data["dynamic_group"].add_members(devices)

        self.stdout.write("Test data generated successfully.")

    def common_data(self):
        manufacturer, _ = Manufacturer.objects.get_or_create(name="Arista")
        device_role, _ = Role.objects.get_or_create(name="Router")
        device_role.content_types.add(ContentType.objects.get_for_model(Device))
        device_type, _ = DeviceType.objects.get_or_create(manufacturer=manufacturer, model="Arista cEOS")
        for i in range(1, 9):
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
        CLKind.objects.get_or_create(kind="ceos", image="ceos:4.32.1F", platform=platform)
        dynamic_group, _ = DynamicGroup.objects.get_or_create(
            name="lab devices",
            group_type=DynamicGroupTypeChoices.TYPE_STATIC,
            content_type=ContentType.objects.get_for_model(Device),
        )
        Topology.objects.get_or_create(name="lab devices", dynamic_group=dynamic_group)

        return {
            "device_type": device_type,
            "device_role": device_role,
            "location": location,
            "platform": platform,
            "dynamic_group": dynamic_group,
        }

    def small_topology(self, device_type, device_role, location, platform, **kwargs):
        """The small topology consists of a single backbone router and single distribution router."""
        bb_rtr1, _ = Device.objects.get_or_create(
            name="wan-rtr-bb1",
            device_type=device_type,
            role=device_role,
            platform=platform,
            location=location,
            status=Status.objects.get(name="Active"),
        )
        dist_rtr1, _ = Device.objects.get_or_create(
            name="dist-rtr1",
            device_type=device_type,
            role=device_role,
            platform=platform,
            location=location,
            status=Status.objects.get(name="Active"),
        )

        Cable.objects.filter(_termination_a_device__in=[bb_rtr1, dist_rtr1]).delete()
        Cable.objects.filter(_termination_b_device__in=[bb_rtr1, dist_rtr1]).delete()

        interface_ct = ContentType.objects.get_for_model(Interface)

        # backbone router to distribution router
        Cable.objects.create(
            termination_a_id=bb_rtr1.interfaces.filter(name="eth1").first().id,
            termination_a_type=interface_ct,
            termination_b_id=dist_rtr1.interfaces.filter(name="eth1").first().id,
            termination_b_type=interface_ct,
            status=Status.objects.get(name="Connected"),
        )

        return [bb_rtr1, dist_rtr1]

    def medium_topology(self, device_type, device_role, location, platform, **kwargs):
        """For the medium topology, add redundant backbone and distribution routers."""
        bb_rtr2, _ = Device.objects.get_or_create(
            name="wan-rtr-bb2",
            device_type=device_type,
            role=device_role,
            platform=platform,
            location=location,
            status=Status.objects.get(name="Active"),
        )
        dist_rtr2, _ = Device.objects.get_or_create(
            name="dist-rtr2",
            device_type=device_type,
            role=device_role,
            platform=platform,
            location=location,
            status=Status.objects.get(name="Active"),
        )

        Cable.objects.filter(_termination_a_device__in=[bb_rtr2, dist_rtr2]).delete()
        Cable.objects.filter(_termination_b_device__in=[bb_rtr2, dist_rtr2]).delete()

        # backbone router cross-connects
        interface_ct = ContentType.objects.get_for_model(Interface)
        bb_rtr1 = Device.objects.get(name="wan-rtr-bb1")
        Cable.objects.create(
            termination_a_id=bb_rtr1.interfaces.filter(name="eth3").first().id,
            termination_a_type=interface_ct,
            termination_b_id=bb_rtr2.interfaces.filter(name="eth3").first().id,
            termination_b_type=interface_ct,
            status=Status.objects.get(name="Connected"),
        )
        Cable.objects.create(
            termination_a_id=bb_rtr1.interfaces.filter(name="eth4").first().id,
            termination_a_type=interface_ct,
            termination_b_id=bb_rtr2.interfaces.filter(name="eth4").first().id,
            termination_b_type=interface_ct,
            status=Status.objects.get(name="Connected"),
        )

        # backbone router to distribution router
        dist_rtr1 = Device.objects.get(name="dist-rtr1")
        Cable.objects.create(
            termination_a_id=bb_rtr2.interfaces.filter(name="eth2").first().id,
            termination_a_type=interface_ct,
            termination_b_id=dist_rtr1.interfaces.filter(name="eth2").first().id,
            termination_b_type=interface_ct,
            status=Status.objects.get(name="Connected"),
        )
        Cable.objects.create(
            termination_a_id=bb_rtr1.interfaces.filter(name="eth2").first().id,
            termination_a_type=interface_ct,
            termination_b_id=dist_rtr2.interfaces.filter(name="eth2").first().id,
            termination_b_type=interface_ct,
            status=Status.objects.get(name="Connected"),
        )
        Cable.objects.create(
            termination_a_id=bb_rtr2.interfaces.filter(name="eth1").first().id,
            termination_a_type=interface_ct,
            termination_b_id=dist_rtr2.interfaces.filter(name="eth1").first().id,
            termination_b_type=interface_ct,
            status=Status.objects.get(name="Connected"),
        )

        return [bb_rtr2, dist_rtr2]

    def large_topology(self, device_type, device_role, location, platform, **kwargs):
        """For the large topology, add a dmz router and datacenter switches."""
        dmz_rtr1, _ = Device.objects.get_or_create(
            name="dmz-rtr-bdr1",
            device_type=device_type,
            role=device_role,
            platform=platform,
            location=location,
            status=Status.objects.get(name="Active"),
        )
        dc_tor1, _ = Device.objects.get_or_create(
            name="dc-sw-tor1",
            device_type=device_type,
            role=device_role,
            platform=platform,
            location=location,
            status=Status.objects.get(name="Active"),
        )
        dc_tor2, _ = Device.objects.get_or_create(
            name="dc-sw-tor2",
            device_type=device_type,
            role=device_role,
            platform=platform,
            location=location,
            status=Status.objects.get(name="Active"),
        )
        dc_tor3, _ = Device.objects.get_or_create(
            name="dc-sw-tor3",
            device_type=device_type,
            role=device_role,
            platform=platform,
            location=location,
            status=Status.objects.get(name="Active"),
        )
        dc_tor4, _ = Device.objects.get_or_create(
            name="dc-sw-tor4",
            device_type=device_type,
            role=device_role,
            platform=platform,
            location=location,
            status=Status.objects.get(name="Active"),
        )

        Cable.objects.filter(_termination_a_device__in=[dmz_rtr1, dc_tor1, dc_tor2, dc_tor3, dc_tor4]).delete()
        Cable.objects.filter(_termination_b_device__in=[dmz_rtr1, dc_tor1, dc_tor2, dc_tor3, dc_tor4]).delete()

        # backbone routers to DMZ border router
        interface_ct = ContentType.objects.get_for_model(Interface)
        bb_rtr1 = Device.objects.get(name="wan-rtr-bb1")
        bb_rtr2 = Device.objects.get(name="wan-rtr-bb2")
        dist_rtr1 = Device.objects.get(name="dist-rtr1")
        dist_rtr2 = Device.objects.get(name="dist-rtr2")
        Cable.objects.create(
            termination_a_id=bb_rtr1.interfaces.filter(name="eth5").first().id,
            termination_a_type=interface_ct,
            termination_b_id=dmz_rtr1.interfaces.filter(name="eth1").first().id,
            termination_b_type=interface_ct,
            status=Status.objects.get(name="Connected"),
        )
        Cable.objects.create(
            termination_a_id=bb_rtr2.interfaces.filter(name="eth5").first().id,
            termination_a_type=interface_ct,
            termination_b_id=dmz_rtr1.interfaces.filter(name="eth2").first().id,
            termination_b_type=interface_ct,
            status=Status.objects.get(name="Connected"),
        )
        # distribution routers to datacenter ToR switches
        Cable.objects.create(
            termination_a_id=dist_rtr1.interfaces.filter(name="eth3").first().id,
            termination_a_type=interface_ct,
            termination_b_id=dc_tor1.interfaces.filter(name="eth1").first().id,
            termination_b_type=interface_ct,
            status=Status.objects.get(name="Connected"),
        )
        Cable.objects.create(
            termination_a_id=dist_rtr1.interfaces.filter(name="eth4").first().id,
            termination_a_type=interface_ct,
            termination_b_id=dc_tor2.interfaces.filter(name="eth1").first().id,
            termination_b_type=interface_ct,
            status=Status.objects.get(name="Connected"),
        )
        Cable.objects.create(
            termination_a_id=dist_rtr1.interfaces.filter(name="eth5").first().id,
            termination_a_type=interface_ct,
            termination_b_id=dc_tor3.interfaces.filter(name="eth1").first().id,
            termination_b_type=interface_ct,
            status=Status.objects.get(name="Connected"),
        )
        Cable.objects.create(
            termination_a_id=dist_rtr1.interfaces.filter(name="eth6").first().id,
            termination_a_type=interface_ct,
            termination_b_id=dc_tor4.interfaces.filter(name="eth1").first().id,
            termination_b_type=interface_ct,
            status=Status.objects.get(name="Connected"),
        )
        Cable.objects.create(
            termination_a_id=dist_rtr2.interfaces.filter(name="eth3").first().id,
            termination_a_type=interface_ct,
            termination_b_id=dc_tor1.interfaces.filter(name="eth2").first().id,
            termination_b_type=interface_ct,
            status=Status.objects.get(name="Connected"),
        )
        Cable.objects.create(
            termination_a_id=dist_rtr2.interfaces.filter(name="eth4").first().id,
            termination_a_type=interface_ct,
            termination_b_id=dc_tor2.interfaces.filter(name="eth2").first().id,
            termination_b_type=interface_ct,
            status=Status.objects.get(name="Connected"),
        )
        Cable.objects.create(
            termination_a_id=dist_rtr2.interfaces.filter(name="eth5").first().id,
            termination_a_type=interface_ct,
            termination_b_id=dc_tor3.interfaces.filter(name="eth2").first().id,
            termination_b_type=interface_ct,
            status=Status.objects.get(name="Connected"),
        )
        Cable.objects.create(
            termination_a_id=dist_rtr2.interfaces.filter(name="eth6").first().id,
            termination_a_type=interface_ct,
            termination_b_id=dc_tor4.interfaces.filter(name="eth2").first().id,
            termination_b_type=interface_ct,
            status=Status.objects.get(name="Connected"),
        )

        return [dmz_rtr1, dc_tor1, dc_tor2, dc_tor3, dc_tor4]
