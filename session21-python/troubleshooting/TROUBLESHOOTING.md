# Kubernetes Troubleshooting Challenge & RCA Report

This document records the systematic diagnosis, root cause analysis (RCA), and remediation for the deliberately broken manifests in Session 21.

---

## Challenge 1: Broken Image (`broken-image.yaml`)

### Symptoms
When applying the manifest `kubectl apply -f troubleshooting/broken-image.yaml`, the pod failed to start.
```bash
$ kubectl apply -f troubleshooting/broken-image.yaml
deployment.apps/taskboard-broken-image created

$ kubectl get pods -n taskboard
NAME                                      READY   STATUS             RESTARTS   AGE
taskboard-broken-image-78d5985b9f-xkz92   0/1     ImagePullBackOff   0          42s
```

### Investigation
Inspect the pod events and container statuses using `kubectl describe`:
```bash
$ kubectl describe pod taskboard-broken-image-78d5985b9f-xkz92 -n taskboard
...
Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
  Normal   Scheduled  55s                default-scheduler  Successfully assigned taskboard/taskboard-broken-image-78d5985b9f-xkz92 to node-1
  Normal   Pulling    18s (x3 over 54s)  kubelet            Pulling image "ghcr.io/example/taskboard-backend:does-not-exist"
  Warning  Failed     17s (x3 over 53s)  kubelet            Failed to pull image "ghcr.io/example/taskboard-backend:does-not-exist": rpc error: code = NotFound desc = failed to pull and unpack image: not found
  Warning  Failed     17s (x3 over 53s)  kubelet            Error: ErrImagePull
  Normal   BackOff    5s (x4 over 52s)   kubelet            Back-off pulling image "ghcr.io/example/taskboard-backend:does-not-exist"
  Warning  Failed     5s (x4 over 52s)   kubelet            Error: ImagePullBackOff
```

### Root Cause
The deployment container spec referenced an invalid image repository and tag: `ghcr.io/example/taskboard-backend:does-not-exist`. The kubelet could not find or pull this image from the container registry.

### Remediation
Created `troubleshooting/fixed-image.yaml` with the correct image reference and image pull policy:
```yaml
spec:
  containers:
    - name: backend
      image: taskboard-backend:v1.0.0
      imagePullPolicy: IfNotPresent
      ports:
        - containerPort: 8000
```

### Verification
```bash
$ kubectl apply -f troubleshooting/fixed-image.yaml
deployment.apps/taskboard-fixed-image created

$ kubectl get pods -n taskboard -l app=fixed-backend
NAME                                     READY   STATUS    RESTARTS   AGE
taskboard-fixed-image-69f8d5bf9b-k4v7r   1/1     Running   0          14s
```

---

## Challenge 2: Broken Service (`broken-service.yaml`)

### Symptoms
When applying `broken-service.yaml`, client traffic to port 8080 fails with connection timed out / connection refused, and no backend endpoints receive traffic.
```bash
$ kubectl apply -f troubleshooting/broken-service.yaml
service/broken-service created

$ curl http://broken-service.taskboard.svc.cluster.local:8080
curl: (7) Failed to connect to broken-service.taskboard.svc.cluster.local port 8080: Connection refused
```

### Investigation
Check the service details and its corresponding Endpoints object:
```bash
$ kubectl get svc broken-service -n taskboard
NAME             TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
broken-service   ClusterIP   10.100.45.120   <none>        8080/TCP   30s

$ kubectl get endpoints broken-service -n taskboard
NAME             ENDPOINTS   AGE
broken-service   <none>      38s
```
Notice that `ENDPOINTS` is `<none>`. Next, inspect the pod labels in the namespace:
```bash
$ kubectl get pods -n taskboard --show-labels
NAME                                  READY   STATUS    RESTARTS   AGE   LABELS
taskboard-backend-67dfb6f5cb-4n9qp    1/1     Running   0          10m   app=taskboard-backend,release=taskboard
taskboard-frontend-7764dbcdb8-7c8vw   1/1     Running   0          10m   app=taskboard-frontend,release=taskboard

$ kubectl describe svc broken-service -n taskboard
Name:              broken-service
Namespace:         taskboard
Selector:          app=label-that-does-not-exist
Type:              ClusterIP
Port:              <unset>  8080/TCP
TargetPort:        8080/TCP
Endpoints:         <none>
```

### Root Cause
The Service definition specified `selector: {app: label-that-does-not-exist}`. Because no pods in the cluster carried the label `app=label-that-does-not-exist`, the Kubernetes endpoints controller did not populate any IP endpoints. Additionally, the backend was listening on port 8000, not 8080.

### Remediation
Created `troubleshooting/fixed-service.yaml` specifying the correct selector matching running backend pods (`app: taskboard-backend`) and matching target port (`targetPort: 8000`):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: fixed-service
  namespace: taskboard
spec:
  selector:
    app: taskboard-backend
  ports:
    - name: http
      port: 8000
      targetPort: 8000
```

### Verification
```bash
$ kubectl apply -f troubleshooting/fixed-service.yaml
service/fixed-service created

$ kubectl get endpoints fixed-service -n taskboard
NAME            ENDPOINTS            AGE
fixed-service   10.244.1.15:8000     8s

$ curl http://fixed-service.taskboard.svc.cluster.local:8000/health
{"status":"UP"}
```
Traffic is now correctly routed to the active pod instances.
