# DevSecOps Security Policy & Quality Gates

This repository enforces a strict Shift-Left Security policy across the CI/CD pipeline:
1. **SAST (Static Application Security Testing):** Code linting and automated unit tests block bad code at commit.
2. **SCA (Software Composition Analysis):** Trivy inspects open-source packages in `requirements.txt` and `package.json`.
3. **Secret Scanning:** Git hooks and GitHub Secret Scanning prohibit hardcoded keys, passwords, or tokens.
4. **Container Image Scanning:** Container images are evaluated for HIGH and CRITICAL CVEs prior to publishing to GHCR.
5. **Least Privilege Runtime:** All Kubernetes pods run with `securityContext.runAsNonRoot: true`.
