import os
import pytest
from unittest.mock import Mock, patch
from openai.types.chat import ChatCompletion, ChatCompletionMessage, Choice
from cto_signal_scanner.utils.gpt_agent import GPTAgent

@pytest.fixture
def mock_openai_response():
    mock_message = ChatCompletionMessage(
        content="Summary: Test summary\nRating: High\nRationale: Test rationale",
        role="assistant",
        function_call=None,
        tool_calls=None
    )
    mock_choice = Choice(
        finish_reason="stop",
        index=0,
        message=mock_message,
        logprobs=None
    )
    return ChatCompletion(
        id="test_id",
        choices=[mock_choice],
        created=1234567890,
        model="gpt-3.5-turbo",
        object="chat.completion",
        system_fingerprint=None,
        usage=None
    )

@pytest.fixture
def mock_client(mock_openai_response):
    mock = Mock()
    mock.chat.completions.create.return_value = mock_openai_response
    return mock

def test_gpt_agent_init_openai():
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key', 'USE_OLLAMA': 'false'}):
        agent = GPTAgent()
        assert agent.model == 'gpt-3.5-turbo'
        assert not agent.use_ollama

def test_gpt_agent_init_ollama():
    with patch.dict(os.environ, {
        'USE_OLLAMA': 'true',
        'OLLAMA_BASE_URL': 'http://test:11434/v1',
        'OLLAMA_MODEL': 'test-model'
    }):
        agent = GPTAgent()
        assert agent.model == 'test-model'
        assert agent.use_ollama
        assert agent.client.base_url == 'http://test:11434/v1'

def test_get_current_prompt():
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key', 'GPT_PROMPT': 'test prompt {title}'}):
        agent = GPTAgent()
        assert agent.get_current_prompt() == 'test prompt {title}'

def test_evaluate_post(mock_client):
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
        agent = GPTAgent()
        agent.client = mock_client
        
        result = agent.evaluate_post(
            title="Test Title",
            summary="Test Summary",
            link="http://test.com"
        )
        
        assert result['summary'] == 'Test summary'
        assert result['rating'] == 'High'
        assert result['rationale'] == 'Test rationale'
        mock_client.chat.completions.create.assert_called_once()

def test_evaluate_post_handles_api_error(mock_client):
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
        agent = GPTAgent()
        agent.client = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = agent.evaluate_post(
            title="Test Title",
            summary="Test Summary",
            link="http://test.com"
        )
        
        assert result['rating'] == 'Error'
        assert 'API Error' in result['summary']
        assert result['rationale'] == 'Failed to analyze article'

def test_evaluate_post_incomplete_response(mock_client):
    incomplete_response = ChatCompletion(
        id="test_id",
        choices=[Choice(
            finish_reason="stop",
            index=0,
            message=ChatCompletionMessage(
                content="Summary: Test summary\nRating: High",  # Missing rationale
                role="assistant",
                function_call=None,
                tool_calls=None
            ),
            logprobs=None
        )],
        created=1234567890,
        model="gpt-3.5-turbo",
        object="chat.completion",
        system_fingerprint=None,
        usage=None
    )
    
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
        agent = GPTAgent()
        agent.client = mock_client
        mock_client.chat.completions.create.return_value = incomplete_response
        
        result = agent.evaluate_post(
            title="Test Title",
            summary="Test Summary",
            link="http://test.com"
        )
        
        assert result['summary'] == 'Test summary'
        assert result['rating'] == 'High'
        assert result['rationale'] == ''  # Empty rationale due to incomplete response 