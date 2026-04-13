# GitHub API Integration for Vercel

This directory contains a serverless function that proxies GitHub API requests, solving CORS and authentication issues for client-side applications.

## Files

- `github.js` - Vercel serverless function for GitHub API proxy
- `../github-client.js` - Client-side JavaScript for calling the API

## Setup

### 1. Create GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Vercel GitHub API")
4. Select scopes:
   - `public_repo` - Access public repositories
   - `read:org` - Read organization data (if needed)
5. Click "Generate token"
6. **Copy the token immediately** - you won't be able to see it again

### 2. Add Environment Variable in Vercel

1. Go to your Vercel project dashboard
2. Navigate to Settings → Environment Variables
3. Add a new variable:
   - **Name**: `GITHUB_TOKEN`
   - **Value**: Your GitHub Personal Access Token
4. Select environments: Production, Preview, Development
5. Click "Save"

### 3. Deploy

Push your changes to GitHub. Vercel will automatically deploy with the new configuration.

## Usage

### Client-Side JavaScript

Include `github-client.js` in your HTML:

```html
<script src="/github-client.js"></script>
```

Create a container for repositories:

```html
<div id="github-repos"></div>
```

The client will automatically fetch and display repositories.

### Manual API Calls

```javascript
const client = new GitHubClient();

// Get organization info
const org = await client.getOrganization('quantumdynamics927-dotcom');

// Get organization repositories
const repos = await client.getOrganizationRepos('quantumdynamics927-dotcom');

// Get specific repository
const repo = await client.getRepository('AGI-model', 'quantumdynamics927-dotcom');

// Get README
const readme = await client.getReadme('AGI-model', 'quantumdynamics927-dotcom');
```

### Direct API Endpoint

You can also call the API directly:

```bash
# Get organization repositories
curl "https://your-domain.vercel.app/api/github.js?endpoint=org-repos&org=quantumdynamics927-dotcom"

# Get specific repository
curl "https://your-domain.vercel.app/api/github.js?endpoint=repo&org=quantumdynamics927-dotcom&repo=AGI-model"
```

## API Endpoints

| Endpoint | Parameters | Description |
|----------|------------|-------------|
| `org` | `org` | Get organization information |
| `org-repos` | `org` | Get organization repositories |
| `user` | `username` | Get user information |
| `user-repos` | `username` | Get user repositories |
| `repo` | `org`, `repo` | Get specific repository |
| `readme` | `org`, `repo` | Get repository README |

## Rate Limits

GitHub API has rate limits:
- **Authenticated**: 5,000 requests per hour
- **Unauthenticated**: 60 requests per hour

This serverless function uses authentication, so you get the higher limit.

The client-side `github-client.js` includes a 5-minute cache to reduce API calls.

## Error Handling

The API returns structured error responses:

```json
{
  "error": "Organization not found",
  "message": "Organization 'invalid-org' not found",
  "status": 404
}
```

Common errors:
- `404` - Organization or repository not found
- `403` - Rate limit exceeded or access denied
- `500` - Server error (check Vercel logs)

## Troubleshooting

### "Organization not found" Error

1. Verify the organization name is correct
2. Check if the organization is public
3. Ensure your GitHub token has `read:org` scope

### "Unauthorized" Error

1. Verify `GITHUB_TOKEN` is set in Vercel environment variables
2. Check the token hasn't expired
3. Ensure the token has the correct scopes

### CORS Errors

The API includes CORS headers, but if you still see CORS errors:
1. Check the `vercel.json` configuration
2. Ensure you're using the correct API endpoint
3. Verify the request headers

### Rate Limit Exceeded

1. Wait for the rate limit to reset (1 hour window)
2. Implement client-side caching (already included in `github-client.js`)
3. Reduce the number of API calls

## Security Notes

- **Never expose your GitHub token in client-side code**
- The token is only used in the serverless function (server-side)
- The API only allows GET requests (read-only)
- CORS headers allow all origins by default - restrict in production if needed

## Architecture

```
Client Browser
     ↓
github-client.js (fetches from /api/github.js)
     ↓
Vercel Serverless Function (api/github.js)
     ↓
GitHub API (with authentication)
     ↓
Returns data to client
```

This architecture:
- Hides the GitHub token from clients
- Solves CORS issues
- Provides caching layer
- Handles rate limiting gracefully

## Monitoring

Check Vercel logs for:
- API response times
- Error rates
- Rate limit warnings

Add monitoring in production:
```javascript
// In api/github.js
console.log(`[GitHub API] ${endpoint} - ${response.status} - ${Date.now() - startTime}ms`);
```

## License

MIT License - See LICENSE file for details.