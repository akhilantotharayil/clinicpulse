import boto3
import json

MODEL_ID = "amazon.nova-micro-v1:0"
REGION = "us-east-1"


def investigate_incident(service_name, status, response_time_ms):
    client = boto3.client("bedrock-runtime", region_name=REGION)

    incident = {
        "service": service_name,
        "status": status,
        "response_time_ms": response_time_ms
    }

    prompt = f"""
You are an AI Site Reliability Engineering assistant.

Analyze this ClinicPulse healthcare service incident:

{json.dumps(incident, indent=2)}

Provide:
1. Incident summary
2. Observed evidence
3. Possible root causes
4. Recommended investigation steps
5. Suggested remediation

Rules:
- Use only the supplied monitoring evidence.
- Clearly distinguish confirmed observations from hypotheses.
- Never describe a response time as high, slow, or abnormal unless a baseline is provided.
- A DOWN status does not establish the root cause.
- Do not invent logs, CPU usage, memory usage, network failures, or deployment events.
- Recommend investigation steps before remediation.
- All remediation actions require human approval.
- Do not claim any recovery action has been executed.
- Keep the response concise.
"""

    response = client.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        inferenceConfig={
            "maxTokens": 400,
            "temperature": 0.2
        }
    )

    return response["output"]["message"]["content"][0]["text"]
