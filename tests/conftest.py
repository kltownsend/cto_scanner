import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_feed_entry():
    return {
        'title': 'Test Blog Post',
        'summary': 'This is a test summary of the blog post',
        'link': 'https://example.com/test-post'
    }

@pytest.fixture
def mock_openai_response():
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message={
                'content': 'Summary: Important enterprise tech update\nRating: High\nRationale: Test rationale'
            }
        )
    ]
    return mock_response 