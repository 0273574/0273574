import requests, os, json

TOKEN = os.environ.get("GITHUB_TOKEN")
USERNAME = os.environ.get("USERNAME")

# Walidacja zmiennych środowiskowych
if not TOKEN:
    print("ERROR: GITHUB_TOKEN nie jest ustawiony!")
    exit(1)
if not USERNAME:
    print("ERROR: USERNAME nie jest ustawiony!")
    exit(1)

HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

query = """
query($login: String!) {
  user(login: $login) {
    name
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
      nodes { stargazers { totalCount } }
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestContributions
      totalIssueContributions
      totalRepositoryContributions
    }
    followers { totalCount }
  }
}
"""

print(f"Sending GraphQL query for user: {USERNAME}")
r = requests.post(
    "https://api.github.com/graphql",
    json={"query": query, "variables": {"login": USERNAME}},
    headers=HEADERS,
)

print(f"Response status code: {r.status_code}")
response = r.json()

# Wydrukuj całą odpowiedź dla debugowania
print(f"API Response: {json.dumps(response, indent=2)}")

# Sprawdzenie błędów
if "errors" in response:
    print(f"GraphQL Errors: {response['errors']}")
    exit(1)

if "data" not in response:
    print(f"ERROR: Brak klucza 'data' w odpowiedzi!")
    exit(1)

if response["data"] is None or response["data"].get("user") is None:
    print(f"ERROR: User not found or API returned null!")
    exit(1)

data = response["data"]["user"]

stars = sum(n["stargazers"]["totalCount"] for n in data["repositories"]["nodes"])
commits = (
    data["contributionsCollection"]["totalCommitContributions"]
    + data["contributionsCollection"]["restrictedContributionsCount"]
)
prs = data["contributionsCollection"]["totalPullRequestContributions"]
issues = data["contributionsCollection"]["totalIssueContributions"]
repos = data["contributionsCollection"]["totalRepositoryContributions"]
followers = data["followers"]["totalCount"]

# Formatowanie liczb z tys. notacją (np. 1.2K zamiast 1200)
def format_number(n):
    if n >= 1000:
        return f"{n/1000:.1f}K"
    return str(n)

user_name = data["name"] or USERNAME  # Użyj pełnej nazwy lub fallback na username

svg = f"""<svg width="495" height="195" xmlns="http://www.w3.org/2000/svg">
  <style>
    .bg {{ fill: #0d1117; }}
    .title {{ fill: #58a6ff; font-size: 14px; font-weight: 600; font-family: monospace; }}
    .label {{ fill: #8b949e; font-size: 12px; font-family: monospace; }}
    .value {{ fill: #e6edf3; font-size: 12px; font-weight: 600; font-family: monospace; text-anchor: end; }}
  </style>
  <rect class="bg" width="495" height="195" rx="6"/>
  <rect fill="none" stroke="#30363d" stroke-width="1" width="494" height="194" x="0.5" y="0.5" rx="6"/>
  <text x="25" y="35" class="title">📊 {user_name}'s GitHub Stats</text>
  <text x="25" y="70" class="label">⭐ Total Stars</text>
  <text x="470" y="70" class="value">{format_number(stars)}</text>
  <text x="25" y="95" class="label">📦 Commits (this year)</text>
  <text x="470" y="95" class="value">{format_number(commits)}</text>
  <text x="25" y="120" class="label">🔀 Pull Requests</text>
  <text x="470" y="120" class="value">{format_number(prs)}</text>
  <text x="25" y="145" class="label">🐛 Issues</text>
  <text x="470" y="145" class="value">{format_number(issues)}</text>
  <text x="25" y="170" class="label">👥 Followers</text>
  <text x="470" y="170" class="value">{format_number(followers)}</text>
</svg>"""

os.makedirs("generated", exist_ok=True)
with open("generated/overview.svg", "w") as f:
    f.write(svg)

print(f"✅ Done! Stars: {stars}, Commits: {commits}, PRs: {prs}, Issues: {issues}, Followers: {followers}")
print(f"SVG saved to: generated/overview.svg")
