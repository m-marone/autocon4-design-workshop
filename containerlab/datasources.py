"""Containerlab Datasources."""
import os

import yaml

from nautobot.apps.datasources import DatasourceContent
from nautobot.extras.choices import LogLevelChoices

from containerlab.models import TopologyTemplate


def refresh_git_clab_topologies(repository_record, job_result, delete=False):
    """Callback for GitRepository updates on Containerlab repo."""
    if 'containerlab.topology' not in repository_record.provided_contents or delete:
        return
    job_result.log(
        "Successfully pulled Containerlab Topologies repo",
        level_choice=LogLevelChoices.LOG_INFO,
    )

def refresh_git_clab_templates(repository_record, job_result, delete=False):
    """Callback for GitRepository updates on Containerlab repo."""
    if 'containerlab.template' not in repository_record.provided_contents or delete:
        return
    job_result.log(
        "Successfully pulled Containerlab Template repo",
        level_choice=LogLevelChoices.LOG_INFO,
    )
    template_path = os.path.join(repository_record.filesystem_path, 'clab_topology_templates')
    for filename in os.listdir(template_path):
        with open(os.path.join(template_path, filename)) as fd:
            template_contents = fd.read()
        try:
            # Always update template content
            obj = TopologyTemplate.objects.get(name=filename)
            obj.template_content = template_contents
            obj.validated_save()
            job_result.log(
                f"Updated template `{filename}`",
                level_choice=LogLevelChoices.LOG_INFO,
            )
        except TopologyTemplate.DoesNotExist:
            TopologyTemplate.objects.create(name=filename, template_content=template_contents)
            job_result.log(
                f"Created template `{filename}`",
                level_choice=LogLevelChoices.LOG_INFO,
            )

datasource_contents = [
    (
        "extras.gitrepository",
        DatasourceContent(
            name="containerlab topologies",
            content_identifier="containerlab.topology",
            icon="mdi-flask-outline",
            callback=refresh_git_clab_topologies,
        ),
    ),
    (
        "extras.gitrepository",
        DatasourceContent(
            name="containerlab templates",
            content_identifier="containerlab.template",
            icon="mdi-flask-outline",
            callback=refresh_git_clab_templates,
        ),
    )
]
