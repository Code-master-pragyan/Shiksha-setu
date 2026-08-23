import time
from typing import List, Union
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from google import genai
from google.genai import errors
from app.services.embeddings.embedding_provider import EmbeddingProvider

class GeminiEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str, model: str = "text-embedding-004"):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self._dimension = 3072  # gemini models might use 3072

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=20),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((errors.APIError,)),
        reraise=True
    )
    def embed_text(self, text: str) -> List[float]:
        response = self.client.models.embed_content(
            model=self.model,
            contents=text,
        )
        return response.embeddings[0].values

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=20),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((errors.APIError,)),
        reraise=True
    )
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        # The new SDK takes a single string or list of contents
        response = self.client.models.embed_content(
            model=self.model,
            contents=texts,
        )
        return [emb.values for emb in response.embeddings]

    @property
    def dimension(self) -> int:
        return self._dimension
