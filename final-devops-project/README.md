# Final DevOps Capstone Project

## Project overview
This final capstone project demonstrates an end-to-end DevOps lifecycle from development to production monitoring. The project implements a complete microservices architecture featuring:
- **Application:** React + Vite frontend, FastAPI Python backend, PostgreSQL database with SQLAlchemy and Alembic migrations.
- **Containerization:** Multi-stage Docker builds running as non-root users and Docker Compose for local orchestration.
- **Continuous Integration:** GitHub Actions automated testing (Pytest), frontend build, and Docker builds.
- **DevSecOps:** Shift-left security with Trivy container vulnerability scanning and GitHub secret detection.
- **Infrastructure as Code:** Terraform scripts provisioning an AWS VPC with public/private subnets and an Amazon EKS cluster with managed node groups.
- **Kubernetes Orchestration:** Deployments, ClusterIP Services, Ingress with NGINX controller, Horizontal Pod Autoscaler (HPA), and persistent storage (PVC).
- **Package Management:** Modular Helm chart with environment-specific values (`values-dev.yaml`, `values-prod.yaml`).
- **Observability:** Prometheus scraping application `/metrics` via ServiceMonitor, and Grafana dashboards for cluster and application telemetry.
- **GitOps:** Continuous reconciliation with ArgoCD syncing manifests from Git to Kubernetes.
- **Troubleshooting:** Real-world incident response and Root Cause Analysis (RCA) for simulated failures.

```text
final-devops-project/
├── application/
│   ├── backend/               # FastAPI, SQLAlchemy, Alembic, Pytest
│   └── frontend/              # React 18, Vite, responsive UI
├── docker/
│   ├── Dockerfile.backend     # Python 3.12 slim, non-root user
│   ├── Dockerfile.frontend    # Multi-stage Node 20 build -> Nginx Alpine
│   └── docker-compose.yml     # Complete local stack
├── kubernetes/
│   ├── namespace.yaml         # Isolated namespace
│   ├── backend-deployment.yaml# Deployments with probes and resource limits
│   ├── backend-service.yaml   # ClusterIP service
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── postgres.yaml          # StatefulSet with PVC
│   ├── ingress.yaml           # Nginx Ingress routing
│   ├── hpa.yaml               # Autoscaling based on CPU
│   ├── configmap.yaml
│   └── secret.yaml
├── helm/
│   └── capstone-chart/        # Templated Helm chart
├── terraform/
│   ├── versions.tf            # Provider configuration
│   ├── variables.tf           # Configurable inputs
│   ├── main.tf                # VPC, subnets, IGW, EKS cluster
│   ├── outputs.tf             # EKS endpoint and kubeconfig command
│   └── terraform.tfvars.example
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # GitHub Actions test, scan, and push
├── security/
│   ├── trivy-scan.sh          # Container scanning script
│   └── security-policy.md     # DevSecOps quality gate standards
├── monitoring/
│   ├── prometheus-values.yaml # Helm values for Prometheus operator
│   ├── servicemonitor.yaml    # ServiceMonitor for FastAPI /metrics
│   └── grafana-dashboard.json # Grafana monitoring dashboard
├── gitops/
│   └── argocd-application.yaml# ArgoCD declarative GitOps application
└── README.md
```

## Architecture diagram
```mermaid
graph TD
    Dev["Developer Workstation"] -->|"Git Commit & Push"| GitHub["GitHub Repository"]
    GitHub -->|"Webhook Trigger"| GHA["GitHub Actions CI/CD"]
    subgraph CI_Pipeline ["Continuous Integration & DevSecOps"]
        GHA -->|"1. Run Tests"| Pytest["Pytest Test Suite"]
        GHA -->|"2. Build Frontend"| Vite["Vite Production Build"]
        GHA -->|"3. Containerize"| Docker["Docker Multi-Stage Build"]
        GHA -->|"4. Vulnerability Scan"| Trivy["Trivy Security Gate"]
        Trivy -->|"Pass: Push Image"| GHCR["GitHub Container Registry"]
    end
    subgraph Cloud_Infra ["AWS Cloud Infrastructure - Terraform"]
        TF["Terraform"] -->|"Provision"| VPC["AWS VPC & Subnets"]
        TF -->|"Provision"| EKS["Amazon EKS Cluster"]
    end
    subgraph K8s_Cluster ["Kubernetes Cluster"]
        GHCR -.->|"Pull Images"| Deployments["Pods & Deployments"]
        ArgoCD["ArgoCD GitOps"] -->|"Reconcile State"| Deployments
        Ingress["NGINX Ingress Controller"] -->|"Route /api"| Backend["FastAPI Backend"]
        Ingress -->|"Route /"| Frontend["React Frontend"]
        Backend -->|"SQLAlchemy"| Postgres[("PostgreSQL Database")]
        HPA["Horizontal Pod Autoscaler"] -->|"Auto-scale"| Backend
    end
    subgraph Observability_Stack ["Monitoring & Telemetry"]
        Backend -->|"Expose"| Metrics["/metrics Endpoint"]
        Prometheus["Prometheus Operator"] -->|"Scrape"| Metrics
        Prometheus -->|"Visualize"| Grafana["Grafana Dashboards"]
    end
```

## Technologies used
- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, Uvicorn
- **Frontend:** React 18, Vite, Vanilla CSS Design System, Responsive HTML5/JSX
- **Database:** PostgreSQL 16
- **Testing:** Pytest, HTTPX, FastAPI TestClient
- **Containerization:** Docker, Docker Compose, Multi-stage builds
- **Cloud Infrastructure:** AWS (VPC, Subnets, Internet Gateway, NAT Gateway, EKS Cluster, IAM)
- **Infrastructure as Code:** Terraform (AWS Provider v5.x)
- **Container Orchestration:** Kubernetes (v1.28+), Helm v3
- **CI/CD:** GitHub Actions (Actions Runner, GHCR)
- **DevSecOps:** Trivy Container Scanner, GitHub Secret Scanning, Non-root runtime policies
- **Observability:** Prometheus Operator, Grafana, prometheus-fastapi-instrumentator
- **GitOps:** ArgoCD

## Application setup
To run the application natively on a developer machine:

### Backend:
```bash
cd application/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql+psycopg://devops_user:devops_secure_password@localhost:5432/capstone_db"
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend:
```bash
cd application/frontend
npm install
npm run dev
```

### Automated Testing:
```bash
cd application/backend
pytest -v
```

## Docker setup
The application is fully containerized with security and minimal image footprints in mind:
- **Backend:** Based on `python:3.12-slim`, utilizes non-root system user `appuser:10001`.
- **Frontend:** Multi-stage build (Stage 1 compiles static assets using Node 20; Stage 2 serves assets through high-performance Nginx Alpine).

### Running locally with Docker Compose:
```bash
cd docker
docker compose up --build
```
Access endpoints:
- Frontend: `http://localhost:3000`
- Backend API Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
- Metrics: `http://localhost:8000/metrics`

```bash
# Verify running containers
$ docker compose ps
NAME                IMAGE                  COMMAND                  SERVICE    CREATED          STATUS                    PORTS
capstone-backend    docker-backend         "uvicorn app.main:ap…"   backend    10 seconds ago   Up 9 seconds              0.0.0.0:8000->8000/tcp
capstone-frontend   docker-frontend        "nginx -g 'daemon of…"   frontend   10 seconds ago   Up 9 seconds              0.0.0.0:3000->80/tcp
capstone-postgres   postgres:16-alpine     "docker-entrypoint.s…"   postgres   10 seconds ago   Up 9 seconds (healthy)    0.0.0.0:5432->5432/tcp
```

## Kubernetes deployment
Deploy manifests natively to Kubernetes:
```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secret.yaml
kubectl apply -f kubernetes/postgres.yaml
kubectl apply -f kubernetes/backend-deployment.yaml
kubectl apply -f kubernetes/backend-service.yaml
kubectl apply -f kubernetes/frontend-deployment.yaml
kubectl apply -f kubernetes/frontend-service.yaml
kubectl apply -f kubernetes/ingress.yaml
kubectl apply -f kubernetes/hpa.yaml
```

Verification:
```bash
$ kubectl get pods -n devops-production
NAME                        READY   STATUS    RESTARTS   AGE
backend-647bfbc58f-4g7lq    1/1     Running   0          45s
backend-647bfbc58f-9d2ks    1/1     Running   0          45s
frontend-78bd6c8d7b-2m6tz   1/1     Running   0          40s
frontend-78bd6c8d7b-8jkl3   1/1     Running   0          40s
postgres-0                  1/1     Running   0          55s
```

## Helm deployment
The application is packaged into a reusable Helm chart located in `helm/capstone-chart`:
```bash
# Lint the chart
helm lint helm/capstone-chart

# Install / Upgrade Release
helm upgrade --install capstone-release ./helm/capstone-chart \
  --namespace devops-production \
  --create-namespace \
  -f helm/capstone-chart/values-prod.yaml
```

```bash
$ helm list -n devops-production
NAME              NAMESPACE          REVISION    UPDATED                                STATUS      CHART                 APP VERSION
capstone-release  devops-production  1           2026-10-16 20:50:12.435921 +0530 IST   deployed    capstone-app-1.0.0    1.0.0
```

## Terraform infrastructure
Infrastructure as Code manages the entire AWS foundational footprint:
```bash
cd terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

Components provisioned:
1. Custom VPC (`10.0.0.0/16`) with DNS support and hostnames enabled.
2. Two Public Subnets across multiple Availability Zones (`ap-south-1a`, `ap-south-1b`).
3. Internet Gateway (IGW) and public route tables.
4. AWS IAM Roles and Policies for EKS cluster control plane.
5. Amazon EKS Cluster with managed Kubernetes control plane.

```bash
$ terraform plan
Plan: 10 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + cluster_endpoint   = (known after apply)
  + cluster_name       = "capstone-eks-cluster"
  + kubeconfig_command = "aws eks update-kubeconfig --region ap-south-1 --name capstone-eks-cluster"
  + vpc_id             = (known after apply)
```

## CI/CD pipeline
Automated CI/CD is implemented via GitHub Actions (`.github/workflows/ci-cd.yml`):
- **Triggers:** Push and pull requests targeting branch `main`.
- **Job 1 (Test):** Sets up Python 3.12, installs dependencies, executes `pytest -v` test suite, installs Node 20, and runs `npm run build`.
- **Job 2 (Security Scan):** Builds container images and executes Trivy vulnerability scans for HIGH and CRITICAL vulnerabilities.
- **Job 3 (Build & Push):** Authenticates with GitHub Container Registry (GHCR) and pushes images tagged with the immutable commit SHA (`${{ github.sha }}`) and `latest`.

## DevSecOps implementation
Security is integrated at every phase:
1. **Static Analysis & Linting:** Automated unit testing and syntax validation.
2. **Container Image Scanning (Trivy):** Scans OS packages and application dependencies for CVEs. The pipeline fails on HIGH or CRITICAL issues:
   ```bash
   trivy image --severity HIGH,CRITICAL --exit-code 1 local/backend:${{ github.sha }}
   ```
3. **Secret Protection:** No hardcoded database passwords or cloud tokens in Git. Secrets are managed via Kubernetes Secret objects and injected via environment variables.
4. **Least-Privilege Containers:** Containers do not run as root (`runAsNonRoot: true`, user `10001` for backend, user `101` for frontend).

## Monitoring
Observability is provided by Prometheus and Grafana:
- Backend exposes metrics via `/metrics` using `prometheus-fastapi-instrumentator`.
- `ServiceMonitor` resources configure Prometheus Operator to scrape metrics every 15 seconds.
- Grafana dashboard visualizes:
  - Total HTTP request throughput
  - P95 / P99 request latency
  - HTTP 4xx and 5xx error distribution
  - Pod CPU and memory utilization

```bash
$ curl -s http://localhost:8000/metrics | head -n 15
# HELP http_requests_total Total number of HTTP requests processed.
# TYPE http_requests_total counter
http_requests_total{handler="/health",method="GET",status="200"} 12
http_requests_total{handler="/ready",method="GET",status="200"} 12
http_requests_total{handler="/api/tasks",method="GET",status="200"} 34
```

## GitOps
Continuous deployment and configuration synchronization are achieved using ArgoCD:
- ArgoCD monitors the Git repository at `final-devops-project/kubernetes`.
- When changes are merged into `main`, ArgoCD detects the configuration drift and reconciles the desired state on the Kubernetes cluster.
- `automated.prune: true` ensures deleted resources are removed.
- `automated.selfHeal: true` prevents unauthorized manual overrides.

## Troubleshooting
### Incident 1: Backend CrashLoopBackOff (Database Connection Error)
- **Symptom:** Backend Pod shows status `CrashLoopBackOff` upon rollout.
- **Investigation:**
  ```bash
  $ kubectl get pods -n devops-production
  backend-647bfbc58f-4g7lq   0/1   CrashLoopBackOff   3   2m

  $ kubectl logs backend-647bfbc58f-4g7lq -n devops-production
  psycopg.OperationalError: [Errno 111] Connection refused
  ```
- **Root Cause:** The secret `DATABASE_URL` contained `postgres:5432` instead of the Kubernetes cluster DNS name `postgres-service:5432`.
- **Resolution:** Updated `kubernetes/secret.yaml` with the correct service DNS endpoint and executed `kubectl rollout restart deployment backend -n devops-production`.

### Incident 2: Ingress 502 Bad Gateway
- **Symptom:** Browser requests to `http://devops-capstone.local/api` return `502 Bad Gateway`.
- **Investigation:**
  ```bash
  $ kubectl get endpoints backend-service -n devops-production
  NAME              ENDPOINTS   AGE
  backend-service   <none>      5m
  ```
- **Root Cause:** The service selector was mismatched (`app: backend-api` instead of `app: backend`).
- **Resolution:** Corrected `selector: { app: backend }` in `backend-service.yaml`. The endpoints populated immediately and traffic resolved with HTTP 200 OK.

## Screenshots
```text
=== Local Full-Stack Startup Output ===
$ docker compose up -d
[+] Running 4/4
 ✔ Network docker_default         Created                                                              0.0s 
 ✔ Container capstone-postgres    Healthy                                                              1.2s 
 ✔ Container capstone-backend     Started                                                              1.5s 
 ✔ Container capstone-frontend    Started                                                              1.6s 

=== Automated Pytest Verification ===
$ pytest -v
tests/test_api.py::test_root PASSED                                      [  9%]
tests/test_api.py::test_health PASSED                                    [ 18%]
tests/test_api.py::test_ready PASSED                                     [ 27%]
tests/test_api.py::test_metrics_endpoint PASSED                          [ 36%]
tests/test_api.py::test_create_task PASSED                               [ 45%]
tests/test_api.py::test_list_tasks PASSED                                [ 54%]
tests/test_api.py::test_get_task_by_id PASSED                            [ 63%]
tests/test_api.py::test_update_task PASSED                               [ 72%]
tests/test_api.py::test_stats PASSED                                     [ 81%]
tests/test_api.py::test_get_task_not_found PASSED                        [ 90%]
tests/test_api.py::test_delete_task PASSED                               [100%]
======================== 11 passed in 0.41s ========================

=== Kubernetes Cluster Workloads ===
$ kubectl get all -n devops-production
NAME                            READY   STATUS    RESTARTS   AGE
pod/backend-647bfbc58f-4g7lq    1/1     Running   0          10m
pod/backend-647bfbc58f-9d2ks    1/1     Running   0          10m
pod/frontend-78bd6c8d7b-2m6tz   1/1     Running   0          10m
pod/frontend-78bd6c8d7b-8jkl3   1/1     Running   0          10m
pod/postgres-0                  1/1     Running   0          12m

NAME                       TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
service/backend-service    ClusterIP   10.100.124.55    <none>        8000/TCP   10m
service/frontend-service   ClusterIP   10.100.180.12    <none>        80/TCP     10m
service/postgres-service   ClusterIP   10.100.210.89    <none>        5432/TCP   12m

NAME                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/backend    2/2     2            2           10m
deployment.apps/frontend   2/2     2            2           10m

NAME                                  REFERENCE            TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
horizontalpodautoscaler.autoscaling   Deployment/backend   cpu: 12% / 70%   2         8         2          10m
```

## Lessons learned
- **Automated Quality Gates:** Running tests and container security scanning in GitHub Actions prevents flawed code and vulnerable packages from ever reaching container registries or clusters.
- **Infrastructure as Code (IaC) Reproducibility:** Provisioning AWS EKS and networking through Terraform guarantees deterministic, repeatable infrastructure setups that eliminate manual drift.
- **GitOps for Stability:** Leveraging Git as the single source of truth with ArgoCD ensures transparent audit logs, effortless rollbacks, and zero configuration drift in production environments.
- **Deep Observability:** Exposing Prometheus metrics at the application layer combined with Grafana dashboards empowers teams to proactively identify bottlenecks before users experience downtime.
