"""Containerlab Jobs."""

from pathlib import Path

from nautobot.apps.jobs import JobButtonReceiver, ObjectVar, register_jobs
from nautobot.core.utils.git import GitRepo as _GitRepo
from nautobot.extras.datasources.git import get_repo_from_url_to_path_and_from_branch
from nautobot.extras.jobs import get_task_logger
from nautobot.extras.models.datasources import GitRepository

from containerlab.models import Topology
from containerlab.exceptions import GitRepositoryNotFound

LOGGER = get_task_logger(__name__)


class GitRepo(_GitRepo):  # pylint: disable=too-many-instance-attributes
    """Git Repo object to help with git actions."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        path,
        url,
        clone_initially=True,
        base_url=None,
        nautobot_repo_obj=None,
    ):
        """Set attributes to easily interact with Git Repositories."""
        super().__init__(path, url, clone_initially)
        self.base_url = base_url
        self.nautobot_repo_obj = nautobot_repo_obj

    def commit_with_added(self, commit_description):
        """Make a force commit.

        Args:
            commit_description (str): the description of commit
        """
        LOGGER.debug("Committing with message `%s`", commit_description)
        self.repo.git.add(self.repo.untracked_files)
        self.repo.git.add(update=True)
        self.repo.index.commit(commit_description)
        LOGGER.debug("Commit completed")

    def push(self):
        """Push latest to the git repo."""
        LOGGER.debug("Push changes to repo")
        self.repo.remotes.origin.push().raise_if_error()


class PushContainerlabTopologyToGit(JobButtonReceiver):
    """Generate Containerlab Topology and push to git repo."""

    class Meta:
        """Meta class."""
        name = "Push Containerlab Topology to Remote Repository"

    def receive_job_button(self, obj):
        """Job run method."""
        topology = obj
        self.logger.info("Topology Model.", extra={"object": topology})
        try:
            topology_repo = GitRepository.objects.filter(provided_contents__contains='containerlab.topology')[0]
        except IndexError:
            msg = "Please configure a GitRepository that provides containerlab.topology content."
            self.logger.error(msg)
            raise GitRepositoryNotFound(msg)
        git_info = get_repo_from_url_to_path_and_from_branch(topology_repo)
        repo = GitRepo(
            topology_repo.filesystem_path,
            git_info.from_url,
            clone_initially=True,
            base_url=topology_repo.remote_url,
            nautobot_repo_obj=topology_repo,
        )

        topology_data = topology.generate_topology_file()
        # Should replace '/opt/nautobot' with $HOME/
        topology_path = f"/opt/nautobot/git/{topology_repo.slug}/containerlab_topologies/{topology.name}"

        Path(topology_path).mkdir(parents=True, exist_ok=True)

        with open(f"{topology_path}/{topology}.clab.yml", "w") as t_file:
            t_file.write(topology_data)
        repo.commit_with_added("Pushing to repo.")
        repo.push()


register_jobs(PushContainerlabTopologyToGit)
