"""Containerlab Jobs."""

import platform
from pathlib import Path

import docker
from django.utils.text import slugify
from nautobot.apps.jobs import (
    JobButtonReceiver,
    register_jobs,
)
from nautobot.core.utils.git import GitRepo as _GitRepo
from nautobot.extras.datasources.git import get_repo_from_url_to_path_and_from_branch
from nautobot.extras.jobs import get_task_logger
from nautobot.extras.models.datasources import GitRepository

from containerlab.exceptions import GitRepositoryNotFound
from containerlab.models import Topology

LOGGER = get_task_logger(__name__)


def deploy_clab(job_obj, topology, action="deploy"):
    """Deploy containerlab topology to local environment."""
    job_obj.logger.info("Topology Model.", extra={"object": topology})
    docker_client = docker.from_env()
    worker_container = None
    docker_containers = docker_client.containers.list()
    possible_container_names = [platform.node(), platform.node().split(".")[0]]
    job_obj.logger.debug(
        "Trying to find worker container in docker using names: %s",
        possible_container_names,
    )
    for container in docker_containers:
        if (
            container.id in possible_container_names
            or container.short_id in possible_container_names
        ):
            worker_container = container
            break
    if worker_container is None:
        raise RuntimeError(
            "Unable to locate worker in docker. Ensure the worker is a docker container and the host docker socket is mounted at /var/run/docker.sock."
        )
    worker_container.reload()

    # Generate the topology data using the worker's network name and subnet
    if len(worker_container.attrs["NetworkSettings"]["Networks"]) != 1:
        raise RuntimeError("Worker container cannot be connected to multiple networks.")
    worker_network_name = list(
        worker_container.attrs["NetworkSettings"]["Networks"].keys()
    )[0]
    worker_network_subnet = docker_client.networks.get(worker_network_name).attrs[
        "IPAM"
    ]["Config"][0]["Subnet"]
    topology_data = topology.generate_topology_file(
        mgmt_network=worker_network_name, mgmt_subnet=worker_network_subnet
    )

    # Find an appropriate mount to write the topology file (a bind mounted directory that is mounted read-write)
    topology_worker_path = None
    topology_host_path = None
    for mount in worker_container.attrs["Mounts"]:
        if (
            mount["Type"] == "bind"
            and mount["Mode"] == "rw"
            and Path(mount["Destination"]).is_dir()
        ):
            topology_worker_path = mount["Destination"]
            topology_host_path = mount["Source"]
            break

    if not topology_worker_path:
        raise RuntimeError(
            "Unable to find a suitable bind mount directory to write the topology file. Ensure at least one volume is mounted read-write."
        )

    # Find the host's docker socket path
    docker_socket_mount = [
        m
        for m in worker_container.attrs["Mounts"]
        if m["Destination"] == "/var/run/docker.sock"
    ]
    if not docker_socket_mount:
        raise RuntimeError(
            "Unable to find the docker socket path. Ensure the host's docker socket is mounted at /var/run/docker.sock."
        )
    else:
        host_docker_socket_path = docker_socket_mount[0]["Source"]

    # Write the topology file
    yaml_file_path = Path(topology_worker_path) / f"{slugify(topology.name)}.yml"
    yaml_file_path.write_text(topology_data)
    job_obj.logger.info(
        f"Topology file written to {topology_host_path}/{slugify(topology.name)}.yml on the host."
    )

    # Run containerlab to deploy/destroy the topology
    job_obj.logger.info("%sing topology with containerlab.", action.capitalize())
    docker_output = docker_client.containers.run(
        "ghcr.io/srl-labs/clab",
        command=f"containerlab {action} --topo {slugify(topology.name)}.yml",
        volumes={
            host_docker_socket_path: {"bind": "/var/run/docker.sock", "mode": "rw"},
            topology_host_path: {"bind": topology_host_path, "mode": "rw"},
            "/var/run/netns": {"bind": "/var/run/netns", "mode": "rw"},
            "/etc/hosts": {"bind": "/etc/hosts", "mode": "rw"},
            "/var/lib/docker/containers": {
                "bind": "/var/lib/docker/containers",
                "mode": "rw",
            },
        },
        working_dir=topology_host_path,
        network_mode="host",
        pid_mode="host",
        privileged=True,
        remove=True,
    )

    job_obj.logger.info("Topology %sed.", action)
    if docker_output.decode():
        job_obj.logger.info("```%s```", docker_output.decode())


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
            topology_repo = GitRepository.objects.filter(
                provided_contents__contains="containerlab.topology"
            )[0]
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


class DeployContainerTopologyToDocker(JobButtonReceiver):
    """Deploy Containerlab Topology to Docker."""

    class Meta:
        name = "Deploy Containerlab Topology to Docker"
        description = """
            Deploy Containerlab Topology to Docker.
            This only works if your Nautobot and worker instances are running in the same docker compose network!
        """

    def receive_job_button(self, obj):
        """Receive job button method."""
        deploy_clab(self, obj, action="deploy")


class DestroyContainerTopologyToDocker(JobButtonReceiver):
    """Destroy a running Containerlab Topology in Docker."""

    class Meta:
        name = "Destroy a running Containerlab Topology in Docker"
        description = """
            Destroy a running Containerlab Topology in Docker.
            This only works if your Nautobot and worker instances are running in the same docker compose network!
        """

    def receive_job_button(self, obj):
        """Receive job button method."""
        deploy_clab(self, obj, action="destroy")


register_jobs(
    PushContainerlabTopologyToGit,
    DeployContainerTopologyToDocker,
    DestroyContainerTopologyToDocker,
)
