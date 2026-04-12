# Docker Build Optimization Notes

## Why Multi-Stage Builds Are Required

This repository uses **multi-stage Docker builds** to minimize runtime image size and prevent CI failures.

### Problem Context

GitHub Actions runners have limited disk space (~14GB). Large Docker images combined with build cache can exhaust available space, causing builds to fail with:

```
ERROR: write /blobs/sha256/...: no space left on device
ERROR: failed to build: failed to solve: failed to copy to tar
```

### Solution: Multi-Stage Builds

The `Dockerfile` uses a two-stage build pattern:

1. **Builder Stage**: Installs build dependencies (build-essential, git, curl)
2. **Runtime Stage**: Copies only compiled packages and application code

**Benefits:**
- Reduces final image size from 3GB+ to significantly smaller
- Discards build tools after compilation
- Minimizes attack surface by excluding unnecessary packages

**Reference:** [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)

## Why GHA Cache Export Was Removed

The `deploy.yml` workflow previously used GitHub Actions cache:

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

### Why It Was Removed

- **Disk Pressure:** GHA cache consumes additional temporary storage during builds
- **Runner Limits:** GitHub-hosted runners have limited disk space
- **Conflict:** Combined with large images, this caused disk exhaustion

**Reference:** [Docker Buildx Cache](https://docs.docker.com/build/ci/github-actions/cache/)

### Trade-offs

**Removed:**
- ✅ Reduced disk usage during builds
- ✅ Fewer disk exhaustion failures

**Cost:**
- ⚠️ Potentially slower builds (no layer caching between runs)
- ⚠️ More bandwidth usage (re-downloading layers)

## Monitoring Recommendations

### Key Metrics to Watch

1. **Final Image Size**
   ```bash
   docker images tmt-os-quantum:local
   ```
   - Target: < 2GB (down from 3GB+)
   - Alert if > 2.5GB

2. **Runner Free Space**
   - Before build: ~14GB available
   - After build: Should have > 2GB free
   - Alert if < 1GB free

3. **Build Duration**
   - Baseline: Note current build time
   - Alert if > 2x baseline (may indicate cache issues)

4. **Failure Rate**
   - Monitor for "no space left on device" errors
   - Alert if recurrence > 5% of builds

### GitHub Actions Workflow

Add to your workflow for monitoring:

```yaml
- name: Check disk space
  run: |
    echo "Available disk space:"
    df -h /
    echo "Docker disk usage:"
    docker system df
```

## When to Re-enable Cache

GHA cache can be safely re-enabled if:

1. **Image size is stable** (< 2GB)
2. **Build times are acceptable** (< 10 minutes)
3. **Failure rate is low** (< 1% disk exhaustion)

### Safe Cache Configuration

```yaml
cache-from: type=gha
cache-to: type=gha,mode=min  # Use 'min' instead of 'max'
```

**Why 'min' mode:**
- Only caches final layers
- Reduces cache storage overhead
- Still provides build time benefits

**Reference:** [GitHub Actions Runner Disk Space Issues](https://github.com/actions/runner-images/issues/2875)

## Alternative Cache Strategies

If build times become problematic, consider:

### 1. Registry Cache
```yaml
cache-from: type=registry,ref=ghcr.io/${{ github.repository }}/cache:runtime
cache-to: type=registry,ref=ghcr.io/${{ github.repository }}/cache:runtime,mode=max
```

### 2. Local Cache
```yaml
cache-from: type=local,src=/tmp/.buildx-cache
cache-to: type=local,dest=/tmp/.buildx-cache-new,mode=max
```

### 3. S3 Cache (for self-hosted runners)
```yaml
cache-from: type=s3,region=us-east-1,bucket=my-bucket,key=cache
cache-to: type=s3,region=us-east-1,bucket=my-bucket,key=cache
```

## Related Commits

- `3f25c9d`: Multi-stage Dockerfile optimization
- `6eee993`: Disable GHA cache export
- `8d04234`: Stop exporting Buildx cache (PR #26)

## Troubleshooting

### Build Fails with "No Space Left on Device"

1. Check current image size:
   ```bash
   docker images | grep tmt-os-quantum
   ```

2. Clean up Docker system:
   ```bash
   docker system prune -af --volumes
   ```

3. Verify multi-stage build is working:
   ```bash
   docker build --target runtime -t test .
   ```

### Build Times Increase Significantly

1. Check if cache is being used:
   ```bash
   docker buildx du
   ```

2. Consider re-enabling cache with 'min' mode
3. Monitor disk space during builds

## References

- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Buildx Cache](https://docs.docker.com/build/ci/github-actions/cache/)
- [GitHub Actions Runner Disk Space](https://github.com/actions/runner-images/issues/2875)
- [Blacksmith: Understanding Multi-Stage Builds](https://www.blacksmith.sh/blog/understanding-multi-stage-docker-builds)