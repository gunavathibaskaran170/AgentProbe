"""Status classification placeholder.

combine_checks() picks the final VerificationResult status from the rule,
similarity and judge checks. It currently returns a safe placeholder.
"""

from __future__ import annotations


def combine_checks(rules: dict, similarity: float, judge: dict) -> str:
    """Combine three checks into one of the five contract statuses.

    TODO: decide the precedence rules for these situations:
      * rules fail because a forbidden word was found -> contradicted,
        but only when it genuinely contradicts the reference; never call a
        claim contradicted merely because text could not be found;
      * every check agrees (rules pass, high similarity, judge pass)
        -> verified;
      * only some required terms are present -> partially_verified;
      * rules pass but similarity is low -> unsupported or unverified;
      * required information is absent and nothing contradicts it
        -> unverified / unsupported;
      * judge disagrees with the rules or similarity -> decide which signal
        wins, and how an ``unknown`` judge verdict should fall back.

    The returned value must be one of: verified, contradicted, unsupported,
    partially_verified, unverified.
    """
    return "unverified"
