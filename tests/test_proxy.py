from unittest.mock import Mock, patch

import pytest

from wolf-logic import Memory, MemoryClient
from wolf-logic.proxy.main import Chat, Completions, Mem0


@pytest.fixture
def mock_memory_client():
    mock_client = Mock(spec=MemoryClient)
    mock_client.user_email = None
    return mock_client


@pytest.fixture
def mock_ollama_embedding_client():
    with patch("wolf-logic.embeddings.ollama.OpenAI") as mock_ollama:
        mock_client = Mock()
        mock_ollama.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_ollama_llm_client():
    with patch("wolf-logic.llms.ollama.OpenAI") as mock_ollama:
        mock_client = Mock()
        mock_ollama.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_litellm():
    with patch("wolf-logic.proxy.main.litellm") as mock:
        yield mock


def test_wolf-logic_initialization_with_api_key(mock_ollama_embedding_client, mock_ollama_llm_client):
    wolf-logic = Mem0()
    assert isinstance(wolf-logic.wolf-logic_client, Memory)
    assert isinstance(wolf-logic.chat, Chat)


def test_wolf-logic_initialization_with_config():
    config = {"some_config": "value"}
    with patch("wolf-logic.Memory.from_config") as mock_from_config:
        wolf-logic = Mem0(config=config)
        mock_from_config.assert_called_once_with(config)
        assert isinstance(wolf-logic.chat, Chat)


def test_wolf-logic_initialization_without_params(mock_ollama_embedding_client, mock_ollama_llm_client):
    wolf-logic = Mem0()
    assert isinstance(wolf-logic.wolf-logic_client, Memory)
    assert isinstance(wolf-logic.chat, Chat)


def test_chat_initialization(mock_memory_client):
    chat = Chat(mock_memory_client)
    assert isinstance(chat.completions, Completions)


def test_completions_create(mock_memory_client, mock_litellm):
    completions = Completions(mock_memory_client)

    messages = [{"role": "user", "content": "Hello, how are you?"}]
    mock_memory_client.search.return_value = [{"memory": "Some relevant memory"}]
    mock_litellm.completion.return_value = {"choices": [{"message": {"content": "I'm doing well, thank you!"}}]}
    mock_litellm.supports_function_calling.return_value = True

    response = completions.create(model="gpt-4o-mini", messages=messages, user_id="test_user", temperature=0.7)

    mock_memory_client.add.assert_called_once()
    mock_memory_client.search.assert_called_once()

    mock_litellm.completion.assert_called_once()
    call_args = mock_litellm.completion.call_args[1]
    assert call_args["model"] == "gpt-4o-mini"
    assert len(call_args["messages"]) == 2
    assert call_args["temperature"] == 0.7

    assert response == {"choices": [{"message": {"content": "I'm doing well, thank you!"}}]}


def test_completions_create_with_system_message(mock_memory_client, mock_litellm):
    completions = Completions(mock_memory_client)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
    ]
    mock_memory_client.search.return_value = [{"memory": "Some relevant memory"}]
    mock_litellm.completion.return_value = {"choices": [{"message": {"content": "I'm doing well, thank you!"}}]}
    mock_litellm.supports_function_calling.return_value = True

    completions.create(model="gpt-4o-mini", messages=messages, user_id="test_user")

    call_args = mock_litellm.completion.call_args[1]
    assert call_args["messages"][0]["role"] == "system"
    assert call_args["messages"][0]["content"] == "You are a helpful assistant."
