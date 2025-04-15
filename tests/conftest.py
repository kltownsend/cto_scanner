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
                'content': 'Score: 8/10\nReason: Important enterprise tech update\nTweet 1: Test tweet\nTweet 2: Another test tweet'
            }
        )
    ]
    return mock_response 