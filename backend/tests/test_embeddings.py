import pytest
from unittest.mock import MagicMock, patch
from google.genai import errors
from app.services.embeddings.gemini_embedding_provider import GeminiEmbeddingProvider

def test_missing_api_key():
    with pytest.raises(ValueError, match="GEMINI_API_KEY is required"):
        GeminiEmbeddingProvider(api_key="")

@patch("google.genai.Client")
def test_embed_text_success(MockClient):
    mock_client = MockClient.return_value
    mock_response = MagicMock()
    mock_emb = MagicMock()
    mock_emb.values = [0.1, 0.2, 0.3]
    mock_response.embeddings = [mock_emb]
    mock_client.models.embed_content.return_value = mock_response

    provider = GeminiEmbeddingProvider(api_key="fake-key")
    result = provider.embed_text("test text")
    
    assert result == [0.1, 0.2, 0.3]
    mock_client.models.embed_content.assert_called_once_with(
        model="text-embedding-004",
        contents="test text"
    )

@patch("google.genai.Client")
def test_embed_text_retry(MockClient):
    mock_client = MockClient.return_value
    mock_response = MagicMock()
    mock_emb = MagicMock()
    mock_emb.values = [0.4, 0.5]
    mock_response.embeddings = [mock_emb]
    
    # Create a mock exception that is an instance of APIError
    mock_error = errors.APIError(429, {})
    
    # Fail first, then succeed
    mock_client.models.embed_content.side_effect = [
        mock_error,
        mock_response
    ]

    provider = GeminiEmbeddingProvider(api_key="fake-key")
    result = provider.embed_text("test retry")
    
    assert result == [0.4, 0.5]
    assert mock_client.models.embed_content.call_count == 2
