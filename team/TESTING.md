# Testing

## Testing Library
We used **pytest** as our testing framework. Pytest was chosen because it is lightweight, widely used for Python projects, and makes it easy to write and run unit and integration tests.

## Testing Approach
Our testing focuses on verifying core backend functionality without relying on manual testing. We use pytest to validate:
- API endpoint behavior
- Data returned from the backend
- External data collection logic

Tests are written to check expected responses and ensure that key components continue working as the codebase evolves.

## Implemented Tests

### API Endpoint Tests
Location: `tests file`

These tests:
- Send requests to backend endpoints
- Verify status codes (e.g., 200 OK)
- Confirm that responses contain expected fields and formats

## How to Run Tests

From the project root:

Install pytest (if needed):
```bash
pip install pytest

