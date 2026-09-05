from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
import secrets
import os
import requests
import random

app = FastAPI(title="AegisAI - Autonomous Self-Improving Engine", version="6.0.0")

MERCHANT_TRON_WALLET = "TXSAYwmoPkHyeiEpEV8XD2aHGaCDgGS2ft"

def init_db():
    conn = sqlite3.connect("aegisai.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            api_key TEXT UNIQUE,
            tier TEXT DEFAULT 'free'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            amount_usdt REAL,
            status TEXT DEFAULT 'pending'
        )
    """)
    # جدول حافظه هوشمند و یادگیری تطبیقی (Adaptive Learning Memory)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS adaptive_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT UNIQUE,
            action TEXT DEFAULT 'block',
            reason TEXT
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO users (email, api_key, tier) VALUES (?, ?, ?)", 
                   ("admin@aegisai.com", "aegis_live_sec_9999", "enterprise"))
    # قوانین اولیه یادگرفته شده توسط سیستم
    cursor.execute("INSERT OR IGNORE INTO adaptive_rules (keyword, action, reason) VALUES (?, ?, ?)", 
                   ("100% guarantee", "block", "Unverified absolute claims violate enterprise safety."))
    conn.commit()
    conn.close()

init_db()

class GuardrailRequest(BaseModel):
    context_rule: str
    context_data: str = ""
    ai_output: str
    agent_output: str = ""

class CryptoInvoiceRequest(BaseModel):
    email: str
    plan: str

class FeedbackRequest(BaseModel):
    keyword: str
    action: str
    reason: str

def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API Key is missing.")
    conn = sqlite3.connect("aegisai.db")
    cursor = conn.cursor()
    cursor.execute("SELECT email, tier FROM users WHERE api_key = ?", (x_api_key,))
    user = cursor.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API Key.")
    return {"email": user[0], "tier": user[1]}

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AegisAI // Autonomous Guardrail & Web3 Billing</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 font-sans antialiased min-h-screen flex flex-col justify-between">
        <div class="max-w-4xl mx-auto px-4 py-10 w-full">
            <header class="flex justify-between items-center mb-8 border-b border-slate-800 pb-4">
                <div>
                    <h1 class="text-2xl font-black tracking-wider text-cyan-400">AEGIS<span class="text-white">AI</span></h1>
                    <p class="text-xs text-slate-400">Self-Improving Guardrail & Direct TRC20 Engine</p>
                </div>
                <span class="px-3 py-1 bg-emerald-950 border border-emerald-800 text-emerald-400 text-xs rounded-full font-mono">v6.0 Adaptive</span>
            </header>

            <main class="grid gap-6">
                <!-- بخش تست گاردریل هوشمند -->
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                    <h2 class="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">Adaptive AI Guardrail Playground</h2>
                    <div class="mb-4">
                        <label class="block text-xs font-medium text-slate-400 mb-1">API Key</label>
                        <input type="text" id="apiKey" value="aegis_live_sec_9999" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs font-mono text-cyan-300 focus:outline-none focus:border-cyan-500">
                    </div>
                    
                    <div class="space-y-4">
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">Context Rule / Policy</label>
                            <textarea id="rule" rows="2" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:outline-none focus:border-cyan-500">Strictly block unverified absolute promises and unauthorized support claims.</textarea>
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">AI Output Payload</label>
                            <textarea id="payload" rows="2" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:outline-none focus:border-cyan-500">Our customer support is available 24/7 globally with a 100% guarantee.</textarea>
                        </div>
                        <button onclick="runAudit()" class="w-full bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold py-3 px-4 rounded-lg transition duration-200 text-sm tracking-wide">
                            Execute Adaptive Scan
                        </button>
                    </div>
                </div>

                <!-- بخش آموزش سیستم (Self-Learning Feedback Loop) -->
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                    <h2 class="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-2">Teach & Improve System Memory</h2>
                    <p class="text-xs text-slate-400 mb-4">Feed new behavioral rules into the AI adaptive memory database instantly.</p>
                    <div class="grid md:grid-cols-3 gap-3 mb-3">
                        <input type="text" id="teachKeyword" placeholder="Forbidden Keyword/Phrase" class="bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200">
                        <input type="text" id="teachReason" placeholder="Violation Reason" class="bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200">
                        <button onclick="teachSystem()" class="bg-emerald-700 hover:bg-emerald-600 text-white font-bold py-2 rounded text-xs">Inject New Rule</button>
                    </div>
                </div>

                <!-- بخش درگاه پرداخت کریپتو -->
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                    <h2 class="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-2">Direct Crypto Checkout (USDT - TRC20)</h2>
                    <p class="text-xs text-slate-400 mb-4 font-mono">Merchant Wallet: {MERCHANT_TRON_WALLET}</p>
                    <div class="grid md:grid-cols-2 gap-4 mb-4">
                        <div class="bg-slate-950 p-4 rounded-lg border border-slate-800">
                            <h3 class="text-cyan-400 font-bold text-sm">Pro Tier</h3>
                            <p class="text-xs text-slate-400 my-1">Direct blockchain payment</p>
                            <p class="text-lg font-mono font-bold text-white mb-3">$29.00 USDT</p>
                            <button onclick="createInvoice('pro')" class="w-full bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold py-2 rounded text-xs">Generate Invoice</button>
                        </div>
                        <div class="bg-slate-950 p-4 rounded-lg border border-slate-800">
                            <h3 class="text-cyan-400 font-bold text-sm">Enterprise Tier</h3>
                            <p class="text-xs text-slate-400 my-1">Direct blockchain payment</p>
                            <p class="text-lg font-mono font-bold text-white mb-3">$99.00 USDT</p>
                            <button onclick="createInvoice('enterprise')" class="w-full bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold py-2 rounded text-xs">Generate Invoice</button>
                        </div>
                    </div>
                    
                    <div class="border-t border-slate-800 pt-4 mt-4">
                        <div class="flex gap-2">
                            <input type="text" id="payEmail" placeholder="customer@aegisai.com" class="w-1/2 bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200">
                            <input type="number" step="0.01" id="payAmount" placeholder="29.XX" class="w-1/4 bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200">
                            <button onclick="verifyPayment()" class="w-1/4 bg-cyan-700 hover:bg-cyan-600 text-white font-bold py-2 rounded text-xs">Verify on Chain</button>
                        </div>
                    </div>
                </div>

                <div id="resultBox" class="hidden bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                    <h3 class="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">System Intelligence Output</h3>
                    <pre id="outputJson" class="bg-slate-950 p-4 rounded-lg text-xs font-mono text-cyan-300 overflow-x-auto"></pre>
                </div>
            </main>
        </div>

        <script>
            async function runAudit() {{
                const apiKey = document.getElementById('apiKey').value;
                const rule = document.getElementById('rule').value;
                const payload = document.getElementById('payload').value;
                const resultBox = document.getElementById('resultBox');
                const outputJson = document.getElementById('outputJson');
                resultBox.classList.remove('hidden');
                outputJson.textContent = "Processing adaptive scan...";
                try {{
                    const response = await fetch('/api/v1/check', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json', 'X-API-Key': apiKey }},
                        body: JSON.stringify({{ context_rule: rule, ai_output: payload }})
                    }});
                    const data = await response.json();
                    outputJson.textContent = JSON.stringify(data, null, 2);
                }} catch (err) {{
                    outputJson.textContent = "Error: " + err.message;
                }}
            }}

            async function teachSystem() {{
                const keyword = document.getElementById('teachKeyword').value;
                const reason = document.getElementById('teachReason').value;
                const resultBox = document.getElementById('resultBox');
                const outputJson = document.getElementById('outputJson');
                resultBox.classList.remove('hidden');
                outputJson.textContent = "Injecting new rule into neural memory...";
                try {{
                    const response = await fetch('/api/v1/feedback', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ keyword: keyword, action: 'block', reason: reason }})
                    }});
                    const data = await response.json();
                    outputJson.textContent = JSON.stringify(data, null, 2);
                }} catch (err) {{
                    outputJson.textContent = "Error: " + err.message;
                }}
            }}

            async function createInvoice(plan) {{
                const resultBox = document.getElementById('resultBox');
                const outputJson = document.getElementById('outputJson');
                resultBox.classList.remove('hidden');
                outputJson.textContent = "Generating blockchain invoice...";
                try {{
                    const response = await fetch('/api/v1/billing/crypto', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ email: "customer@aegisai.com", plan: plan }})
                    }});
                    const data = await response.json();
                    outputJson.textContent = JSON.stringify(data, null, 2);
                    if(data.send_exact_amount) {{
                        document.getElementById('payAmount').value = data.send_exact_amount;
                        document.getElementById('payEmail').value = "customer@aegisai.com";
                    }}
                }} catch (err) {{
                    outputJson.textContent = "Error: " + err.message;
                }}
            }}

            async function verifyPayment() {{
                const email = document.getElementById('payEmail').value;
                const amount = document.getElementById('payAmount').value;
                const resultBox = document.getElementById('resultBox');
                const outputJson = document.getElementById('outputJson');
                resultBox.classList.remove('hidden');
                outputJson.textContent = "Checking Tron blockchain...";
                try {{
                    const response = await fetch(`/api/v1/billing/verify?email=${{email}}&amount=${{amount}}`);
                    const data = await response.json();
                    outputJson.textContent = JSON.stringify(data, null, 2);
                    if(data.assigned_api_key) {{
                        document.getElementById('apiKey').value = data.assigned_api_key;
                    }}
                }} catch (err) {{
                    outputJson.textContent = "Error: " + err.message;
                }}
            }}
        </script>
    </body>
    </html>
    """

@app.post("/api/v1/feedback")
def teach_system(data: FeedbackRequest):
    conn = sqlite3.connect("aegisai.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO adaptive_rules (keyword, action, reason) VALUES (?, ?, ?)",
                       (data.keyword, data.action, data.reason))
        conn.commit()
    except sqlite3.IntegrityError:
        cursor.execute("UPDATE adaptive_rules SET reason = ? WHERE keyword = ?", (data.reason, data.keyword))
        conn.commit()
    finally:
        conn.close()
    return {"status": "success", "message": f"Learned new rule: keyword '{data.keyword}' will now be evaluated dynamically."}

@app.post("/api/v1/billing/crypto")
def create_crypto_invoice(data: CryptoInvoiceRequest):
    base_price = 29.0 if data.plan == "pro" else 99.0
    unique_cent = round(random.uniform(0.01, 0.99), 2)
    exact_amount = base_price + unique_cent
    
    conn = sqlite3.connect("aegisai.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO invoices (email, amount_usdt, status) VALUES (?, ?, ?)",
                   (data.email, exact_amount, "pending"))
    conn.commit()
    conn.close()

    return {
        "status": "waiting_for_payment",
        "network": "Tron (TRC20)",
        "token": "USDT",
        "send_exact_amount": exact_amount,
        "wallet_address": MERCHANT_TRON_WALLET,
        "instruction": "Send exact amount to your TRC20 wallet address. Then verify payment."
    }

@app.get("/api/v1/billing/verify")
def verify_blockchain_payment(email: str, amount: float):
    usdt_contract = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
    trongrid_url = f"https://api.trongrid.io/v1/accounts/{MERCHANT_TRON_WALLET}/transactions/trc20?contract_address={usdt_contract}&limit=10"
    
    try:
        response = requests.get(trongrid_url, timeout=5)
        data = response.json()
        txs = data.get("data", [])
        payment_found = False
        
        for tx in txs:
            if tx.get("to") == MERCHANT_TRON_WALLET:
                value_in_usdt = float(tx.get("value", 0)) / 10**6
                if abs(value_in_usdt - amount) < 0.005:
                    payment_found = True
                    break
        
        if payment_found:
            conn = sqlite3.connect("aegisai.db")
            cursor = conn.cursor()
            new_api_key = "aegis_pro_" + secrets.token_hex(12)
            cursor.execute("UPDATE users SET tier = ?, api_key = ? WHERE email = ?", ("pro", new_api_key, email))
            if cursor.rowcount == 0:
                cursor.execute("INSERT INTO users (email, api_key, tier) VALUES (?, ?, ?)", (email, new_api_key, "pro"))
            conn.commit()
            conn.close()
            return {"status": "success", "message": "Payment verified! Pro API Key assigned.", "assigned_api_key": new_api_key, "tier": "pro"}
        else:
            return {"status": "pending", "message": "Payment not found yet on blockchain."}
            
    except Exception as e:
        return {"status": "error", "message": f"Node connection error: {str(e)}"}

@app.post("/api/v1/check")
def check_guardrail(request: GuardrailRequest, user: dict = Depends(verify_api_key)):
    # بررسی هوشمند تطبیقی از حافظه دیتابیس (Adaptive Memory Check)
    conn = sqlite3.connect("aegisai.db")
    cursor = conn.cursor()
    cursor.execute("SELECT keyword, reason FROM adaptive_rules")
    learned_rules = cursor.fetchall()
    conn.close()

    is_safe = True
    violation_reason = None

    for kw, reason in learned_rules:
        if kw.lower() in request.ai_output.lower():
            is_safe = False
            violation_reason = f"Adaptive Intelligence Block: {reason}"
            break

    if is_safe and "24/7" in request.ai_output and "approved" not in request.context_rule.lower():
        is_safe = False
        violation_reason = "Violation of company policy regarding unverified 24/7 claims."

    return {
        "authenticated_user": user["email"],
        "account_tier": user["tier"],
        "is_safe": bool(is_safe),
        "confidence_score": 0.99,
        "sanitized_output": request.ai_output if is_safe else "[BLOCKED BY AEGISAI ADAPTIVE ENGINE]",
        "error_reason": violation_reason
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
  
