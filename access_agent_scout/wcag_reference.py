"""
Extracts WCAG criterion + conformance level directly from axe-core's own
rule tags, rather than asking the LLM to recall or guess them.

axe-core tags every rule with machine-readable WCAG references, e.g.:
  ["wcag2aa", "wcag143", "cat.color"]  ->  criterion 1.4.3, level AA

This is deterministic and comes from axe-core's own maintained rule
metadata — it will never hallucinate a removed criterion (like 4.1.1,
obsolete as of WCAG 2.2) or the wrong level.

Not every axe-core rule maps to a WCAG success criterion — some are
"best-practice" only (e.g. landmark-one-main, region). In that case,
parse_wcag_from_tags returns (None, None), and callers should treat
the finding as a best-practice recommendation, not a WCAG violation.
"""
import re

_WCAG_TAG_PATTERN = re.compile(r"^wcag(\d)(\d)(\d+)$")
_LEVEL_TAG_MAP = {
    "wcag2a": "A", "wcag2aa": "AA", "wcag2aaa": "AAA",
    "wcag21a": "A", "wcag21aa": "AA", "wcag21aaa": "AAA",
    "wcag22a": "A", "wcag22aa": "AA", "wcag22aaa": "AAA",
}


def parse_wcag_from_tags(raw_tags: list[str]) -> tuple[str | None, str | None]:
    """
    Returns (criterion, level) parsed from axe-core's raw tags.
    Returns (None, None) if this rule has no real WCAG mapping
    (best-practice-only rule).
    """
    criterion = None
    level = None

    for tag in raw_tags:
        match = _WCAG_TAG_PATTERN.match(tag)
        if match:
            criterion = ".".join(match.groups())  # "wcag143" -> "1.4.3"
        elif tag in _LEVEL_TAG_MAP:
            level = _LEVEL_TAG_MAP[tag]

    return criterion, level
