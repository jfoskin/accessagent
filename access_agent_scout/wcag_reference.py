"""
Static WCAG 2.2 criterion -> conformance level lookup.

This intentionally does NOT rely on the LLM to determine conformance level —
the criterion-to-level mapping is a fixed, published fact from the W3C, not
something that should ever be inferred or guessed.

This table currently covers the success criteria axe-core commonly flags in
Phase 1 detection. It is NOT the full 87-criterion table. Before relying on
this for a criterion not listed here, verify against the authoritative
source and add it:
https://www.w3.org/WAI/WCAG22/quickref/

Format: "criterion_number": "level"
"""

WCAG_LEVELS: dict[str, str] = {
    # Perceivable
    "1.1.1": "A",    # Non-text Content
    "1.2.1": "A",    # Audio-only and Video-only (Prerecorded)
    "1.2.2": "A",    # Captions (Prerecorded)
    "1.3.1": "A",    # Info and Relationships
    "1.3.2": "A",    # Meaningful Sequence
    "1.3.3": "A",    # Sensory Characteristics
    "1.3.5": "AA",   # Identify Input Purpose
    "1.4.1": "A",    # Use of Color
    "1.4.2": "A",    # Audio Control
    "1.4.3": "AA",   # Contrast (Minimum)
    "1.4.4": "AA",   # Resize Text
    "1.4.10": "AA",  # Reflow
    "1.4.11": "AA",  # Non-text Contrast

    # Operable
    "2.1.1": "A",    # Keyboard
    "2.1.2": "A",    # No Keyboard Trap
    "2.4.1": "A",    # Bypass Blocks
    "2.4.2": "A",    # Page Titled
    "2.4.3": "A",    # Focus Order
    "2.4.4": "A",    # Link Purpose (In Context)
    "2.4.6": "AA",   # Headings and Labels
    "2.4.7": "AA",   # Focus Visible
    "2.4.11": "AA",  # Focus Not Obscured (Minimum) — new in 2.2
    "2.5.3": "A",    # Label in Name

    # Understandable
    "3.1.1": "A",    # Language of Page
    "3.1.2": "AA",   # Language of Parts
    "3.2.1": "A",    # On Focus
    "3.2.2": "A",    # On Input
    "3.3.1": "A",    # Error Identification
    "3.3.2": "A",    # Labels or Instructions

    # Robust
    "4.1.2": "A",    # Name, Role, Value
    "4.1.3": "AA",   # Status Messages
}


def get_level(criterion: str | None) -> str | None:
    """Returns the official conformance level for a WCAG criterion, or
    None if it's not in the table, should fall back to the
    LLM-provided level (flagged as lower-confidence) in that case."""
    if criterion is None:
        return None
    return WCAG_LEVELS.get(criterion.strip())
