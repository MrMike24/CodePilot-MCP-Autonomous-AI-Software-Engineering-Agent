import sys
from backend.app.core.config import settings
from mcp_servers.github.server import GitHubMCPServer

def main():
    print("==================================================")
    print("  CodePilot-MCP: GitHub Integration Health Check")
    print("==================================================")
    print(f"Configured Owner: {settings.GITHUB_DEFAULT_OWNER}")
    print(f"Configured Repo:  {settings.GITHUB_DEFAULT_REPO}")
    print(f"Target Base URL:  https://api.github.com")

    token = settings.GITHUB_TOKEN
    if not token or not token.strip():
        print("\n[STATUS: NOT CONFIGURED]")
        print("GITHUB_TOKEN is missing or empty.")
        print("To enable real GitHub Pull Request creation:")
        print("  1. Create a GitHub Personal Access Token (classic with 'repo' scope or fine-grained with Contents & Pull Requests write permissions).")
        print("  2. Set environment variable: GITHUB_TOKEN=ghp_your_token_here (or in your .env file).")
        print("  3. Set GITHUB_DEFAULT_OWNER=your_github_username_or_org")
        print("  4. Set GITHUB_DEFAULT_REPO=your_target_repository_name")
        return 1

    masked_token = token[:4] + "*" * (len(token) - 8) + token[-4:] if len(token) > 8 else "***"
    print(f"Token Configured: {masked_token}")

    server = GitHubMCPServer()
    auth_res = server.verify_authentication()

    if not auth_res.get("authenticated"):
        print("\n[STATUS: AUTHENTICATION FAILED]")
        print(f"Error: {auth_res.get('error')}")
        return 1

    print("\n[STATUS: AUTHENTICATED SUCCESSFULLY]")
    print(f"Authenticated as GitHub User: {auth_res.get('login')} ({auth_res.get('name') or 'No display name'})")

    # Check repository accessibility
    try:
        repo_data = server.get_repository(settings.GITHUB_DEFAULT_OWNER, settings.GITHUB_DEFAULT_REPO)
        print(f"[REPOSITORY ACCESSIBLE]: {repo_data.get('full_name')} (Default branch: {repo_data.get('default_branch')})")
        print("GitHub integration is 100% ready for real Pull Request delivery.")
        return 0
    except Exception as e:
        print(f"\n[REPOSITORY INACCESSIBLE]: {e}")
        print("Make sure the repository exists and your token has access to it.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
