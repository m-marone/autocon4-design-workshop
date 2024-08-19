"""Signals for Containerlab App."""

from nautobot.extras.models import Job, JobButton

TOPOLOGY_VIEW_BUTTONS = {
    "deploy_local_clab": {
        "job_class_path": "containerlab.jobs.DeployContainerTopologyToDocker",
        "job_button_data": {
            "name": "Deploy Topology",
            "job": "",
            "text": "Deploy Topology",
            "weight": 100,
            "button_class": "primary",
            "group_name": "Containerlab Actions",
            "confirmation": True,
        },
    },
    "destroy_local_clab": {
        "job_class_path": "containerlab.jobs.DestroyContainerTopologyToDocker",
        "job_button_data": {
            "name": "Destroy Topology",
            "job": "",
            "text": "Destroy Topology",
            "weight": 110,
            "button_class": "primary",
            "group_name": "Containerlab Actions",
            "confirmation": True,
        },
    },
    "push_topology_to_repo": {
        "job_class_path": "containerlab.jobs.PushContainerlabTopologyToGit",
        "job_button_data": {
            "name": "Push Topology to Repo",
            "job": "",
            "text": "Push topology file to Repo",
            "weight": 120,
            "button_class": "primary",
            "group_name": "Containerlab Actions",
            "confirmation": True,
        },
    },
}


def create_job_buttons(sender, apps, **kwargs):  # pylint: disable=unused-argument
    """Enable Jobs."""
    for data in TOPOLOGY_VIEW_BUTTONS.values():
        job_receiver = Job.objects.get_for_class_path(data["job_class_path"])
        job_receiver.enabled = True
        job_receiver.validated_save()

        data["job_button_data"]["job"] = job_receiver

        Topology = sender.get_model("Topology")
        ContentType = apps.get_model("contenttypes", "ContentType")

        job_button, created = JobButton.objects.get_or_create(
            name=data["job_button_data"]["name"],
            defaults=data["job_button_data"],
        )
        if created:
            ct_id = ContentType.objects.get_for_model(Topology).id
            job_button.content_types.set([ct_id])
