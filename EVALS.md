# AI Tech Consultant — Evaluation Report

## 1. Purpose

This document describes the testing and evaluation approach for the three components of AI Tech Consultant: Knowledge Brain, Inbox Agent, and Meeting to Scope.

## 2. Automated Test Results

The following automated tests were run locally using pytest.

| Component | Tests passed |
|---|---:|
| Task 1 — Knowledge Brain | 5 |
| Task 2 — Inbox Agent | 10 |
| Task 3 — Meeting to Scope | 8 |
| **Total** | **23** |

Command used:

```bash
python -m pytest -v
```

Observed result: **23 passed, 1 warning**. The warning was a ChromaDB dependency deprecation warning and did not cause a test failure.

These results describe the current automated tests. They do not establish production readiness or prove the accuracy of all responses.

## 3. Task 1 — Knowledge Brain

### Evaluation checks
- The home endpoint responds successfully.
- The health endpoint reports the service status.
- A relevant website-design question returns a valid response structure.
- An unrelated question can trigger human escalation.
- An empty question receives a validation-style message.

### Known limitations
Only a small number of automated cases currently cover retrieval and escalation. A larger test set is needed to measure retrieval relevance, source correctness, abstention quality, and incremental crawling behavior.

## 4. Task 2 — Inbox Agent

### Evaluation checks
- The home and health endpoints respond successfully.
- Billing and technical-support emails can be classified.
- Website-design emails can be classified.
- Drafts can be listed, edited, approved, and rejected.
- Invalid review actions are handled.

### Known limitations
Classification currently uses keyword rules, and replies use fixed templates. The tests do not establish LLM-level classification quality, response quality across 50 real-world-style emails, or whether feedback improves future predictions.

## 5. Task 3 — Meeting to Scope

### Evaluation checks
- The home and health endpoints respond successfully.
- Valid meeting notes can be analyzed.
- Invalid or incomplete requests are handled.
- Scope drafts can be listed, approved, and rejected.

### Known limitations
Requirement extraction is preliminary, task estimates are placeholders, and out-of-scope detection needs stronger evaluation. Human review remains necessary.

## 6. Model Comparison

A fair model comparison has not yet been completed. No comparative quality, latency, cost, or safety scores should be reported until models have been tested on the same cases using a documented evaluation method.

The current free-mode prototype uses local embeddings and deterministic rules/templates. These components are not equivalent to Claude-generated responses.

## 7. Next Evaluation Work

1. Build at least 20 evaluation cases for each task.
2. Include normal, ambiguous, incomplete, and failure scenarios.
3. Record expected behavior and actual output for each case.
4. Measure accuracy, evidence relevance, escalation correctness, latency, and cost where applicable.
5. Compare at least two models under the same conditions when access is available.
6. Document failures and improvements honestly.

## 8. Conclusion

The current automated test suite passes all 23 tests. This is a useful baseline for continued development, but broader evaluation datasets, model comparisons, UI testing, and end-to-end demo validation remain necessary before final submission.
