# Task 2 — Inbox Agent Evaluation

## Purpose

Evaluate email classification, reply-draft safety, Knowledge Brain integration, and human review.

## T2-01 — Billing email
- **Input:** Subject: Payment refund request. Body: I was charged twice and need a refund.
- **Expected category:** billing
- **Expected behavior:** Create a draft and require human approval.
- **Result:** PASS
- **Actual category:** billing
- **Draft status:** pending_human_approval
- **Automatic sending:** false
- **Knowledge check:** evidence_found

## T2-02 — Technical support email
- **Input:** Subject: Login error. Body: The website shows an error when I log in.
- **Expected category:** technical_support
- **Expected behavior:** Create a support draft.
- **Result:** PASS
- **Actual category:** technical_support
- **Draft status:** pending_human_approval
- **Automatic sending:** false
- **Knowledge check:** evidence_found

## T2-03 — Account email
- **Input:** Subject: Reset password. Body: I need help resetting my account password.
- **Expected category:** account
- **Expected behavior:** Create a draft requiring human approval.
- **Result:** PASS
- **Actual category:** account
- **Draft status:** pending_human_approval
- **Automatic sending:** false
- **Knowledge check:** evidence_found
- **Evidence relevance:** PARTIAL — the returned source is about Finance, not password resets.

## T2-04 — Feature request
- **Input:** Subject: New feature suggestion. Body: Please add a new feature to improve the website.
- **Expected category:** feature_request
- **Expected behavior:** Create a feedback draft.
- **Result:** PASS
- **Actual category:** feature_request
- **Draft status:** pending_human_approval
- **Automatic sending:** false
- **Knowledge check:** evidence_found
- **Evidence relevance:** PARTIAL — general website documentation returned; no direct answer to the feature request.

## T2-05 — Website design email
- **Input:** Subject: Change website fonts. Body: I want to customize the website design.
- **Expected category:** website_design
- **Expected behavior:** Create a design-support draft.
- **Result:** PASS
- **Actual category:** website_design
- **Draft status:** pending_human_approval
- **Automatic sending:** false
- **Knowledge check:** evidence_found
- **Evidence relevance:** RELEVANT — the source explains how to customize colors and fonts.

## T2-06 — General email
- **Input:** Subject: General question. Body: I have a question for your support team.
- **Expected category:** general
- **Expected behavior:** Create a general support draft.
- **Result:** PASS
- **Actual category:** general
- **Draft status:** pending_human_approval
- **Automatic sending:** false
- **Knowledge check:** evidence_found
- **Evidence relevance:** PARTIAL — broad support documentation returned, but the customer's question is unspecified.

## T2-07 — Billing and technical keywords
- **Input:** Subject: Payment error. Body: My payment failed and I need help.
- **Expected category:** billing
- **Expected behavior:** Apply the implementation's keyword-counting rule and record whether the category is appropriate.
- **Result:** PARTIAL PASS
- **Actual category:** technical_support
- **Draft status:** pending_human_approval
- **Automatic sending:** false
- **Knowledge check:** evidence_found
- **Observation:** The keyword-counting rule selected technical_support because more technical-support keywords matched. However, the customer's main concern may be a failed payment.

## T2-08 — Mixed category keywords
- **Input:** Subject: Account billing issue. Body: I have a problem with my account payment.
- **Expected category:** Review required
- **Expected behavior:** Record which category the implementation selects and whether it matches the primary customer need.
- **Result:** PARTIAL PASS
- **Actual category:** billing
- **Draft status:** pending_human_approval
- **Automatic sending:** false
- **Knowledge check:** evidence_found
- **Observation:** The classifier selected billing for a mixed account and billing email. Review whether the selected category matches the customer's primary need.

## T2-09 — Empty subject
- **Input:** Subject: Empty string. Body: I need help with my invoice.
- **Expected behavior:** Reject invalid input with HTTP 422.
- **Result:** PASS
- **Actual HTTP status:** 422
- **Observation:** The API rejected the empty subject because the minimum length is 1 character.

## T2-10 — Empty body
- **Input:** Subject: Billing question. Body: Empty string.
- **Expected behavior:** Reject invalid input with HTTP 422.
- **Result:** PASS
- **Actual HTTP status:** 422 Unprocessable Content
- **Observation:** The API correctly rejected an empty email body because the body must contain at least one character.

## T2-11 — Missing subject
- **Input:** Body only: I need help with my invoice.
- **Expected behavior:** Reject invalid input with HTTP 422.
- **Result:** PASS
- **Actual HTTP status:** 422 Unprocessable Content
- **Observation:** The API correctly rejected the request because the required `subject` field was missing.

## T2-12 — Missing body
- **Input:** Subject only: Billing question.
- **Expected behavior:** Reject invalid input with HTTP 422.
- **Result:** PASS
- **Actual HTTP status:** 422 Unprocessable Content
- **Observation:** The API correctly rejected the request because the required `body` field was missing.

## T2-13 — List drafts
- **Expected behavior:** Return a drafts list.
- **Result:** PASS
- **Actual response:** Drafts list returned successfully.
- **Draft count returned:** 6
- **Draft status:** pending_human_approval
- **Observation:** The API successfully returned saved email drafts, including their subjects, categories, suggested replies, and knowledge-check results.

## T2-14 — Edit a draft
- **Expected behavior:** Save the edited reply and keep the draft pending approval.
- **Result:** PASS
- **Actual status:** pending_human_approval
- **Updated reply:** Updated draft reply for testing.
- **Observation:** The API successfully edited the draft and correctly kept it pending human approval. The response confirmed that human approval is still required.

## T2-15 — Approve a draft
- **Expected behavior:** Mark the draft approved without sending an email.
- **Result:** PASS
- **Actual status:** approved
- **Automatic sending:** false
- **Observation:** The API successfully approved the draft. No email was sent automatically, preserving human control over email delivery.

## T2-16 — Reject a draft
- **Expected behavior:** Mark the draft rejected without sending an email.
- **Result:** PASS
- **Actual status:** rejected
- **Automatic sending:** No email was sent.
- **Observation:** The API successfully rejected the draft and confirmed that no email was sent automatically.

## T2-17 — Invalid review action
- **Input:** Action: send
- **Expected behavior:** Return HTTP 400.
- **Result:** PASS
- **Actual HTTP status:** 400 Bad Request
- **Response:** `Action must be approve, edit, or reject`
- **Observation:** The API correctly rejected the unsupported `send` action and accepted only the allowed review actions: approve, edit, or reject.

## T2-18 — Nonexistent draft
- **Input:** Review a draft ID that does not exist.
- **Expected behavior:** Return HTTP 404.
- **Result:** PASS
- **Actual HTTP status:** 404 Not Found
- **Response:** `Draft not found`
- **Observation:** The API correctly returned a not-found error when asked to review a nonexistent draft.

## T2-19 — Review a draft twice
- **Expected behavior:** The second review after approval or rejection returns HTTP 409.
- **Result:** PASS
- **Actual result:** First approval returned status `"approved"`. Second approval returned HTTP 409 Conflict.
- **Message:** `"This draft has already been reviewed"`
- **Conclusion:** The API correctly prevents a second review of an already reviewed draft.

## T2-20 — Automatic sending safety
- **Expected behavior:** Classification and approval must return `auto_send: false`; the application must not send an email automatically.
- **Result:** PASS
- **Actual result:** The API created a billing draft with status `"pending_human_approval"` and `"auto_send": false`.
- **Conclusion:** The system requires human approval and does not send emails automatically.
## Evaluation note

These are planned evaluation cases. Results must be changed from NOT RUN only after each case has actually been tested. Classification uses keyword rules, and reply drafts use fixed templates rather than LLM-generated text.