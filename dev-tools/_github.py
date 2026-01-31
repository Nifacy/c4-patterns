from dataclasses import dataclass
import json
from typing import Any, Final
import urllib.parse
import github
import python_graphql_client as graphql

_GITHUB_HOST: Final = "github.com"
_CLOSED_STATE: Final = "closed"
_GITHUB_GRAPHQL_API_URL: Final = "https://api.github.com/graphql"
_GET_PULL_REQUEST_QUERY: Final = """
query($owner: String!, $repo: String!, $prNumber: Int!) {
    repository(owner: $owner, name: $repo) {
        pullRequest(number: $prNumber) {
            closingIssuesReferences(first: 10) {
                nodes {
                    url
                    state
                }
                totalCount
            }
        }
    }
}
"""


@dataclass(frozen=True, slots=True)
class _IssuePath:
    owner: str
    repo: str
    issue_number: int

    @property
    def full_repo_name(self) -> str:
        return f"{self.owner}/{self.repo}"


@dataclass(frozen=True, slots=True)
class IssueInfo:
    owner: str
    repo: str
    number: int
    is_closed: bool


@dataclass(frozen=True, slots=True)
class PullRequestInfo:
    number: int
    pinned_issues: tuple[IssueInfo, ...]


@dataclass(frozen=True, slots=True)
class PullRequestLocation:
    repo: str
    id: int


def _is_issue_closed(github_client: github.Github, issue_path: _IssuePath) -> bool:
    repository = github_client.get_repo(issue_path.full_repo_name)
    issue = repository.get_issue(issue_path.issue_number)
    return issue.state == _CLOSED_STATE


def _split_repo_path(repo_path: str) -> tuple[str, str]:
    parts = repo_path.split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid repository path: {repo_path}")
    return parts[0], parts[1]


def _extract_issue_path(issue_link: str) -> _IssuePath:
    parsed = urllib.parse.urlparse(issue_link)
    path_parts = parsed.path.strip("/").split("/")

    if parsed.hostname != _GITHUB_HOST:
        raise ValueError(f"Expected GitHub host, got {parsed.hostname!r}")

    match path_parts:
        case [owner, repo, "issues", issue_number_str] if (
            owner and repo and issue_number_str.isdigit()
        ):
            issue_number = int(issue_number_str)
            return _IssuePath(owner=owner, repo=repo, issue_number=issue_number)
        case _:
            raise ValueError(f"Unrecognized issue link format: {issue_link}")


def get_issue_info(github_client: github.Github, issue_link: str) -> IssueInfo:
    issue_path = _extract_issue_path(issue_link)
    is_closed = _is_issue_closed(github_client, issue_path)

    return IssueInfo(
        owner=issue_path.owner,
        repo=issue_path.repo,
        number=issue_path.issue_number,
        is_closed=is_closed,
    )


def get_pull_request_info(
    github_token: str | None,
    pr_location: PullRequestLocation,
) -> PullRequestInfo:
    client = graphql.GraphqlClient(endpoint=_GITHUB_GRAPHQL_API_URL)
    owner, repo = _split_repo_path(pr_location.repo)
    variables: dict[str, Any] = {
        "owner": owner,
        "repo": repo,
        "prNumber": pr_location.id,
    }

    headers: dict[str, str] = {}
    if github_token is not None:
        headers["Authorization"] = f"Bearer {github_token}"

    data = client.execute(
        query=_GET_PULL_REQUEST_QUERY,
        variables=variables,
        headers=headers,
    )

    try:
        pr_data = data["data"]["repository"]["pullRequest"]
        closing_issues = pr_data["closingIssuesReferences"]["nodes"]
        issues: list[IssueInfo] = []

        for issue in closing_issues:
            issue_url = issue["url"]
            issue_path = _extract_issue_path(issue_url)
            issues.append(
                IssueInfo(
                    owner=issue_path.owner,
                    repo=issue_path.repo,
                    number=issue_path.issue_number,
                    is_closed=issue["state"].lower() == _CLOSED_STATE,
                )
            )

        return PullRequestInfo(
            number=pr_location.id,
            pinned_issues=tuple(issues),
        )

    except KeyError:
        raise RuntimeError(
            "Invalid response from GitHub API:\n" f"{json.dumps(data, indent=4)}"
        )
