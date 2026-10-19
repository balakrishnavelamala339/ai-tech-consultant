# AI Tech Consultant — System Design

## 1. Overview

AI Tech Consultant is a support automation project with three connected components: Knowledge Brain, Inbox Agent, and Meeting to Scope. The system uses a local knowledge retrieval service to help ground support workflows in documentation. Human review is required before email drafts or project scopes are approved.

## 2. Architecture

### Task 1 — Knowledge Brain

**Purpose:** Retrieve evidence from Brilliant Directories support documentation.

**Workflow:**
1. Read support article URLs from the support sitemap.
2. Crawl pages politely and save article data locally.
3. Split article text into smaller chunks.
4. Generate embeddings using `sentence-transformers/all-MiniLM-L6-v2`.
5. Store searchable chunks in ChromaDB.
6. Receive questions through a FastAPI endpoint.
7. Retrieve relevant chunks and return source links.
8. Escalate when relevant evidence is not found.

**API endpoints:** `GET /`, `GET /health`, `POST /ask`.

### Task 2 — Inbox Agent

**Purpose:** Classify customer emails and prepare draft replies.

**Workflow:**
1. Receive an email subject and body.
2. Classify the email using keyword-based rules.
3. Call the Knowledge Brain API to look for supporting documentation.
4. Create a reply draft using a category-based template.
5. Store the draft for human review.
6. Allow a reviewer to edit, approve, or reject the draft.

**API endpoints:** `GET /`, `GET /health`, `POST /classify`, `GET /drafts`, and `POST /drafts/{draft_id}/review`.

No email is sent automatically.

### Task 3 — Meeting to Scope

**Purpose:** Convert customer meeting notes into a preliminary project scope.

**Workflow:**
1. Receive a customer name and meeting notes.
2. Extract preliminary requirements from the notes.
3. Identify information that may need clarification.
4. Query the Knowledge Brain for relevant existing support features.
5. Generate preliminary tasks and placeholder hour estimates.
6. Save the proposed scope for human review.
7. Allow a reviewer to edit, approve, or reject the scope.

**API endpoints:** `GET /`, `GET /health`, `POST /analyze`, `GET /scopes`, and `POST /scopes/{scope_id}/review`.

## 3. Technology Stack

- **Language:** Python
- **API framework:** FastAPI
- **Request validation:** Pydantic
- **Knowledge retrieval:** Sentence Transformers and ChromaDB
- **HTTP communication:** HTTPX
- **Testing:** pytest
- **Support data:** Brilliant Directories support documentation

## 4. Component Communication

Task 1 exposes the Knowledge Brain API on port 8000. Task 2 runs on port 8001 and Task 3 runs on port 8002. Task 2 and Task 3 send HTTP requests to Task 1 to retrieve relevant evidence.

The three services can be tested separately. Task 1 should be started before testing workflows that depend on it.

## 5. Reliability and Safety

- Validate incoming requests using Pydantic.
- Return a human-escalation response when sufficient evidence is unavailable.
- Keep email drafts and scopes pending until human review.
- Do not automatically send customer emails.
- Keep API keys and secrets in environment variables.
- Avoid committing `.env` files or credentials to Git.
- Run automated tests after code changes.

## 6. Current Limitations

The current implementation is a free-mode prototype. Knowledge Brain retrieves evidence but does not generate full Claude-written answers. Inbox Agent uses keyword-based classification and fixed reply templates rather than an LLM. Meeting requirements and estimates are preliminary and require human verification.

The current workflow uses in-memory storage for drafts and scopes, so those records may be lost when the services restart. Model comparisons, production reliability, and broader evaluation coverage require further validation.
