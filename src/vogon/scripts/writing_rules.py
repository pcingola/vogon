"""The word lists the writing check applies.

Copied from `src/docs/dev/writing.md` (banned words and phrases, placeholders,
counted nouns) and `assets/brand.md` (fixed strings). `assets/` is not part
of the plugin, so the checker holds its own copy. A change to either document
is made here in the same change.
"""

from __future__ import annotations

# writing.md, "Banned words and phrases": rule -> words and phrases.
BANNED: dict[str, tuple[str, ...]] = {
    "No emphasis in place of a fact": (
        "critically", "crucially", "importantly", "notably", "worth noting",
        "it should be noted", "needless to say", "the key insight",
        "here is the thing",
    ),
    "No metaphors for importance": (
        "load-bearing", "linchpin", "gate", "gatekeeper", "forcing function",
        "north star", "cornerstone", "silver bullet", "game-changer",
    ),
    "No marketing or management vocabulary": (
        "leverage", "seamless", "seamlessly", "synergy", "best-in-class",
        "world-class", "cutting-edge", "state-of-the-art", "next-generation",
        "holistic", "empower", "unlock", "streamline", "value proposition",
        "paradigm shift", "move the needle", "deep dive", "low-hanging fruit",
        "wedge", "land-and-expand",
    ),
}

# writing.md, "Other checks": frontmatter values that stand in for an absent
# field, compared ignoring case. `none` is allowed only in NONE_ALLOWED_IN.
PLACEHOLDERS = ("n/a", "na", "tbd", "todo", "none considered", "-", "null", "")
NONE_PLACEHOLDER = "none"
NONE_ALLOWED_IN = ("gxp_risk",)

# writing.md, "Other checks": what a section heading or bold block label may not name.
OPEN_ITEM_LABELS = ("open questions", "open question", "open issues", "open issue",
                    "todo", "todos", "tbd", "next steps", "next step")

# writing.md, "Other checks": plural nouns naming something the repository
# holds, which may not follow a cardinal number.
COUNTED_NOUNS = ("skills", "commands", "requirements", "records", "tests", "checks", "modules")

NUMBER_WORDS = (
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
    "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "dozen",
)

# The bold block label that opens the example block, which the count rule exempts.
EXAMPLE_LABELS = ("example", "examples")

# records.md, "Length limits": maximum words in the body, by record type.
BODY_WORD_LIMITS = {"requirement": 300, "fact": 200, "constraint": 200, "decision": 600}

# assets/brand.md, "Fixed strings" and the terminal stamp. Matched with case,
# because each is written in a fixed form and the ordinary words in them are not
# the voice. The tagline is matched with or without its full stop.
BRAND_STRINGS = (
    "Because good enough is not compliant",
    "COMPLIANCE · TRACEABILITY · RISK MANAGEMENT · A BRIGHTER TOMORROW",
    "A BRIGHTER TOMORROW",
    "Same problems. More process.",
    "It depends.",
    "Per SOP.",
    "REJECTED",
)
