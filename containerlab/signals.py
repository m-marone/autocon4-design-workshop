"""Signals for Containerlab App."""

from nautobot.extras.models import Job, JobButton


def push_to_repo_job_button(sender, apps, **kwargs):  # pylint: disable=unused-argument
    """Enable Jobs."""
    job_receiver = Job.objects.get_for_class_path("containerlab.jobs.PushContainerlabTopologyToGit")
    job_receiver.enabled = True
    job_receiver.validated_save()

    Topology = sender.get_model("Topology")
    ContentType = apps.get_model("contenttypes", "ContentType")

    job_button_data = {
        "name": "Push Topology to Repo",
        "job": job_receiver,
        "text": "Push to Repo",
        "weight": 100,
        "button_class": "primary",
        "confirmation": True,
    }

    job_button, created = JobButton.objects.get_or_create(name=job_button_data["name"], defaults=job_button_data)
    if created:
        ct_id = ContentType.objects.get_for_model(Topology).id
        job_button.content_types.set([ct_id])
