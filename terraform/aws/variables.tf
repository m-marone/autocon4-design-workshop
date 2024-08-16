variable "AWS_ACCESS_KEY" {
  type = string
}

variable "AWS_SECRET_KEY" {
  type = string
}

variable "region" {
  type = string
}

variable "zone" {
  type = string
}

variable "instance_ami" {
  type        = string
  description = "AMI ID"
  default     = "ami-024e6efaf93d85776"
}

# Pass in via Ansible
variable "instance_count" {
  type        = number
  description = "Number of instances to create"
  default     = 1
}

variable "instance_type" {
  type        = string
  description = "Instance type"
  default     = "e2-micro"
}

variable "instance_name" {
  type        = string
  description = "Name of the instance"
  default     = "TF Test Instance"
}