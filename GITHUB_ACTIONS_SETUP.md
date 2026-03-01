# 🚀 GitHub Actions - Automated Docker Build

## Overview
This setup automatically builds and pushes Docker images to GitHub Container Registry (and optionally Docker Hub) whenever you push code.

## Workflows Included

### 1. **docker-build.yml** (GitHub Container Registry)
- Builds on every push to `main`, `master`, `develop`
- Pushes to GitHub Container Registry (`ghcr.io`)
- No secrets required (uses GitHub Token)
- **Recommended for private/public repos**

### 2. **docker-hub.yml** (Docker Hub - Optional)
- Requires Docker Hub account
- Requires repository secrets setup
- Only pushes on main branch and tags
- **Optional - only if you want public Docker Hub distribution**

## Setup Instructions

### For GitHub Container Registry (ghcr.io) - No Setup Needed!

The `docker-build.yml` workflow is ready to use immediately:

1. **Push your code to GitHub**
   ```bash
   git push origin main
   ```

2. **Workflow automatically triggers**
   - Go to GitHub repo → Actions tab
   - See workflow running
   - Image built and pushed to `ghcr.io`

3. **Access your image**
   ```bash
   docker pull ghcr.io/YOUR_USERNAME/photosort:latest
   ```

### For Docker Hub (Optional Setup)

If you want to also publish to Docker Hub:

#### Step 1: Create Docker Hub Account
- Go to [Docker Hub](https://hub.docker.com)
- Sign up for free account
- Note your username

#### Step 2: Create Docker Hub Personal Access Token
1. Login to Docker Hub
2. Go to Account Settings → Security
3. Click "New Access Token"
4. Enter token name: `github-actions`
5. Copy the token (you'll need it)

#### Step 3: Add Secrets to GitHub Repository
1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add these secrets:
   - **DOCKER_USERNAME**: Your Docker Hub username
   - **DOCKER_PASSWORD**: Your Docker Hub access token

#### Step 4: Push Code to Trigger Workflow
```bash
git push origin main
```

The workflow will build and push to Docker Hub.

## How It Works

### Automatic Triggers

**docker-build.yml** triggers on:
- Push to `main`, `master`, `develop` branches
- Pull requests to `main`, `master`
- Push of version tags (v1.0.0, v2.0, etc.)

**docker-hub.yml** triggers on:
- Push to `main`, `master`
- Version tags (v1.0.0, etc.)
- Manual workflow dispatch (Actions tab)

### Automatic Tagging

Images are automatically tagged with:
- **Branch name**: `branch-name`
- **Version number**: `v1.0.0` (from tags)
- **Git SHA**: Latest commit hash
- **latest**: Always latest on default branch

Example tags created:
```
ghcr.io/username/photosort:latest
ghcr.io/username/photosort:main
ghcr.io/username/photosort:v1.0.0
ghcr.io/username/photosort:abc123def456
```

## Using Images

### Pull from GitHub Container Registry
```bash
# Latest version
docker pull ghcr.io/YOUR_USERNAME/photosort:latest

# Specific version
docker pull ghcr.io/YOUR_USERNAME/photosort:v1.0.0

# Run it
docker run -d -p 5000:5000 ghcr.io/YOUR_USERNAME/photosort:latest
```

### Pull from Docker Hub
```bash
# Latest version
docker pull YOUR_DOCKER_USERNAME/photosort:latest

# Specific version
docker pull YOUR_DOCKER_USERNAME/photosort:v1.0.0

# Run it
docker run -d -p 5000:5000 YOUR_DOCKER_USERNAME/photosort:latest
```

## GitHub Actions Dashboard

Monitor your builds:

1. **Go to Actions tab** in your GitHub repo
2. **See workflow runs** with status (✅ passed, ❌ failed)
3. **Click on run** to see detailed logs
4. **View images** pushed to registry

## Troubleshooting

### Workflow not triggering
- Check branch name (must be main/master/develop)
- Check file changes in repo
- Push to trigger workflow

### Build fails
- Check workflow logs in Actions tab
- Common issues:
  - Missing Dockerfile
  - Python dependencies missing
  - Port conflicts

### Can't push to Docker Hub
- Verify secrets are set correctly
- Check token hasn't expired
- Ensure Docker Hub account exists

### Image not found after build
- Wait for workflow to complete (check Actions tab)
- Verify image name and tag
- Images are private by default on ghcr.io

## Making Images Public

### GitHub Container Registry
1. Go to your GitHub repo
2. Look for "Packages" section on right
3. Click on package (photosort)
4. Go to Package settings
5. Change visibility to "Public"

### Docker Hub
- Automatically public if shared through docker-hub.yml

## Versioning Strategy

### Recommended Git Workflow

```bash
# Development
git push origin main                    # Auto builds with :main tag

# Create release tag
git tag v1.0.0                         # Creates :v1.0.0 and :latest
git push origin v1.0.0                 # Triggers build with version tags

# View all tags
git tag -l
```

## Environment Variables

Add environment variables for builds:

Edit `.github/workflows/docker-build.yml`:

```yaml
env:
  BUILD_DATE: ${{ github.event.head_commit.timestamp }}
  VCS_REF: ${{ github.sha }}
```

## Matrix Builds (Advanced)

Build for multiple architectures:

```yaml
strategy:
  matrix:
    platform:
      - linux/amd64
      - linux/arm64
      - linux/arm/v7

with:
  platforms: ${{ matrix.platform }}
```

## Cache Optimization

Workflows use GitHub Actions cache:
- Speeds up builds significantly
- Caches Docker layers
- Automatic cleanup after 7 days

## Secrets Management

**Never commit secrets!** Use GitHub Secrets for:
- Docker Hub tokens
- Registry credentials
- API keys
- Passwords

Access in workflows:
```yaml
password: ${{ secrets.SECRET_NAME }}
```

## Next Steps

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Add Docker and GitHub Actions"
   git push origin main
   ```

2. **Monitor build**
   - Go to Actions tab
   - Watch workflow run
   - See image pushed

3. **Use image**
   ```bash
   docker pull ghcr.io/username/photosort:latest
   docker run -d -p 5000:5000 ghcr.io/username/photosort:latest
   ```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Action](https://github.com/docker/build-push-action)
- [Container Registry Guide](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Hub Integration](https://github.com/marketplace/actions/build-and-push-docker-images)

---

**Status: ✅ Ready for Automated Builds**

Your PhotoSort app now automatically builds Docker images on every push! 🎉

Happy deploying! 🚀📸
