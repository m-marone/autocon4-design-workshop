terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~>4.0"
    }
  }
  backend "s3" {
    bucket         = "ntc-containerlab-hackathon-2024"   # Replace with your S3 bucket name
    key            = "terraform.tfstate"                 # Path within the bucket to store the state file
    region         = "us-east-2"                         # Replace with your desired AWS region
    encrypt        = true                                # Encrypt the state file at rest
    dynamodb_table = "ntc-containerlab-hackathon-2024"   # Optional: Replace with your DynamoDB table name for state locking
  }
}

provider "aws" {
  region     = var.region
  access_key = var.AWS_ACCESS_KEY
  secret_key = var.AWS_SECRET_KEY
}

provider "tls" {}