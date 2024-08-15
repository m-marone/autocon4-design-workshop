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
)

menu_items = (
    NavMenuTab(
        name="Containerlab",
        groups=(NavMenuGroup(name="Containerlab", items=tuple(items)),),
    ),
)
