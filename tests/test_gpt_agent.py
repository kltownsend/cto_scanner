import pytest
from unittest.mock import patch, MagicMock
from cto_signal_scanner.utils.gpt_agent import evaluate_post

def test_evaluate_post():
    # Create a mock response with the correct structure
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content="Score: 8/10\nReason: Test reason\nTweet 1: Test tweet\nTweet 2: Another test tweet"
            )
        )
    ]
    
    # Create a mock client with the correct structure
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    
    # Mock the get_openai_client function to return our mock client
    with patch('cto_signal_scanner.utils.gpt_agent.get_openai_client', return_value=mock_client):
        result = evaluate_post(
            title="Test Post",
            summary="Test Summary",
            url="https://example.com"
        )
        
        assert "Score:" in result
        assert "Tweet" in result
        mock_client.chat.completions.create.assert_called_once()

def test_evaluate_post_handles_api_error():
    with patch('cto_signal_scanner.utils.gpt_agent.get_openai_client') as mock_get_client:
        mock_get_client.side_effect = Exception("API Error")
        with pytest.raises(Exception):
            evaluate_post(
                title="Test Post",
                summary="Test Summary",
                url="https://example.com"
            ) 