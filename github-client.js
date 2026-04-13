/**
 * GitHub API Client for QuantumDynamics Website
 * 
 * This module fetches repository data from the Vercel serverless function
 * instead of directly from GitHub API, solving CORS and authentication issues.
 */

class GitHubClient {
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl || window.location.origin;
    this.cache = new Map();
    this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
  }
  
  /**
   * Fetch data from GitHub API via Vercel serverless function
   */
  async fetchFromAPI(endpoint, params = {}) {
    const queryParams = new URLSearchParams({ endpoint, ...params });
    const url = `${this.baseUrl}/api/github.js?${queryParams}`;
    
    // Check cache
    const cacheKey = url;
    const cached = this.cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      console.log('Returning cached data for:', url);
      return cached.data;
    }
    
    try {
      console.log('Fetching from API:', url);
      const response = await fetch(url);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(error.message || `HTTP ${response.status}`);
      }
      
      const data = await response.json();
      
      // Cache the result
      this.cache.set(cacheKey, {
        data,
        timestamp: Date.now()
      });
      
      return data;
      
    } catch (error) {
      console.error('Error fetching from GitHub API:', error);
      throw error;
    }
  }
  
  /**
   * Get organization information
   */
  async getOrganization(org = 'quantumdynamics927-dotcom') {
    return this.fetchFromAPI('org', { org });
  }
  
  /**
   * Get organization repositories
   */
  async getOrganizationRepos(org = 'quantumdynamics927-dotcom') {
    return this.fetchFromAPI('org-repos', { org });
  }
  
  /**
   * Get user information
   */
  async getUser(username = 'quantumdynamics927-dotcom') {
    return this.fetchFromAPI('user', { username });
  }
  
  /**
   * Get user repositories
   */
  async getUserRepos(username = 'quantumdynamics927-dotcom') {
    return this.fetchFromAPI('user-repos', { username });
  }
  
  /**
   * Get specific repository
   */
  async getRepository(repo, org = 'quantumdynamics927-dotcom') {
    return this.fetchFromAPI('repo', { org, repo });
  }
  
  /**
   * Get repository README
   */
  async getReadme(repo, org = 'quantumdynamics927-dotcom') {
    return this.fetchFromAPI('readme', { org, repo });
  }
  
  /**
   * Display repositories in a container
   */
  async displayRepositories(containerId, org = 'quantumdynamics927-dotcom') {
    const container = document.getElementById(containerId);
    
    if (!container) {
      console.error(`Container with ID "${containerId}" not found`);
      return;
    }
    
    try {
      // Show loading state
      container.innerHTML = `
        <div class="loading">
          <p>Loading repositories...</p>
        </div>
      `;
      
      // Fetch repositories
      const repos = await this.getOrganizationRepos(org);
      
      if (!Array.isArray(repos) || repos.length === 0) {
        container.innerHTML = `
          <div class="no-repos">
            <p>No repositories found for organization "${org}"</p>
          </div>
        `;
        return;
      }
      
      // Sort by stars and update time
      repos.sort((a, b) => {
        const starsDiff = (b.stargazers_count || 0) - (a.stargazers_count || 0);
        if (starsDiff !== 0) return starsDiff;
        return new Date(b.updated_at) - new Date(a.updated_at);
      });
      
      // Generate HTML
      const reposHTML = repos.map(repo => this.createRepoCard(repo)).join('');
      
      container.innerHTML = `
        <div class="repos-grid">
          ${reposHTML}
        </div>
      `;
      
    } catch (error) {
      console.error('Error displaying repositories:', error);
      container.innerHTML = `
        <div class="error">
          <p>Error loading repositories: ${error.message}</p>
          <button onclick="location.reload()">Retry</button>
        </div>
      `;
    }
  }
  
  /**
   * Create a repository card HTML
   */
  createRepoCard(repo) {
    const description = repo.description || 'No description available';
    const language = repo.language || 'Unknown';
    const stars = repo.stargazers_count || 0;
    const forks = repo.forks_count || 0;
    const updated = new Date(repo.updated_at).toLocaleDateString();
    
    return `
      <div class="repo-card">
        <h3>
          <a href="${repo.html_url}" target="_blank" rel="noopener noreferrer">
            ${repo.name}
          </a>
        </h3>
        <p class="description">${this.escapeHtml(description)}</p>
        <div class="repo-meta">
          <span class="language">
            <span class="language-color" style="background-color: ${this.getLanguageColor(language)}"></span>
            ${language}
          </span>
          <span class="stars">⭐ ${stars}</span>
          <span class="forks">🍴 ${forks}</span>
        </div>
        <p class="updated">Updated: ${updated}</p>
      </div>
    `;
  }
  
  /**
   * Escape HTML to prevent XSS
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
  
  /**
   * Get language color (simplified)
   */
  getLanguageColor(language) {
    const colors = {
      'Python': '#3572A5',
      'JavaScript': '#f1e05a',
      'TypeScript': '#2b7489',
      'Java': '#b07219',
      'C++': '#f34b7d',
      'C': '#555555',
      'Go': '#00ADD8',
      'Rust': '#dea584',
      'Ruby': '#701516',
      'PHP': '#4F5D95',
      'Swift': '#ffac05',
      'Kotlin': '#F18E33',
      'Jupyter Notebook': '#DA5B0B',
      'HTML': '#e34c26',
      'CSS': '#563d7c',
      'Shell': '#89e051',
      'Dockerfile': '#384d54',
      'Unknown': '#6e7681'
    };
    return colors[language] || colors['Unknown'];
  }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GitHubClient;
}

// Auto-initialize if container exists
document.addEventListener('DOMContentLoaded', () => {
  const reposContainer = document.getElementById('github-repos');
  if (reposContainer) {
    const client = new GitHubClient();
    client.displayRepositories('github-repos');
  }
});