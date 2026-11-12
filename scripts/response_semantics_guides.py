"""Keep behavioral guarantees next to the generated public contract."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
START='{/* BEGIN RESPONSE SEMANTICS */}'
END='{/* END RESPONSE SEMANTICS */}'
SECTIONS={
'api-reference/risk-package.mdx':'''## Interpret recommendations and accepted inputs

A failed rule with `on_fail: outside_policy` takes precedence over a review-only rule. Otherwise, a failed or unavailable rule requiring review, or an unresolved verification outcome, yields `review_required`. `within_policy` requires all applicable executable rules to pass. Verification outcomes and policy recommendations remain separate from your institution's lending decision.

Application amounts and terms come from the accepted application and lending-product version. The evidence set includes those institution-supplied inputs. Signal uses the deal snapshot pinned when its evaluation is claimed; a newer snapshot does not change an in-progress or historical result.

`view=summary` includes the recommendation, verification outcome, accepted identity revision, currency, period, product/policy IDs and section counts. Explanation excerpts are bounded to 2,000 characters. `omitted_fields` lists unusually large context fields omitted from this compact representation; retrieve the full package or export to obtain those values. Read all limitations and policy reasons before making an institution decision.
''',
'api-reference/risk-package-methodology.mdx':'''## Consistent Sandbox calculations

Sandbox monetary calculations use only eligible observations in the reporting currency. Sandbox does not invent FX rates or relabel a CAD value as USD. Unsupported currency scope is reported as unavailable, with an explicit reason.

The synthetic fixed-rate, monthly term-loan illustration uses the accepted principal, requested term, amortization period and annual rate. It repays equal principal, calculates each month's interest on opening principal, and reconciles rounded cents. If the requested term is shorter than amortization, the final installment includes the remaining balloon. The first illustrative payment is due on the first day of the following UTC month. Unsupported repayment frequencies, variable rates or fees without a payment date remain unavailable rather than receiving an invented schedule.

Cash balances sum eligible accounts on each observed calendar day. History counts calendar days, not account-days. Missing account coverage is not filled with zero. Overdraft days account for an overdrawn individual account even if another account leaves consolidated cash positive.

Reconciliation requires explicit transaction-to-invoice allocations over comparable periods. Equal totals alone do not prove a match. Bank match share is matched value divided by eligible bank receipts. Reconciled-value share is twice the matched value divided by combined eligible bank receipts and accounting revenue; unmatched value remains explicit.

Observation periods are taken from frozen records. A later assessment does not move old transactions into a new year or imply a fresh upstream collection. Source freshness, financial period and assessment time are separate fields.
''',
'api-reference/monitoring-design.mdx':'''## Evaluate changes without rewriting history

Read `configuration.cadences[].interval_seconds` for the provisioned schedule. Cadence controls evaluation timing; it is not a claim that every upstream provider has refreshed. Sandbox evidence remains frozen until an explicit source-refresh or scenario action changes it. Repeated evaluations report the actual source window and collection time; sample observations older than 35 days are identified as stale.

Lender-reported performance comes from the pinned `deal_snapshot_id`. Missing performance does not become zero delinquency or a perfect payment history. Provider loan balances and lender exposure are not summed as separate liabilities unless their relationship is reconciled.

An ongoing condition keeps its alert ID and emits `alert.updated` with the latest values, risk package and evidence. A comparable passing evaluation resolves that policy condition. Replacing a policy closes its old alerts with an explicit superseded-policy explanation; that closure does not assert that the borrower recovered. Inspect the alert message and exact policy version.
''',
'api-reference/data-access.mdx':'''## Preserve exact observations through change

Each newly ingested observation has a unique `DataRecord.id`; its logical `resource_id` can remain the same across versions. Keep the ID and version referenced by evidence or a change event. Historical observations whose physical storage previously shared an ID are exposed through distinct opaque observation IDs, without changing their normalized content. Do not parse or construct an observation ID yourself.

The server checks that normalized object type, logical ID and version match their DataRecord envelope. Document `status` filters describe currently accessible status: consent withdrawal can make a previously available document `restricted` before filtering and pagination.

A cursor can become unusable when unread history falls outside retention, even if its original expiry time is in the future. Both event and data-change feeds return `410 cursor_expired` for a detected gap. Reconcile from a new snapshot and retain your deduplication state; never assume that advancing a cursor proves a missing interval was empty.
''',
'api-reference/consumption-reporting.mdx':'''## Distinguish charge-time and current workload

`BillingUsage.workload` freezes the workload at `charged_at`. The workload report contains current accumulated operational counts as of its own `as_of`. These can differ after another included Signal evaluation. This does not create another borrower/month charge or change the agreed historical rate.

Signal rate cards use `first_successful_evaluation_in_month`. Historical cards can retain an earlier timing label; the immutable transaction and `charged_at` identify when credits were actually deducted. Insights charges on successful output completion.

Funding exports preserve `returned`, `partially_refunded` and `refunded` states. `ledger_entry_id` identifies the original credit, `transaction_ids` includes its subsequent movements, and `reversal_transaction_ids` identifies returns or refunds. Reconcile these linked entries instead of treating a return as a failed payment that never settled.
''',
'api-reference/sandbox-journeys.mdx':'''## Test saved automatic-payment settings

The `autopay` scenario uses the selected workspace's saved enabled flag, threshold, recharge amount and payment method. When autopay is disabled or the balance is at or above the threshold, it records the expected no-charge result. An inactive or missing method does not create funds.

Below the threshold, a saved card simulates settlement and posts the configured credit once. ACH remains pending without spendable credit, then the background simulator settles it after at least one minute. A pending attempt prevents duplicate automatic collection. Disabling future autopay does not undo an already submitted pending attempt. No real payment is collected.

Use `card_declined`, `ach_returned` and `payment_refund` for forced payment-outcome fixtures. Those fixtures deliberately create their documented fictional outcome; they are separate from testing automatic funding settings. Loading the sample pack does not enable autopay or override your payment settings.

Use `verification_failed`, `verification_review` and `verification_expired` to test completed underwriting that requires review because the normalized verification is failed, unresolved or expired. A completed response is not an approval, and the presence of a verification record is not a passed check.
''',
'console/billing.mdx':'''## Try automatic funding in Sandbox

Save a payment method and automatic-payment settings, then use the `autopay` scenario to test the actual saved configuration. A balance equal to the threshold does not trigger funding; it must be lower. Card funding settles in the simulator; ACH first appears pending and credits become available only after simulated settlement. Disabling future autopay preserves the outcome of an attempt already submitted.

The sample pack and forced payment scenarios use fictional payments. They do not change your saved autopay settings or collect real money. Funding history distinguishes returns and refunds from failures before settlement.
''',
'api-reference/large-results.mdx':'''## Read decisions without downloading every record

The summary includes bounded `assessment`, `verification_summary` and `decision_context` objects. They carry the recommendation and the exact accepted identity/product/policy references while observations stay in paged sections. Descriptive text is an excerpt, capped at 2,000 characters. An institution reference longer than 512 characters or a monetary amount string longer than 64 characters is omitted from summary with its path in `omitted_fields`; the complete package/export retains it. This omission never changes the calculation or full result.
'''
}
def write_guides():
 for name,content in SECTIONS.items():
  path=ROOT/name
  if not path.exists():raise ValueError('Unknown guide: '+name)
  source=path.read_text()
  if START in source:source=source[:source.index(START)]+source[source.index(END)+len(END):]
  path.write_text(source.rstrip()+'\n\n'+START+'\n'+content.strip()+'\n'+END+'\n')
