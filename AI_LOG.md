# AI Tech Consultant — AI Development Log

## AI Coding Assistant
AI assistance was used to understand requirements, plan the application structure, debug implementation issues, and create and improve automated tests. All generated suggestions were reviewed and tested before use.

## Five Prompts Used

1. **Project architecture:** “Help me design a Python project with three connected components: a documentation-based Knowledge Brain, an Inbox Agent, and a Meeting-to-Scope workflow.”

2. **Knowledge retrieval:** “Explain how to use Sentence Transformers and ChromaDB to retrieve relevant support-documentation chunks and return source links.”

3. **API integration:** “Help me connect a FastAPI email-classification service to a separate Knowledge Brain API using HTTPX, including timeout and error handling.”

4. **Human review:** “Help me implement API endpoints that let a human edit, approve, or reject an email reply draft without automatically sending the email.”

5. **Testing and debugging:** “Help me write pytest tests for API health checks, relevant and unrelated questions, email classification, and human approval workflows.”

## Rejected AI Answer

**Actual rejected answer:** [Replace this placeholder with a real AI-generated answer that I rejected during development.]

**Why I rejected it:** [Explain the actual reason, such as unsupported information, incorrect code, missing error handling, or failure to meet an assignment requirement.]

**What I did instead:** [Describe the correction you actually made and how you verified it.]

## Verification and Responsibility

I ran the automated test suite using:

```bash
python -m pytest -v
```

The observed result was 23 passing tests. I reviewed the test output and used it to check the current API behavior.

AI-generated code and documentation were treated as suggestions, not as proof of correctness. I checked implementation behavior using local tests. The current prototype still has limitations, including template-based email replies, preliminary meeting estimates, and incomplete model comparisons.

## Limitations

The project has not yet completed all required evaluation cases or a measured comparison of at least two language models. These tasks must be completed and documented using actual results before final submission.
