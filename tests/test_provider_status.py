import unittest

from claude_agent_harness_opt.provider_status import (
    ANTHROPIC_CREDIT_BLOCK_REASON,
    anthropic_credit_block_fields,
)


class ProviderStatusTests(unittest.TestCase):
    def test_anthropic_credit_balance_error_is_provider_blocked(self):
        fields = anthropic_credit_block_fields(
            "Your credit balance is too low to access the Anthropic API. "
            "Please go to Plans & Billing to upgrade or purchase credits."
        )

        self.assertIsNotNone(fields)
        assert fields is not None
        self.assertEqual("provider_blocked", fields["provider_status"])
        self.assertEqual(ANTHROPIC_CREDIT_BLOCK_REASON, fields["provider_block_reason"])

    def test_anthropic_disabled_usage_credit_email_wording_is_provider_blocked(self):
        fields = anthropic_credit_block_fields(
            "Your access to the Claude API has been disabled because your organization "
            "is out of usage credits. Go to the Billing page to add credits."
        )

        self.assertIsNotNone(fields)
        assert fields is not None
        self.assertIn("do not classify this as a model-quality failure", fields["error"])

    def test_non_credit_provider_error_is_not_billing_blocked(self):
        fields = anthropic_credit_block_fields(
            "model did not return a parseable JSON tool choice"
        )

        self.assertIsNone(fields)


if __name__ == "__main__":
    unittest.main()
