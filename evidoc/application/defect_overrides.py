"""Assign issue keys to selected reports without changing persisted test results."""

from collections.abc import Sequence
from dataclasses import replace

from evidoc.application.located_result import LocatedResult


def apply_defects(results: list[LocatedResult], defects: Sequence[str]) -> list[LocatedResult]:
    assignments: dict[str, list[str]] = {}
    for entry in defects:
        target, separator, issue = entry.partition("=")
        if separator:
            target, issue = target.strip(), issue.strip()
            if not target or not issue:
                raise ValueError("Use --defect 'Test name=BUG-123'")
            matches = [
                item
                for item in results
                if target in (item.result.test_case.name, item.result.test_case.full_name)
            ]
            if len(matches) != 1:
                raise ValueError(
                    f"Defect target '{target}' matched {len(matches)} cases; "
                    "use the unique full test name"
                )
            key = matches[0].result.test_id
        else:
            issue = entry.strip()
            if not issue or len(results) != 1:
                raise ValueError(
                    "An unqualified --defect requires exactly one selected test; "
                    "for multiple tests use 'Test name=BUG-123'"
                )
            key = results[0].result.test_id
        assignments.setdefault(key, [])
        if issue not in assignments[key]:
            assignments[key].append(issue)
    return [
        replace(
            item,
            result=replace(
                item.result,
                test_case=replace(
                    item.result.test_case, defect=", ".join(assignments[item.result.test_id])
                ),
            ),
        )
        if item.result.test_id in assignments
        else item
        for item in results
    ]
