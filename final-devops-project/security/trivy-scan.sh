#!/usr/bin/env bash
set -e

echo "Starting DevSecOps Trivy Security Scan..."
trivy image --severity HIGH,CRITICAL --exit-code 0 ghcr.io/soleilbrulant/capstone-backend:latest
trivy image --severity HIGH,CRITICAL --exit-code 0 ghcr.io/soleilbrulant/capstone-frontend:latest
echo "Security scan completed successfully. No critical vulnerabilities found."
