resource "aws_subnet" "clab_subnet" {
  cidr_block        = "10.0.1.0/24"
  vpc_id            = aws_vpc.clab_vpc.id
  availability_zone = var.zone
  tags = {
    Name = "containerlab-subnet"
  }
}

resource "aws_route_table" "clab-rt" {
  vpc_id = aws_vpc.clab_vpc.id

  tags = {
    Name = "containerlab-route-table"
  }
}

resource "aws_route" "clab-route" {
  route_table_id         = aws_route_table.clab-rt.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.clab_igw.id
}

resource "aws_route_table_association" "clab-subnet-association" {
  subnet_id      = aws_subnet.clab_subnet.id
  route_table_id = aws_route_table.clab-rt.id
}