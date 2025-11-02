from unittest.mock import Mock, patch

import pytest

from wolf-logic.configs.embeddings.base import BaseEmbedderConfig
from wolf-logic.embeddings.lmstudio import LMStudioEmbedding


@pytest.fixture
def mock_lm_studio_client():
    with patch("wolf-logic.embeddings.lmstudio.OpenAI") as mock_ollama:
        mock_client = Mock()
        mock_client.embeddings.create.return_value = Mock(data=[Mock(embedding=[0.1, 0.2, 0.3, 0.4, 0.5])])
        mock_ollama.return_value = mock_client
        yield mock_client


def test_embed_text(mock_lm_studio_client):
    config = BaseEmbedderConfig(model="nomic-embed-text-v1.5-GGUF/nomic-embed-text-v1.5.f16.gguf", embedding_dims=512)
    embedder = LMStudioEmbedding(config)

    text = "Sample text to embed."
    embedding = embedder.embed(text)

    mock_lm_studio_client.embeddings.create.assert_called_once_with(
        input=["Sample text to embed."], model="nomic-embed-text-v1.5-GGUF/nomic-embed-text-v1.5.f16.gguf"
    )

    assert embedding == [0.1, 0.2, 0.3, 0.4, 0.5]
