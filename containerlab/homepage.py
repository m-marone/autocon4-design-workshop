"""Homepage panels."""

from nautobot.apps.ui import HomePageItem, HomePagePanel

from containerlab.models import CLKind, Topology

layout = (
    HomePagePanel(
        name="Containerlab",
        weight=900,
        items=(
            HomePageItem(
                name="Kinds",
                link="plugins:containerlab:clkind_list",
                model=CLKind,
                description="Containerlab Kinds",
                permissions=["containerlab.view_clkind"],
                weight=100,
            ),
            HomePageItem(
                name="Topologies",
                link="plugins:containerlab:topology_list",
                model=Topology,
                description="Containerlab Topologies",
                permissions=["containerlab.view_topology"],
                weight=200,
            ),
        ),
    ),
)
