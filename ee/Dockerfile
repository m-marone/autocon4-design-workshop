# Use the official AWX EE base image
FROM quay.io/ansible/awx-ee:latest

USER root

# Cryptography
RUN pip install --upgrade pip
RUN pip3 install cryptography

# Terraform
# Official documentation: https://developer.hashicorp.com/terraform/install
# RUN yum install -y yum-utils \
#   && yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo \
#   && yum install -y terraform \
#   && yum clean all

RUN yum install -y git
RUN curl https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo | tee /etc/yum.repos.d/terraform.repo
RUN yum install -y terraform

# Copy any custom requirements
RUN ansible-galaxy collection install community.general
RUN ansible-galaxy collection install community.docker
# COPY requirements.yml /requirements.yml
# RUN ansible-galaxy collection install -r /requirements.yml


# Set the entry point
# ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/ansible-runner", "worker", "--private-data-dir=/runner"]

# Fix a bug in the runner's home directory
RUN chown -R 1000:1000 /runner

# Drop back to the regular user (good practice)
USER 1000