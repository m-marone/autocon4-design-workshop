# ruff: noqa: D100, D101, D102, D103, PLR0915

from django.core.management.base import BaseCommand

from containerlab.models import Topology


class Command(BaseCommand):
    help = "Generate a clab.yml file from a Topology instance."

    def add_arguments(self, parser):
        parser.add_argument(
            "--topology",
            help="Name of the topology to use. Defaults to the first topology if not supplied.",
        )
        parser.add_argument(
            "--mgmt-network",
            help="Name of the docker network to use for the containerlab management network.",
        )
        parser.add_argument(
            "--mgmt-subnet",
            help="Subnet to use for the containerlab management network. CIDR Format.",
        )

    def handle(self, *args, **options):
        if options["topology"]:
            topology = Topology.objects.get(name=options["topology"])
        else:
            topology = Topology.objects.first()

        if not topology:
            self.stderr.write("No containerlab topology found.")
            return

        self.stdout.write(
            topology.generate_topology_file(mgmt_network=options["mgmt_network"], mgmt_subnet=options["mgmt_subnet"])
        )
