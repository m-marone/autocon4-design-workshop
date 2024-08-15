"""Containerlab Datasources."""
from nautobot.apps.datasources import DatasourceContent
from nautobot.extras.choices import LogLevelChoices


def refresh_git(repository_record, job_result, delete=False):  # pylint: disable=unused-argument
    """Callback for GitRepository updates on Containerlab repo."""
    job_result.log(
        "Successfully pulled Containerlab Lab repo",
        level_choice=LogLevelChoices.LOG_INFO,
    )


datasource_contents = [
    (
        "extras.gitrepository",
        DatasourceContent(
            name="containerlab topologies",
            content_identifier="containerlab.topology",
            icon="mdi-flask-outline",
            callback=refresh_git,
        ),
    )
]