"""App declaration for containerlab."""

# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
from importlib import metadata

from nautobot.apps import NautobotAppConfig, nautobot_database_ready

# from .signals import push_to_repo_job_button

__version__ = metadata.version(__name__)


class ContainerlabConfig(NautobotAppConfig):
    """App configuration for the containerlab app."""

    name = "containerlab"
    verbose_name = "Containerlab"
    version = __version__
    author = "Network to Code, LLC"
    description = "Containerlab."
    base_url = "containerlab"
    required_settings = []
    min_version = "2.3.0"
    max_version = "2.9999"
    default_settings = {}
    caching_config = {}
    docs_view_name = "plugins:containerlab:docs"

    def ready(self):
        """Method to call signals."""
        super().ready()
        from containerlab.signals import create_job_buttons
        nautobot_database_ready.connect(create_job_buttons, sender=self)


config = ContainerlabConfig  # pylint:disable=invalid-name
