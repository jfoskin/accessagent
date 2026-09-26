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


WCAG_NAMES: dict[str, str] = {
    "1.1.1": "Non-text Content",
    "1.3.1": "Info and Relationships",
    "1.3.2": "Meaningful Sequence",
    "1.4.3": "Contrast (Minimum)",
    "1.4.4": "Resize Text",
    "2.4.2": "Page Titled",
    "2.4.4": "Link Purpose (In Context)",
    "2.4.6": "Headings and Labels",
    "2.4.7": "Focus Visible",
    "3.1.1": "Language of Page",
    "3.3.2": "Labels or Instructions",
    "4.1.2": "Name, Role, Value",
    "4.1.3": "Status Messages",
}


def get_name(criterion: str | None) -> str | None:
    """Returns the official name for a WCAG criterion, or None if not
    in the table — verify against the W3C quickref before adding entries."""
    if criterion is None:
        return None
    return WCAG_NAMES.get(criterion.strip())


WCAG_SLUGS: dict[str, str] = {
    "1.1.1": "non-text-content",
    "1.3.1": "info-and-relationships",
    "1.3.2": "meaningful-sequence",
    "1.4.3": "contrast-minimum",
    "1.4.4": "resize-text",
    "2.4.2": "page-titled",
    "2.4.4": "link-purpose-in-context",
    "2.4.6": "headings-and-labels",
    "2.4.7": "focus-visible",
    "3.1.1": "language-of-page",
    "3.3.2": "labels-or-instructions",
    "4.1.2": "name-role-value",
    "4.1.3": "status-messages",
}


def get_reference_url(criterion: str | None) -> str | None:
    """Returns the official W3C quick reference URL for a WCAG 2.2
    criterion, or None if not in the table."""
    if criterion is None:
        return None
    slug = WCAG_SLUGS.get(criterion.strip())
    if not slug:
        return None
    return f"https://www.w3.org/WAI/WCAG22/quickref/#{slug}"
