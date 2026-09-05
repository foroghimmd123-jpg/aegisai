import os
import requests
import random

# دریافت توکن توییتر از متغیرهای محیطی سرور
TWITTER_API_URL = "https://api.twitter.com/2/tweets"
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")

def generate_security_insight():
    # بانک محتواهای تخصصی برای جذب توسعه‌دهندگان
    insights = [
        "LLM hallucinations can leak unverified absolute promises in production AI agents. Secure your workflows instantly with AegisAI's adaptive guardrails and direct TRC20 verification. Try the live sandbox today!",
        "Stop prompt injections and unauthorized AI outputs. AegisAI provides real-time security guardrails with a self-improving memory database. Built for developers.",
        "Building AI apps? Ensure your LLM complies with strict business policies using AegisAI. Automated protection meets Web3 native billing."
    ]
    return random.choice(insights)

def post_to_twitter(text: str):
    if not TWITTER_BEARER_TOKEN:
        print("[AegisAI Agent] Twitter Token missing. Running in simulation mode:", text)
        return {"status": "simulated", "text": text}
    
    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    
    try:
        response = requests.post(TWITTER_API_URL, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    tweet_text = generate_security_insight()
    result = post_to_twitter(tweet_text)
    print("Marketing Execution Result:", result)
