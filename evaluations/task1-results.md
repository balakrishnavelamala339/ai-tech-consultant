# Task 1 — Knowledge Brain Evaluation

## Evaluation Summary

- **Total test cases:** 20
- **Scope:** Relevant support questions, unrelated questions, vague questions, and empty input.
- **Results:** The evaluation includes PASS and PARTIAL PASS cases.
- **Key limitation:** The API retrieves supporting evidence and source links but does not generate AI-written answers.
- **Improvement areas:** Retrieve more detailed support instructions and improve clarification for vague questions.
- **Threshold note:** The distance threshold of 0.65 is preliminary and requires further testing.



## Test 1: Relevant support question

- Question: How can I configure general settings for my website?
- Expected behavior: Retrieve relevant support evidence.
- Actual behavior: Returned three support article results with source URLs.
- Best distance: 0.5595
- Result: PASS

## Test 2: Unrelated question

- Question: Who won the 2026 FIFA World Cup?
- Expected behavior: Abstain and recommend human support.
- Actual behavior: Returned no sources and recommended human support.
- Best distance: 0.9772
- Result: PASS

## Limitations

- Only two test cases have been evaluated so far.
- The distance threshold of 0.65 is preliminary and requires more testing.
- The system retrieves evidence but does not generate AI-written answers.
- The full evaluation requires at least 20 test cases.


## Test 3: Website colors and fonts

- Question: How do I customize the colors and fonts of my website?
- Expected behavior: Retrieve relevant support evidence.
- Actual behavior: Returned support articles, including a guide titled "How to Customize Colors, Fonts and More."
- API status: HTTP 200
- Result: PARTIAL PASS — relevant guide found, but detailed instructions were not retrieved.

### T1-02 — Unrelated question

- **Question:** Who won the 2026 FIFA World Cup?
- **Expected behavior:** Abstain because the question is unrelated to Brilliant Directories support.
- **Actual behavior:** The API returned no sources and requested human support.
- **Result:** PASS
- **Safety:** Passed. The system did not provide an unsupported answer.
- **Evidence:** `sources: []`, `needs_human: true`

### T1-03 — Customize website colors and fonts

- **Question:** How can I customize colors and fonts?
- **Expected behavior:** Return relevant support documentation.
- **Actual behavior:** The API returned “Guide 3. How to Customize Colors, Fonts and More” with supporting evidence.
- **Result:** PASS
- **Relevance:** The source directly discusses color sets, design settings, and font customization.
- **Limitation:** The API provides evidence and source links, not a Claude-generated answer.

### T1-04 — Change website theme

- **Question:** How do I change my website theme?
- **Expected behavior:** Return relevant support documentation.
- **Actual behavior:** The API returned the design settings article, including evidence mentioning “How To Preview & Activate A Theme.”
- **Result:** PASS
- **Relevance:** The evidence directly mentions selecting a new pre-made theme and finding instructions to preview and activate a theme.
- **Limitation:** The API returns evidence and source links rather than a generated step-by-step answer.

### T1-05 — Find design settings

- **Question:** Where can I find design settings?
- **Expected behavior:** Return relevant support documentation.
- **Actual behavior:** The API returned “Guide 3. How to Customize Colors, Fonts and More.”
- **Result:** PASS
- **Relevance:** The evidence explicitly states that users can navigate to Settings → Design Settings in the admin area.
- **Limitation:** The API returns evidence and source links, not a generated step-by-step answer.

### T1-06 — Change website font

- **Question:** How can I change the font on my website?
- **Expected behavior:** Return relevant support documentation.
- **Actual behavior:** The API returned “Guide 3. How to Customize Colors, Fonts and More.”
- **Result:** PASS
- **Relevance:** The evidence explicitly mentions changing font settings under the Main Website Design dropdown.
- **Limitation:** The API provides evidence and source links, rather than a generated step-by-step answer.

### T1-07 — Change website background color

- **Question:** How do I change my website background color?
- **Expected behavior:** Return documentation explaining website color customization.
- **Actual behavior:** The API returned “Guide 3. How to Customize Colors, Fonts and More.”
- **Result:** PARTIAL PASS
- **Relevance:** The evidence describes pre-made color sets and the Design Settings area.
- **Limitation:** The returned evidence does not explicitly confirm the exact steps for changing the background color.

### T1-08 — Change homepage layout
- **Question:** How can I change my homepage layout?
- **Result:** PARTIAL PASS
- **Reason:** The API returned relevant general documentation about the Widget Manager, Sidebar Manager, and website design settings. However, it did not provide exact steps for changing the homepage layout.
- **Sources returned:** 3
- **Needs human review:** No
- **Improvement needed:** Retrieve a specific support article explaining how to change the homepage layout.

### T1-09 — Website appearance options
- **Question:** What website appearance options are available?
- **Result:** PASS
- **Reason:** The API returned relevant evidence about color sets, font settings, design settings, and pre-made themes.
- **Sources returned:** 1
- **Needs human review:** No
- **Improvement needed:** None for this test.

### T1-10 — Choose a pre-made website theme
- **Question:** How can I choose and activate a pre-made website theme?
- **Result:** PARTIAL PASS
- **Reason:** The API found relevant evidence about pre-made themes and referenced the article “How To Preview & Activate A Theme,” but the returned evidence did not include the actual activation steps.
- **Sources returned:** 1
- **Needs human review:** No
- **Improvement needed:** Retrieve the specific theme activation article and its instructions.

### T1-11 — Unrelated question: Windows printer installation
- **Question:** How do I install a printer on Windows?
- **Result:** PASS
- **Reason:** The API found no sufficiently relevant evidence and correctly requested human support instead of inventing an answer.
- **Sources returned:** 0
- **Needs human review:** Yes
- **Improvement needed:** None for this test.

### T1-12 — Unrelated question: Capital of Japan
- **Question:** What is the capital of Japan?
- **Result:** PASS
- **Reason:** The API found no sufficiently relevant evidence and correctly requested human support instead of answering outside its knowledge base.
- **Sources returned:** 0
- **Needs human review:** Yes
- **Improvement needed:** None for this test.

### T1-13 — Vague question: General help request
- **Question:** Can you help me?
- **Result:** PARTIAL PASS
- **Reason:** The API safely requested human support and returned no irrelevant sources. However, it should ideally ask a clarifying question to understand the user's issue.
- **Sources returned:** 0
- **Needs human review:** Yes
- **Improvement needed:** Add a clarification step for vague questions.

### T1-14 — Account password question
- **Question:** How can I change my account password?
- **Result:** PARTIAL PASS
- **Reason:** The API safely referred the user to human support because it found no sufficiently relevant evidence. However, it did not retrieve instructions for changing an account password.
- **Sources returned:** 0
- **Needs human review:** Yes
- **Improvement needed:** Add or retrieve relevant account-password support documentation.

### T1-15 — Billing settings
- **Question:** Where can I find and manage my billing settings?
- **Result:** PARTIAL PASS
- **Reason:** The API returned relevant Finance documentation covering billing, invoices, payment settings, and subscriptions, but did not provide exact instructions for managing billing settings.
- **Sources returned:** 3
- **Needs human review:** No
- **Improvement needed:** Retrieve a specific billing-settings article with step-by-step instructions.

### T1-16 — Create a new static page
- **Question:** How do I create a new static page on my website?
- **Result:** PARTIAL PASS
- **Reason:** The API returned relevant My Content documentation listing “How to Create a New Static Page,” but did not provide the actual creation steps.
- **Sources returned:** 2
- **Needs human review:** No
- **Improvement needed:** Retrieve the specific article with step-by-step instructions.

### T1-17 — Edit navigation menu
- **Question:** How do I edit the navigation menu on my website?
- **Result:** PARTIAL PASS
- **Reason:** The API returned relevant Toolbox documentation listing “How to Edit the Top Header Menu,” but did not provide the actual editing instructions.
- **Sources returned:** 2
- **Needs human review:** No
- **Improvement needed:** Retrieve the specific menu-editing article with step-by-step instructions.

### T1-18 — Edit SEO settings
- **Question:** How do I edit the SEO settings for a static website page?
- **Result:** PARTIAL PASS
- **Reason:** The API returned SEO-related article listings, but not the specific instructions.
- **Sources returned:** 2
- **Needs human review:** No
- **Improvement needed:** Retrieve the specific static-page SEO article with step-by-step instructions.

### T1-19 — Custom domain configuration
- **Question:** How do I connect or configure a custom domain for my website?
- **Result:** PARTIAL PASS
- **Reason:** The API found no sufficiently relevant evidence and correctly requested human support.
- **Sources returned:** 0
- **Needs human review:** Yes
- **Improvement needed:** Add or retrieve relevant custom-domain support documentation.

### T1-20 — Empty question handling
- **Question:** Empty string ("")
- **Result:** PASS
- **Reason:** The API correctly prompted the user to enter a question and returned no sources.
- **Sources returned:** 0
- **Needs human review:** No
- **Improvement needed:** None for this test.