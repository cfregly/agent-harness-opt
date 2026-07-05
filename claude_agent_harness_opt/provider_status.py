"""Provider access status helpers shared by live-call paths."""

from __future__ import annotations

from typing import Any


PROVIDER_BLOCKED_STATUS = "provider_blocked"
ANTHROPIC_CREDIT_BLOCK_REASON = "anthropic_billing_or_usage_credits"
ANTHROPIC_CREDIT_BLOCK_MESSAGE = (
    "Anthropic provider blocked by billing or usage credits: API access is disabled "
    "or the credit balance is too low. Add credits or enable auto-reload before "
    "rerunning; do not classify this as a model-quality failure."
)

_ANTHROPIC_CREDIT_PATTERNS = (
    "credit balance is too low",
    "out of usage credits",
    "out of credits",
)


def anthropic_credit_block_fields(detail: Any) -> dict[str, str] | None:
    """Return normalized provider-block fields for Anthropic billing lockouts."""

    text = " ".join(str(detail).casefold().split())
    credit_pattern = any(pattern in text for pattern in _ANTHROPIC_CREDIT_PATTERNS)
    disabled_access = "disabled" in text and (
        "claude api" in text or "anthropic api" in text or "api access" in text
    )
    billing_remedy = "billing" in text or "add credits" in text or "auto-reload" in text
    if not credit_pattern and not (disabled_access and billing_remedy):
        return None
    return {
        "error": ANTHROPIC_CREDIT_BLOCK_MESSAGE,
        "provider_block_reason": ANTHROPIC_CREDIT_BLOCK_REASON,
        "provider_remediation": "Add Anthropic API credits or enable auto-reload before rerunning.",
        "provider_status": PROVIDER_BLOCKED_STATUS,
    }
