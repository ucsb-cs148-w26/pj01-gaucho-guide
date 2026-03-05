## Testing Approach

We use **pytest** as our main testing framework. We chose pytest because it’s simple, widely used for Python projects, and easy to manage as the codebase grows. It lets us write both unit tests and integration tests without needing extra tools or complicated setup.

Our testing is focused on making sure the backend works the way it’s supposed to. This includes things like parsing UCSB transcripts, generating schedules, and making sure the right data gets sent to the frontend. We want good coverage where it matters, without slowing development down by testing everything.

---

## 1. Unit Tests Implementation (Previous Lab)

For the previous lab, we used **pytest** to write unit tests.

We focused our unit tests on the external data collection logic, specifically the transcript scraper in the `tests/` directory. These tests check that transcript data is being parsed correctly and that important fields, like a student’s major or professional tracks, are extracted and formatted properly before they reach the API layer.

Testing this logic in isolation helps catch errors early and keeps bad data from flowing through the rest of the system.

---

## 2. Unit Testing Plans Going Forward

We plan to keep using pytest for unit testing, but we are not aiming for 100% test coverage.

**Our plan:**  
We will write unit tests for complex or critical logic, such as schedule generation calculations or changes to transcript parsing.

**Our reasoning:**  
Writing unit tests for simple or repetitive code does not add much value and takes time away from building features. By focusing on the parts of the code where bugs are more likely to happen, we can protect the core functionality while still moving quickly.

---

## 3. Component / Integration Tests (Current Lab)

To meet this lab’s higher-level testing requirement, we added component and integration tests for our backend API endpoints using **pytest**.

These tests go beyond individual functions and check that different parts of the backend work together correctly. They simulate real requests to the API and make sure the backend responds the way the frontend expects.

The integration tests:
- Send real requests to backend API endpoints  
- Check HTTP status codes (such as `200 OK`)  
- Verify that JSON responses include the expected fields and data formats, like course rigor or prerequisite information  

This helps confirm that the backend can reliably serve data to the React frontend.

---

## 4. Higher-Level Testing Plans Going Forward

We plan to continue maintaining API integration tests, but we are not committing to full end-to-end browser testing right now.

**Our plan:**  
Any new core API route added for features like the chatbot or schedule planner should include an integration test that checks its response. We will use pytest fixtures when needed to keep tests consistent and repeatable.

**Our reasoning:**  
The frontend depends entirely on backend API responses, so keeping those responses stable is the most important integration point. Full UI testing would add a lot of setup time and slow down development. For now, automated API tests combined with manual UI testing give us enough confidence without adding extra overhead.

---

## How to Run the Tests

From the project root directory:

1. Install pytest (if needed):
   ```bash
   pip install pytest
   ```
2. Run the test suite:
   ```bash
   python -m pytest tests/
   ```
This runs both unit tests and integration tests and shows any failures directly in the terminal.
