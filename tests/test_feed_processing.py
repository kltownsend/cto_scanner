import pytest
from unittest.mock import patch, MagicMock
import feedparser
from cto_signal_scanner.main import fetch_and_process_feeds
from cto_signal_scanner.utils.feed_sources import FEEDS

def test_feed_urls_are_valid():
    for url in FEEDS:
        assert url.startswith('http'), f"Feed URL {url} should start with http"
        assert any(term in url.lower() for term in ['rss', 'feed', 'blog']), \
            f"Feed URL {url} should contain 'rss', 'feed', or 'blog'"

@pytest.fixture
def mock_feedparser():
    mock_feed = MagicMock()
    mock_feed.entries = [
        MagicMock(
            title="Test Entry",
            summary="Test Summary",
            link="https://example.com"
        )
    ]
    return mock_feed

def test_fetch_and_process_feeds(mock_feedparser):
    # Create a mock response with the correct structure
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content="Test evaluation"
            )
        )
    ]
    
    # Create a mock client with the correct structure
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    
    with patch('feedparser.parse', return_value=mock_feedparser):
        with patch('cto_signal_scanner.utils.gpt_agent.get_openai_client', return_value=mock_client):
            fetch_and_process_feeds()
            mock_client.chat.completions.create.assert_called() 