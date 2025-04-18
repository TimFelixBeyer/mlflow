from unittest import mock

from fastapi.encoders import jsonable_encoder
import pytest

from mlflow.gateway.providers.cohere import CohereProvider
from mlflow.gateway.schemas import completions, embeddings
from mlflow.gateway.config import RouteConfig
from tests.gateway.tools import MockAsyncResponse


def completions_config():
    return {
        "name": "completions",
        "route_type": "llm/v1/completions",
        "model": {
            "provider": "cohere",
            "name": "command",
            "config": {
                "cohere_api_key": "key",
            },
        },
    }


def completions_response():
    return {
        "id": "string",
        "generations": [
            {
                "id": "string",
                "text": "This is a test",
            }
        ],
        "prompt": "string",
    }


@pytest.mark.asyncio
async def test_completions():
    resp = completions_response()
    config = completions_config()
    with mock.patch(
        "aiohttp.ClientSession.post", return_value=MockAsyncResponse(resp)
    ) as mock_post:
        provider = CohereProvider(RouteConfig(**config))
        payload = {
            "prompt": "This is a test",
        }
        response = await provider.completions(completions.RequestPayload(**payload))
        assert jsonable_encoder(response) == {
            "candidates": [
                {
                    "text": "This is a test",
                    "metadata": {
                        "finish_reason": None,
                    },
                }
            ],
            "metadata": {
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
                "model": "command",
                "route_type": "llm/v1/completions",
            },
        }
        mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_completions_temperature_is_multiplied_by_5():
    resp = completions_response()
    config = completions_config()
    with mock.patch(
        "aiohttp.ClientSession.post", return_value=MockAsyncResponse(resp)
    ) as mock_post:
        provider = CohereProvider(RouteConfig(**config))
        payload = {
            "prompt": "This is a test",
            "temperature": 0.5,
        }
        await provider.completions(completions.RequestPayload(**payload))
        assert mock_post.call_args[1]["json"]["temperature"] == 0.5 * 5


def embeddings_config():
    return {
        "name": "embeddings",
        "route_type": "llm/v1/embeddings",
        "model": {
            "provider": "cohere",
            "name": "embed-english-light-v2.0",
            "config": {
                "cohere_api_key": "key",
            },
        },
    }


def embeddings_response():
    return {
        "id": "bc57846a-3e56-4327-8acc-588ca1a37b8a",
        "texts": ["hello world"],
        "embeddings": [
            [
                3.25,
                0.7685547,
                2.65625,
                -0.30126953,
                -2.3554688,
                1.2597656,
            ]
        ],
        "meta": [
            {
                "api_version": [
                    {
                        "version": "1",
                    }
                ]
            },
        ],
    }


@pytest.mark.asyncio
async def test_embeddings():
    resp = embeddings_response()
    config = embeddings_config()
    with mock.patch(
        "aiohttp.ClientSession.post", return_value=MockAsyncResponse(resp)
    ) as mock_post:
        provider = CohereProvider(RouteConfig(**config))
        payload = {"text": "This is a test"}
        response = await provider.embeddings(embeddings.RequestPayload(**payload))
        assert jsonable_encoder(response) == {
            "embeddings": [
                [
                    3.25,
                    0.7685547,
                    2.65625,
                    -0.30126953,
                    -2.3554688,
                    1.2597656,
                ]
            ],
            "metadata": {
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
                "model": "embed-english-light-v2.0",
                "route_type": "llm/v1/embeddings",
            },
        }
        mock_post.assert_called_once()
