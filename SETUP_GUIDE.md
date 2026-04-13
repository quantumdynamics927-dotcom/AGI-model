# GitHub API Integration Setup Guide

This guide walks you through setting up the GitHub API integration for your Vercel deployment.

## Problem Solved

The error you were seeing:
```
Error: Organization 'quantumdynamics927-dotcom' not found. Please check your configuration and try again.
```

This was caused by:
1. **CORS restrictions** - Browsers block direct GitHub API calls from client-side code
2. **Missing authentication** - Unauthenticated requests have very low rate limits (60/hour)
3. **No server-side proxy** - Direct API calls from browsers expose tokens and hit CORS

## Solution Architecture

```
┌─────────────────┐
│  Client Browser │
│  (index.html)   │
└────────┬────────┘
         │ fetch('/api/github.js?endpoint=org-repos&org=quantumdynamics927-dotcom')
         ▼
┌─────────────────────────┐
│  Vercel Serverless      │
│  Function (api/github.js)│
│  - Uses GITHUB_TOKEN    │
│  - Adds CORS headers    │
│  - Handles rate limits  │
└────────┬────────────────┘
         │ fetch('https://api.github.com/orgs/quantumdynamics927-dotcom/repos')
         ▼
┌─────────────────┐
│   GitHub API    │
│  (Authenticated)│
└─────────────────┘
```

## Files Created

1. **`api/github.js`** - Vercel serverless function
   - Proxies GitHub API requests
   - Adds authentication header
   - Handles CORS
   - Returns JSON responses

2. **`github-client.js`** - Client-side JavaScript
   - Calls the serverless function
   - Caches responses (5 minutes)
   - Displays repositories in HTML
   - Handles errors gracefully

3. **`vercel.json`** - Updated configuration
   - Configures API routes
   - Sets CORS headers
   - Excludes API from SPA routing

4. **`index.html`** - Updated to include client script
   - Loads `github-client.js`
   - Auto-initializes on DOM ready

## Setup Steps

### Step 1: Create GitHub Personal Access Token

1. Go to GitHub: https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Configure:
   - **Note**: `Vercel GitHub API - AGI-model`
   - **Expiration**: 90 days (or longer)
   - **Scopes**: 
     - ✅ `public_repo` - Access public repositories
     - ✅ `read:org` - Read organization data
4. Click **"Generate token"**
5. **Copy the token immediately** (you won't see it again)

### Step 2: Add Environment Variable in Vercel

1. Go to Vercel Dashboard: https://vercel.com/dashboard
2. Select your project: `agi-model`
3. Navigate to **Settings** → **Environment Variables**
4. Add new variable:
   - **Name**: `GITHUB_TOKEN`
   - **Value**: Paste your token from Step 1
5. Select environments:
   - ✅ Production
   - ✅ Preview
   - ✅ Development
6. Click **Save**

### Step 3: Deploy to Vercel

**Option A: Automatic (Recommended)**
```bash
# Just push to GitHub - Vercel auto-deploys
git add .
git commit -m "Add GitHub API integration"
git push origin main
```

**Option B: Manual Deploy**
```bash
# Using Vercel CLI
vercel --prod
```

### Step 4: Verify Deployment

1. Wait for deployment to complete (1-2 minutes)
2. Visit your site: `https://agi-model.vercel.app`
3. Open browser DevTools (F12)
4. Check Console for any errors
5. Test API endpoint:
   ```bash
   curl "https://agi-model.vercel.app/api/github.js?endpoint=org-repos&org=quantumdynamics927-dotcom"
   ```

## Usage Examples

### Display Repositories in HTML

Add this to your HTML:
```html
<div id="github-repos"></div>
<script src="/github-client.js"></script>
```

The client will automatically fetch and display repositories.

### Manual API Calls

```javascript
const client = new GitHubClient();

// Get organization
const org = await client.getOrganization('quantumdynamics927-dotcom');
console.log(org);

// Get repositories
const repos = await client.getOrganizationRepos('quantumdynamics927-dotcom');
console.log(repos);

// Get specific repo
const repo = await client.getRepository('AGI-model', 'quantumdynamics927-dotcom');
console.log(repo);
```

### Direct API Endpoint

```bash
# Get organization info
curl "https://your-domain.vercel.app/api/github.js?endpoint=org&org=quantumdynamics927-dotcom"

# Get repositories
curl "https://your-domain.vercel.app/api/github.js?endpoint=org-repos&org=quantumdynamics927-dotcom"

# Get specific repository
curl "https://your-domain.vercel.app/api/github.js?endpoint=repo&org=quantumdynamics927-dotcom&repo=AGI-model"
```

## Available Endpoints

| Endpoint | Parameters | Description |
|----------|------------|-------------|
| `org` | `org` | Get organization information |
| `org-repos` | `org` | Get organization repositories |
| `user` | `username` | Get user information |
| `user-repos` | `username` | Get user repositories |
| `repo` | `org`, `repo` | Get specific repository |
| `readme` | `org`, `repo` | Get repository README |

## Troubleshooting

### "Organization not found" Error

**Cause**: Organization name is incorrect or organization is private

**Solution**:
1. Verify organization name: `quantumdynamics927-dotcom`
2. Check if organization exists: https://github.com/quantumdynamics927-dotcom
3. Ensure your token has `read:org` scope

### "Unauthorized" Error

**Cause**: Missing or invalid `GITHUB_TOKEN`

**Solution**:
1. Check Vercel environment variables
2. Verify token hasn't expired
3. Regenerate token if needed

### CORS Errors

**Cause**: API route not configured properly

**Solution**:
1. Check `vercel.json` configuration
2. Ensure API route is excluded from SPA routing
3. Verify CORS headers are set

### Rate Limit Exceeded

**Cause**: Too many API requests

**Solution**:
1. Wait 1 hour for rate limit reset
2. Client-side caching is enabled (5 minutes)
3. Reduce API call frequency

### Function Timeout

**Cause**: GitHub API slow to respond

**Solution**:
1. Check Vercel function logs
2. Increase `maxDuration` in `vercel.json`
3. Implement retry logic

## Security Best Practices

✅ **DO**:
- Keep `GITHUB_TOKEN` in Vercel environment variables (server-side only)
- Use minimal required scopes (`public_repo`, `read:org`)
- Rotate tokens regularly (every 90 days)
- Monitor API usage in GitHub settings

❌ **DON'T**:
- Never commit tokens to Git
- Never expose tokens in client-side code
- Never use `repo` scope unless needed (gives write access)
- Never share tokens in chat or email

## Monitoring

### Vercel Logs

1. Go to Vercel Dashboard
2. Select your project
3. Click **Logs**
4. Filter by `/api/github.js`

### GitHub API Usage

1. Go to: https://github.com/settings/tokens
2. Click your token
3. View **"Recent usage"**

### Rate Limit Headers

The API returns rate limit information:
```javascript
{
  "rate": {
    "limit": 5000,
    "remaining": 4999,
    "reset": 1234567890
  }
}
```

## Next Steps

1. ✅ Create GitHub token
2. ✅ Add to Vercel environment
3. ✅ Deploy to Vercel
4. ✅ Test API endpoint
5. ✅ Update frontend to use API
6. ✅ Monitor usage and errors

## Support

If you encounter issues:
1. Check Vercel deployment logs
2. Check browser console for errors
3. Test API endpoint directly with curl
4. Verify environment variables are set
5. Check GitHub token hasn't expired

## Additional Resources

- [Vercel Serverless Functions Docs](https://vercel.com/docs/concepts/functions/serverless-functions)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [GitHub Personal Access Tokens](https://github.com/settings/tokens)
- [CORS MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)