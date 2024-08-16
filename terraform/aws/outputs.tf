output "instance_private_ip" {
  value = aws_instance.clab.*.private_ip
}

output "instance_public_ip" {
  value = aws_eip.clab_eip.*.public_ip
}

output "instance_id" {
  value = aws_instance.clab.*.id
}