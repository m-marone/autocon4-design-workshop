resource "aws_vpc" "clab_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "containerlab-vpc"
  }
}

resource "aws_eip" "clab_eip" {
  instance = aws_instance.clab[count.index].id
  domain   = "vpc"
  count    = var.instance_count
}