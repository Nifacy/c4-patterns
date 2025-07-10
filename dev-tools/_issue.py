from dataclasses import dataclass
from typing import Final
import urllib.parse
import github


_GITHUB_HOST: Final = "github.com"
_CLOSED_STATE: Final = "closed"


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


def extract_issue_info(github_client: github.Github, issue_link: str) -> IssueInfo:
    parsed = urllib.parse.urlparse(issue_link)
    path_parts = parsed.path.strip("/").split("/")

    if parsed.hostname != _GITHUB_HOST:
        raise ValueError(f"Expected GitHub host, got {parsed.hostname!r}")

    match path_parts:
        case [owner, repo, "issues", issue_number_str] if (
            owner and repo and issue_number_str.isdigit()
        ):
            issue_number = int(issue_number_str)
            is_closed = _is_issue_closed(
                github_client,
                _IssuePath(
                    owner=owner,
                    repo=repo,
                    issue_number=issue_number,
                ),
            )
            return IssueInfo(
                owner=owner,
                repo=repo,
                number=issue_number,
                is_closed=is_closed,
            )
        case _:
            raise ValueError(f"Unrecognized issue link format: {issue_link}")


def _is_issue_closed(github_client: github.Github, issue_info: _IssuePath) -> bool:
    repository = github_client.get_repo(issue_info.full_repo_name)
    issue = repository.get_issue(issue_info.issue_number)
    return issue.state == _CLOSED_STATE
