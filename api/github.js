/**
 * Vercel Serverless Function for GitHub API Integration
 * 
 * This function proxies GitHub API requests with authentication,
 * solving the "Organization not found" error by using a GitHub token.
 * 
 * Environment Variables Required:
 * - GITHUB_TOKEN: Personal Access Token with public_repo scope
 */

export default async function handler(req, res) {
  // Set CORS headers for all responses
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  
  // Only allow GET requests
  if (req.method !== 'GET') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }
  
  // Check for GitHub token
  const githubToken = process.env.GITHUB_TOKEN;
  
  if (!githubToken) {
    console.error('GITHUB_TOKEN environment variable not set');
    res.status(500).json({ 
      error: 'GitHub token not configured',
      message: 'Please add GITHUB_TOKEN to Vercel environment variables'
    });
    return;
  }
  
  // Extract query parameters
  const { endpoint, org, repo, username } = req.query;
  
  try {
    let githubUrl;
    let headers = {
      'Authorization': `Bearer ${githubToken}`,
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'QuantumDynamics-Vercel-App'
    };
    
    // Determine which GitHub API endpoint to call
    switch (endpoint) {
      case 'org':
        // Get organization info
        githubUrl = `https://api.github.com/orgs/${org || 'quantumdynamics927-dotcom'}`;
        break;
        
      case 'org-repos':
        // Get organization repositories
        githubUrl = `https://api.github.com/orgs/${org || 'quantumdynamics927-dotcom'}/repos?per_page=100&sort=updated`;
        break;
        
      case 'user':
        // Get user info
        githubUrl = `https://api.github.com/users/${username || 'quantumdynamics927-dotcom'}`;
        break;
        
      case 'user-repos':
        // Get user repositories
        githubUrl = `https://api.github.com/users/${username || 'quantumdynamics927-dotcom'}/repos?per_page=100&sort=updated`;
        break;
        
      case 'repo':
        // Get specific repository
        if (!repo) {
          res.status(400).json({ error: 'Repository name required' });
          return;
        }
        githubUrl = `https://api.github.com/repos/${org || 'quantumdynamics927-dotcom'}/${repo}`;
        break;
        
      case 'readme':
        // Get repository README
        if (!repo) {
          res.status(400).json({ error: 'Repository name required' });
          return;
        }
        githubUrl = `https://api.github.com/repos/${org || 'quantumdynamics927-dotcom'}/${repo}/readme`;
        headers['Accept'] = 'application/vnd.github.v3.raw';
        break;
        
      default:
        // Default: get organization repositories
        githubUrl = `https://api.github.com/orgs/${org || 'quantumdynamics927-dotcom'}/repos?per_page=100&sort=updated`;
    }
    
    console.log(`Fetching from GitHub: ${githubUrl}`);
    
    // Make request to GitHub API
    const response = await fetch(githubUrl, { headers });
    
    // Check for rate limiting
    const rateLimitRemaining = response.headers.get('X-RateLimit-Remaining');
    const rateLimitLimit = response.headers.get('X-RateLimit-Limit');
    
    console.log(`GitHub API Rate Limit: ${rateLimitRemaining}/${rateLimitLimit} remaining`);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('GitHub API Error:', response.status, errorData);
      
      // Handle specific error cases
      if (response.status === 404) {
        res.status(404).json({ 
          error: 'Organization or resource not found',
          message: errorData.message || 'The requested GitHub resource does not exist or is private',
          organization: org || 'quantumdynamics927-dotcom'
        });
        return;
      }
      
      if (response.status === 403) {
        res.status(403).json({ 
          error: 'Rate limit exceeded',
          message: 'GitHub API rate limit exceeded. Please try again later.',
          rateLimit: {
            remaining: rateLimitRemaining,
            limit: rateLimitLimit
          }
        });
        return;
      }
      
      res.status(response.status).json({ 
        error: 'GitHub API error',
        message: errorData.message || 'An error occurred while fetching from GitHub',
        status: response.status
      });
      return;
    }
    
    // Parse response
    const data = await response.json();
    
    // Add rate limit info to response headers
    res.setHeader('X-GitHub-RateLimit-Remaining', rateLimitRemaining || 'unknown');
    res.setHeader('X-GitHub-RateLimit-Limit', rateLimitLimit || 'unknown');
    
    // Return successful response
    res.status(200).json(data);
    
  } catch (error) {
    console.error('Error fetching from GitHub:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      message: error.message || 'An unexpected error occurred'
    });
  }
}