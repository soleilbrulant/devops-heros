variable "aws_region" {
  type        = string
  default     = "ap-south-1"
  description = "AWS region for deployment"
}

variable "environment" {
  type        = string
  default     = "production"
  description = "Deployment environment"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
  description = "VPC CIDR block"
}

variable "cluster_name" {
  type        = string
  default     = "capstone-eks-cluster"
  description = "EKS Cluster Name"
}
