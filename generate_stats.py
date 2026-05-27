import requests, os, json

TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = os.environ["USERNAME"]
HEADERS = {"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"}

query = """
query($login: String!) {
  user(login: $login) {
    name
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
      nodes { stargazers { totalCount } }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalRepositoryContributions
    }
    followers { totalCount }
  }
}
"""

r = requests.post(
    "https://api.github.com/graphql",
    json={"query": query, "variables": {"login": USERNAME}},
    headers=HEADERS,
)
data = r.json()["data"]["user"]

stars = sum(n["stargazers"]["totalCount"] for n in data["repositories"]["nodes"])
commits = data["contributionsCollection"]["totalCommitContributions"]
prs = data["contributionsCollection"]["totalPullRequestContributions"]
issues = data["contributionsCollection"]["totalIssueContributions"]
repos = data["contributionsCollection"]["totalRepositoryContributions"]
followers = data["followers"]["totalCount"]

svg = f"""<svg width="495" height="195" xmlns="http://www.w3.org/2000/svg">
  <style>
    .bg {{ fill: #0d1117; }}
    .border {{ fill: none; stroke: #30363d; stroke-width: 1; rx: 6; }}
    .title {{ fill: #58a6ff; font-size: 14px; font-weight: 600; font-family: monospace; }}
    .label {{ fill: #8b949e; font-size: 12px; font-family: monospace; }}
    .value {{ fill: #e6edf3; font-size: 12px; font-weight: 600; font-family: monospace; }}
    .icon {{ fill: #58a6ff; }}
  </style>
  <rect class="bg" width="495" height="195" rx="6"/>
  <rect class="border" width="494" height="194" x="0.5" y="0.5" rx="6"/>
  <text x="25" y="35" class="title">📊 {USERNAME}'s GitHub Stats</text>
  <text x="25" y="70" class="label">⭐ Total Stars</text>
  <text x="300" y="70" class="value">{stars}</text>
  <text x="25" y="95" class="label">📦 Commits (this year)</text>
  <text x="300" y="95" class="value">{commits}</text>
  <text x="25" y="120" class="label">🔀 Pull Requests</text>
  <text x="300" y="120" class="value">{prs}</text>
  <text x="25" y="145" class="label">🐛 Issues</text>
  <text x="300" y="145" class="value">{issues}</text>
  <text x="25" y="170" class="label">👥 Followers</text>
  <text x="300" y="170" class="value">{followers}</text>
</svg>"""

os.makedirs("generated", exist_ok=True)
with open("generated/overview.svg", "w") as f:
    f.write(svg)

print("Stats generated successfully!")
