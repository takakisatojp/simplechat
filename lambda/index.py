# lambda/index.py
import json
import os
import urllib.request

# MEMO: Google Colab で立てたngrok の URL を環境変数にセットしておく
FASTAPI_URL = os.environ.get(
    "FASTAPI_URL",
    "https://your-colab-ngrok-url.ngrok-free.app"
)

def lambda_handler(event, context=None):
    try:
        print("Received event:", json.dumps(event))
        body = json.loads(event.get('body', '{}'))
        message = body.get('message', '')
        conversation_history = body.get('conversationHistory', [])
        
        print("Processing message:", message)

        payload = json.dumps({
            "prompt": message,
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }).encode("utf-8")

        req = urllib.request.Request(
            url=f"{FASTAPI_URL}/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=10) as res:
            res_text = res.read().decode("utf-8")
            print("FastAPI raw response:", res_text)
            data = json.loads(res_text)
            assistant_response = data.get("generated_text", "")

        messages = conversation_history + [
            {"role": "user",      "content": message},
            {"role": "assistant", "content": assistant_response}
        ]

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": messages
            })
        }
        
    except Exception as error:
        print("Error:", str(error))
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
