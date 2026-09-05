import os
import random
import requests

# تنظیمات اصلی موتور بازاریابی AegisAI
CONFIG = {
    "telegram_token": os.getenv("TELEGRAM_BOT_TOKEN", "8884221288:AAHeB9Djm1RpjJ6RsLhFoyyoio2_pAY0pys"),
    "telegram_chat": os.getenv("TELEGRAM_CHAT_ID", "@ContentFactory99"),
    "twitter_token": os.getenv("TWITTER_BEARER_TOKEN", ""),
    "reddit_id": os.getenv("REDDIT_CLIENT_ID", ""),
    "reddit_secret": os.getenv("REDDIT_CLIENT_SECRET", ""),
    "reddit_user_agent": os.getenv("REDDIT_USER_AGENT", "AegisAI-Growth-Bot/1.0")
}

def generate_security_insight():
    insights = [
        "LLM hallucinations can leak unverified absolute promises in production AI agents. Secure your workflows instantly with AegisAI's adaptive guardrails and direct TRC20 verification. Try the live sandbox today!",
        "Stop prompt injections and unauthorized AI outputs. AegisAI provides real-time security guardrails with a self-improving memory database. Built for developers.",
        "Building AI apps? Ensure your LLM complies with strict business policies using AegisAI. Automated protection meets Web3 native billing."
    ]
    return random.choice(insights)

def post_to_telegram(text: str):
    url = f"https://api.telegram.org/bot{CONFIG['telegram_token']}/sendMessage"
    try:
        response = requests.post(url, json={"chat_id": CONFIG["telegram_chat"], "text": text})
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def post_to_twitter(text: str):
    if not CONFIG["twitter_token"]:
        print("[Twitter Simulation]:", text)
        return {"status": "simulated"}
    headers = {
        "Authorization": f"Bearer {CONFIG['twitter_token']}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post("https://api.twitter.com/2/tweets", json={"text": text}, headers=headers)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def post_to_reddit(text: str, subreddit: str = "LocalLLaMA"):
    if not CONFIG["reddit_id"] or not CONFIG["reddit_secret"]:
        print(f"[Reddit Simulation -> r/{subreddit}]:", text)
        return {"status": "simulated"}
    
    auth = requests.auth.HTTPBasicAuth(CONFIG["reddit_id"], CONFIG["reddit_secret"])
    data = {'grant_type': 'client_credentials'}
    headers = {'User-Agent': CONFIG["reddit_user_agent"]}
    
    try:
        res = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)
        token = res.json().get('access_token')
        if not token:
            return {"status": "error", "message": "Failed to get Reddit token"}
            
        headers = {'Authorization': f"bearer {token}", 'User-Agent': CONFIG["reddit_user_agent"]}
        payload = {
            'sr': subreddit,
            'kind': 'self',
            'title': 'Automated Security Guardrails for LLM Apps',
            'text': text
        }
        response = requests.post('https://oauth.reddit.com/api/submit', data=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    content = generate_security_insight()
    print("--- AegisAI Growth Engine Executing ---")
    
    # تلگرام کاملاً واقعی و زنده ارسال می‌کند
    telegram_res = post_to_telegram(content)
    print("Telegram Result:", telegram_res)
    
    # توییتر و ردیت آماده به کار (فعلاً در حالت امن یا کلیدهای متغیر محیطی)
    print("Twitter Result:", post_to_twitter(content))
    print("Reddit Result:", post_to_reddit(content))
  
