#!/usr/bin/env python3
"""Read complete GitHub pull-request review data with fixed GraphQL queries."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Callable


REPO_RE = re.compile(r"^(?P<owner>[A-Za-z0-9_.-]+)/(?P<name>[A-Za-z0-9_.-]+)$")

PR_META_QUERY = """
query PRMeta($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      id
      number
      url
      title
      author { login }
      baseRefName
      headRefName
      baseRefOid
      headRefOid
      reviewDecision
    }
  }
}
"""

REVIEWS_QUERY = """
query PRReviews($owner: String!, $name: String!, $number: Int!, $first: Int!, $after: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviews(first: $first, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          databaseId
          url
          state
          body
          submittedAt
          author { login }
        }
      }
    }
  }
}
"""

ISSUE_COMMENTS_QUERY = """
query PRIssueComments($owner: String!, $name: String!, $number: Int!, $first: Int!, $after: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      comments(first: $first, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          databaseId
          url
          body
          createdAt
          updatedAt
          author { login }
        }
      }
    }
  }
}
"""

THREADS_QUERY = """
query PRReviewThreads($owner: String!, $name: String!, $number: Int!, $first: Int!, $after: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: $first, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          startLine
          originalLine
          originalStartLine
          diffSide
          startDiffSide
          comments(first: 100) {
            pageInfo { hasNextPage endCursor }
            nodes {
              id
              databaseId
              url
              body
              createdAt
              updatedAt
              author { login }
              pullRequestReview { id state }
            }
          }
        }
      }
    }
  }
}
"""

THREAD_COMMENTS_QUERY = """
query PRReviewThreadComments($threadId: ID!, $first: Int!, $after: String) {
  node(id: $threadId) {
    ... on PullRequestReviewThread {
      comments(first: $first, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          databaseId
          url
          body
          createdAt
          updatedAt
          author { login }
          pullRequestReview { id state }
        }
      }
    }
  }
}
"""

FIXED_QUERIES = (
    PR_META_QUERY,
    REVIEWS_QUERY,
    ISSUE_COMMENTS_QUERY,
    THREADS_QUERY,
    THREAD_COMMENTS_QUERY,
)


class ReviewReadError(RuntimeError):
    """Raised when complete read-only review data cannot be fetched."""


def parse_repo(value: str) -> tuple[str, str]:
    match = REPO_RE.fullmatch(value)
    if not match:
        raise ReviewReadError("--repo must be OWNER/REPOSITORY")
    return match.group("owner"), match.group("name")


def graphql(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    if query not in FIXED_QUERIES or "mutation" in query.lower():
        raise ReviewReadError("refusing a non-fixed or mutating GraphQL document")

    command = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        if value is None:
            continue
        flag = "-F" if isinstance(value, int) else "-f"
        command.extend([flag, f"{key}={value}"])

    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as exc:
        raise ReviewReadError("GitHub CLI `gh` is not installed") from exc

    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ReviewReadError(f"GitHub query failed: {detail}")

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ReviewReadError("GitHub CLI returned invalid JSON") from exc

    if payload.get("errors"):
        raise ReviewReadError(f"GitHub GraphQL errors: {payload['errors']}")
    return payload.get("data", {})


def pull_request(data: dict[str, Any]) -> dict[str, Any]:
    repository = data.get("repository")
    pr = repository.get("pullRequest") if repository else None
    if not pr:
        raise ReviewReadError("pull request was not found or is not readable")
    return pr


def paginate(
    query: str,
    variables: dict[str, Any],
    connection_from: Callable[[dict[str, Any]], dict[str, Any]],
    max_pages: int,
    fetch: Callable[[str, dict[str, Any]], dict[str, Any]] = graphql,
) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    after: str | None = variables.get("after")
    base_variables = {key: value for key, value in variables.items() if key != "after"}
    seen: set[str] = set()

    for _ in range(max_pages):
        page_variables = {**base_variables, "after": after}
        connection = connection_from(fetch(query, page_variables))
        nodes.extend(connection.get("nodes") or [])
        page_info = connection.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            return nodes
        cursor = page_info.get("endCursor")
        if not cursor or cursor in seen:
            raise ReviewReadError("pagination returned a missing or repeated cursor")
        seen.add(cursor)
        after = cursor

    raise ReviewReadError(f"pagination exceeded --max-pages={max_pages}")


def collect(args: argparse.Namespace) -> dict[str, Any]:
    owner, name = parse_repo(args.repo)
    common = {"owner": owner, "name": name, "number": args.number}
    meta = pull_request(graphql(PR_META_QUERY, common))
    page_variables = {**common, "first": args.page_size}

    reviews = paginate(
        REVIEWS_QUERY,
        page_variables,
        lambda data: pull_request(data)["reviews"],
        args.max_pages,
    )
    issue_comments = paginate(
        ISSUE_COMMENTS_QUERY,
        page_variables,
        lambda data: pull_request(data)["comments"],
        args.max_pages,
    )
    threads = paginate(
        THREADS_QUERY,
        page_variables,
        lambda data: pull_request(data)["reviewThreads"],
        args.max_pages,
    )

    for thread in threads:
        comments = thread.get("comments") or {"nodes": [], "pageInfo": {}}
        nodes = comments.get("nodes") or []
        page_info = comments.get("pageInfo") or {}
        if page_info.get("hasNextPage"):
            cursor = page_info.get("endCursor")
            if not cursor:
                raise ReviewReadError("thread comment pagination omitted endCursor")
            extra = paginate(
                THREAD_COMMENTS_QUERY,
                {
                    "threadId": thread["id"],
                    "first": args.page_size,
                    "after": cursor,
                },
                lambda data: (data.get("node") or {}).get("comments")
                or {"nodes": [], "pageInfo": {}},
                args.max_pages,
            )
            nodes.extend(extra)
        thread["comments"] = nodes

    return {
        "schema_version": 1,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "pagination_complete": True,
        "pull_request": meta,
        "reviews": reviews,
        "issue_comments": issue_comments,
        "review_threads": threads,
    }


def self_test() -> dict[str, Any]:
    for query in FIXED_QUERIES:
        if not query.lstrip().startswith("query ") or "mutation" in query.lower():
            raise ReviewReadError("a bundled GraphQL document is not read-only")
    if parse_repo("octo-org/octo_repo") != ("octo-org", "octo_repo"):
        raise ReviewReadError("repository parser failed a valid slug")
    try:
        parse_repo("https://github.com/octo-org/octo_repo")
    except ReviewReadError:
        pass
    else:
        raise ReviewReadError("repository parser accepted a non-slug input")

    observed: list[str | None] = []
    pages = {
        "cursor-0": {
            "connection": {
                "nodes": [{"id": "second-page"}],
                "pageInfo": {"hasNextPage": True, "endCursor": "cursor-1"},
            }
        },
        "cursor-1": {
            "connection": {
                "nodes": [{"id": "third-page"}],
                "pageInfo": {"hasNextPage": False, "endCursor": None},
            }
        },
    }

    def fake_fetch(query: str, variables: dict[str, Any]) -> dict[str, Any]:
        if query != THREAD_COMMENTS_QUERY:
            raise ReviewReadError("self-test received an unexpected query")
        cursor = variables.get("after")
        observed.append(cursor)
        return pages[cursor]

    nodes = paginate(
        THREAD_COMMENTS_QUERY,
        {"threadId": "thread", "first": 100, "after": "cursor-0"},
        lambda data: data["connection"],
        2,
        fetch=fake_fetch,
    )
    if observed != ["cursor-0", "cursor-1"] or len(nodes) != 2:
        raise ReviewReadError("pagination self-test failed")

    return {
        "status": "ok",
        "fixed_queries": len(FIXED_QUERIES),
        "mutation_paths": 0,
        "pagination_pages_tested": len(observed),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="GitHub repository as OWNER/REPOSITORY")
    parser.add_argument("--number", type=int, help="Positive pull-request number")
    parser.add_argument(
        "--page-size", type=int, default=100, help="Items per page (1-100)"
    )
    parser.add_argument(
        "--max-pages", type=int, default=1000, help="Pagination safety bound"
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    parser.add_argument(
        "--self-test", action="store_true", help="Validate fixed queries without network access"
    )
    args = parser.parse_args()

    if not args.self_test and (not args.repo or not args.number):
        parser.error("--repo and --number are required unless --self-test is used")
    if args.number is not None and args.number < 1:
        parser.error("--number must be positive")
    if not 1 <= args.page_size <= 100:
        parser.error("--page-size must be between 1 and 100")
    if args.max_pages < 1:
        parser.error("--max-pages must be positive")
    return args


def main() -> int:
    args = parse_args()
    try:
        payload = self_test() if args.self_test else collect(args)
    except ReviewReadError as exc:
        print(f"read_pr_review: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
