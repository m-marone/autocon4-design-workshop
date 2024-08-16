"""Menu items."""

from nautobot.apps.ui import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuTab

items = (
    NavMenuItem(
        link="plugins:containerlab:topology_list",
        name="Topologies",
        permissions=["containerlab.view_topology"],
        buttons=(
            NavMenuAddButton(
                link="plugins:containerlab:topology_add",
                permissions=["containerlab.add_topology"],
            ),
        ),
    ),
    NavMenuItem(
        link="plugins:containerlab:clkind_list",
        name="Kinds",
        permissions=["containerlab.view_clkind"],
        buttons=(
            NavMenuAddButton(
                link="plugins:containerlab:clkind_add",
                permissions=["containerlab.add_clkind"],
            ),
        ),
    ),
)

menu_items = (
    NavMenuTab(
        name="Containerlab",
        groups=(NavMenuGroup(name="Containerlab", items=tuple(items)),),
    ),
)
