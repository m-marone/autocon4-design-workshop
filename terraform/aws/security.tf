# data "http" "myip" {
#   url = "http://ipv4.icanhazip.com"
# }

resource "aws_security_group" "clab_sg" {
  name_prefix = "clab-sg-"
  vpc_id      = aws_vpc.clab_vpc.id

  # SSH access
  ingress {
    description = "Allow SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Graphite access
  ingress {
    description = "Allow HTTP dev access"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # # ContainerLab Graph access
  # ingress {
  #   description = "Allow HTTP dev access to containerlab graph"
  #   from_port   = 50080
  #   to_port     = 50080
  #   protocol    = "tcp"
  #   cidr_blocks = ["${chomp(data.http.myip.response_body)}/32"]
  # }

  ingress {
    description = "Allow all inbound access"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}