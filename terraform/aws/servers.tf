resource "tls_private_key" "ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "local_file" "ssh_private_key_pem" {
  content         = tls_private_key.ssh.private_key_pem
  filename        = ".ssh/aws_clab"
  file_permission = "0600"
}

resource "aws_key_pair" "clab_ssh_key" {
  key_name   = "clab-key"
  public_key = tls_private_key.ssh.public_key_openssh
}

resource "aws_instance" "clab" {
  ami           = var.instance_ami
  instance_type = var.instance_type
  key_name      = aws_key_pair.clab_ssh_key.key_name
  subnet_id     = aws_subnet.clab_subnet.id
  count         = var.instance_count
  ebs_block_device {
    device_name           = "/dev/sda1"
    volume_size           = 25
    volume_type           = "gp2"
    encrypted             = false
    delete_on_termination = true
  }

  vpc_security_group_ids = [aws_security_group.clab_sg.id]

  tags = {
    Name = "${var.instance_name}-${count.index + 1}"
  }
}