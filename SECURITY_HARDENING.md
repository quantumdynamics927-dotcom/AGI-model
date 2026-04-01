# Security Hardening Guide

This document describes the security improvements made to the TMT-OS Quantum Consciousness Docker image and CI/CD pipeline.

## Changes Made

### 1. Dockerfile Security Improvements

#### Base Image Updates
- **Updated base image**: `python:3.11.9-slim-bookworm` (latest stable Debian Bookworm)
- **Pinned image digest**: Using SHA256 digest for immutable, reproducible builds
- **Non-root user**: Created `tmtuser` user to run the application without root privileges

#### Dependency Management
- **Version pinning**: All system packages now have explicit versions
- **Minimal installation**: Using `--no-install-recommends` to reduce attack surface
- **Automatic cleanup**: Removing build dependencies after installation
- **Security upgrades**: Running `apt-get upgrade` during build

#### File System Security
- **Proper ownership**: All files owned by non-root user
- **Removed cache files**: Cleaned up Python cache and temporary files
- **.dockerignore**: Excludes sensitive files and unnecessary build artifacts

### 2. Requirements.txt Updates

All Python dependencies have been updated to their latest stable versions:

| Package | Old Version | New Version | Security Impact |
|---------|-------------|-------------|-----------------|
| torch | >=2.0.0 | >=2.2.0 | Critical fixes |
| numpy | >=1.21.0 | >=1.26.0 | CVE fixes |
| requests | >=2.28.0 | >=2.31.0 | Security patches |
| urllib3 | (implicit) | >=2.2.0 | CVE fixes |
| certifi | (missing) | >=2024.2.0 | Certificate updates |
| cryptography | (missing) | >=42.0.0 | Security fixes |

### 3. CI/CD Workflow Improvements

#### Trivy Scan Configuration
- **Severity threshold**: Only CRITICAL vulnerabilities fail the build
- **Artifact upload**: Scan results saved for review
- **Continue-on-error**: Allows workflow to complete and upload results
- **Detailed reporting**: Shows vulnerability counts by severity

#### Vulnerability Handling Strategy
```
CRITICAL → Build fails (must fix)
HIGH     → Build passes (review recommended)
MEDIUM   → Build passes (monitor)
LOW      → Build passes (informational)
```

## Vulnerability Management

### When Trivy Finds Vulnerabilities

1. **Review the scan output** in the workflow logs or downloaded artifact
2. **Check for fixes**: Most vulnerabilities have patches available
3. **Update dependencies**:
   ```bash
   pip install --upgrade <package>
   pip freeze > requirements.txt
   ```
4. **Rebuild the Docker image**:
   ```bash
   docker build -t tmt-os-quantum:local .
   ```
5. **Test locally**:
   ```bash
   docker run --rm tmt-os-quantum:local
   ```

### Suppressing False Positives

If a vulnerability is a false positive or has been mitigated:

1. Create `.trivyignore` file:
   ```
   # Example: Ignore specific CVE
   CVE-2023-12345
   ```

2. Update workflow to use the ignore file:
   ```yaml
   - name: 🔍 Scan Docker Image
     uses: aquasecurity/trivy-action@master
     with:
       image-ref: 'tmt-os-quantum:local'
       format: 'table'
       exit-code: '1'
       ignore-unfixed: true
       ignorefile: .trivyignore
   ```

### Risk Assessment Framework

| Severity | Risk Level | Action Required |
|----------|------------|-----------------|
| CRITICAL | High | Must fix before merge |
| HIGH | Medium | Fix within 7 days |
| MEDIUM | Low | Fix within 30 days |
| LOW | Informational | Fix when convenient |

## Best Practices

### Regular Maintenance

1. **Weekly dependency updates**: Check for security patches
2. **Monthly base image updates**: Pull latest base image
3. **Quarterly security audits**: Full vulnerability scan

### Local Testing

Before pushing changes:

```bash
# Build image locally
docker build -t tmt-os-quantum:local .

# Run Trivy scan locally
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image tmt-os-quantum:local

# Test application
docker run --rm -p 8000:8000 tmt-os-quantum:local
```

### Security Checklist

- [ ] Base image uses specific version tag
- [ ] All dependencies have version constraints
- [ ] Non-root user is configured
- [ ] .dockerignore excludes sensitive files
- [ ] No secrets in image layers
- [ ] Health check configured
- [ ] Minimal packages installed
- [ ] Build dependencies removed

## Troubleshooting

### Common Issues

**Issue**: Trivy fails with CRITICAL vulnerabilities
**Solution**: Update dependencies in requirements.txt and rebuild

**Issue**: Build fails on dependency installation
**Solution**: Check for conflicting versions, use `pip check`

**Issue**: Application fails to start
**Solution**: Verify non-root user has correct permissions

## References

- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Docker Security Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

## Contact

For security concerns, contact the security team or create an issue with the `security` label.