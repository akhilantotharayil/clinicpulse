from unittest.mock import patch, MagicMock

import pytest

from app.ai_investigator import investigate_incident


@pytest.mark.parametrize(
    "service,status,response_time",
    [
        ("appointments", "DOWN", 200),
        ("pharmacy", "DOWN", 300),
        ("laboratory", "DOWN", 400),
    ],
)
@patch("app.ai_investigator.boto3.client")
def test_ai_investigation(mock_boto_client, service, status, response_time):
    mock_bedrock = MagicMock()

    mock_bedrock.converse.return_value = {
        "output": {
            "message": {
                "content": [
                    {"text": "AI investigation completed successfully"}
                ]
            }
        }
    }

    mock_boto_client.return_value = mock_bedrock

    result = investigate_incident(
        service,
        status,
        response_time
    )

    assert result == "AI investigation completed successfully"

    mock_boto_client.assert_called_once_with(
        "bedrock-runtime",
        region_name="us-east-1"
    )

    mock_bedrock.converse.assert_called_once()

    call_kwargs = mock_bedrock.converse.call_args.kwargs

    assert call_kwargs["modelId"] == "amazon.nova-micro-v1:0"

    prompt = call_kwargs["messages"][0]["content"][0]["text"]

    assert service in prompt
    assert status in prompt
    assert str(response_time) in prompt

    assert "human approval" in prompt.lower()
    assert "do not invent logs" in prompt.lower()


def test_multiple_ai_investigations():
    with patch("app.ai_investigator.boto3.client") as mock_boto_client:
        mock_bedrock = MagicMock()

        mock_bedrock.converse.side_effect = [
            {
                "output": {
                    "message": {
                        "content": [{"text": "Appointment incident report"}]
                    }
                }
            },
            {
                "output": {
                    "message": {
                        "content": [{"text": "Laboratory incident report"}]
                    }
                }
            },
        ]

        mock_boto_client.return_value = mock_bedrock

        appointment_report = investigate_incident(
            "appointments", "DOWN", 200
        )

        laboratory_report = investigate_incident(
            "laboratory", "DOWN", 400
        )

        assert appointment_report == "Appointment incident report"
        assert laboratory_report == "Laboratory incident report"

        assert mock_bedrock.converse.call_count == 2
