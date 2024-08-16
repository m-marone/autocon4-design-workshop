resource "aws_internet_gateway" "clab_igw" {
  vpc_id = aws_vpc.clab_vpc.id

  tags = {
    Name = "containerlab-ig"
  }
}