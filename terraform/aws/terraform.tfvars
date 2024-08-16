# AWS project information
region = "us-east-2"
zone   = "us-east-2a"

# Instance information
# instance_count = 1
# instance_ami = "ami-053b0d53c279acc90" # x86 in us-east-1 - base image
# instance_ami = "ami-024e6efaf93d85776" # x86 in us-east-2 - base image
# instance_ami = "ami-079541252237005bb" # preconfigured x86 image in us-east-2 no ngrok
instance_ami = "ami-0fafd7eda4e437d93" # preconfigured x86 image in us-east-2 with ngrok
# instance_ami = "ami-0e0b43751c75b1488" # clab-ami-learn with packer
# instance_type  = "m5ad.2xlarge" # "t2.2xlarge" or better is recommended
instance_type  = "t2.2xlarge" # "t2.2xlarge" or better is recommended
instance_name  = "clab-test-instance"