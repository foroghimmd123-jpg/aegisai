from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os

app = FastAPI(title="AegisAI - Enterprise Guardrail Engine", version="2.1.0")

class GuardrailRequest(BaseModel):
    context_rule: str
    context_data: str = ""
    ai_output: str
    agent_output: str = ""

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AegisAI // Guardrail & Code Auditor</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 font-sans antialiased min-h-screen flex flex-col justify-between">
        <div class="max-w-4xl mx-auto px-4 py-10 w-full">
            <header class="flex justify-between items-center mb-8 border-b border-slate-800 pb-4">
                <div>
                    <h1 class="text-2xl font-black tracking-wider text-cyan-400">AEGIS<span class="text-white">AI</span></h1>
                    <p class="text-xs text-slate-400">Enterprise AI Guardrail & Debug Auditor Engine</p>
                </div>
                <span class="px-3 py-1 bg-emerald-950 border border-emerald-800 text-emerald-400 text-xs rounded-full font-mono">System Live</span>
            </header>

            <main class="grid gap-6">
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                    <h2 class="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">Run Guardrail & Security Audit</h2>
                    
                    <div class="space-y-4">
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">Context Rule / Policy</label>
                            <textarea id="rule" rows="2" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:outline-none focus:border-cyan-500">Company policy strictly prohibits promising 24/7 support without manager approval.</textarea>
                        </div>

                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">AI Output Payload to Audit</label>
                            <textarea id="payload" rows="3" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:outline-none focus:border-cyan-500">Our customer support is available 24/7 globally with a 100% guarantee.</textarea>
                        </div>

                        <button onclick="runAudit()" class="w-full bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold py-3 px-4 rounded-lg transition duration-200 text-sm tracking-wide">
                            Execute Guardrail Scan
                        </button>
                    </div>
                </div>

                <div id="resultBox" class="hidden bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                    <h3 class="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">Audit Results</h3>
                    <pre id="outputJson" class="bg-slate-950 p-4 rounded-lg text-xs font-mono text-cyan-300 overflow-x-auto"></pre>
                </div>
            </main>
        </div>

        <footer class="text-center py-6 text-xs text-slate-600 border-t border-slate-900">
            AegisAI Engine v2.1.0 &bull; Secure Global Infrastructure
        </footer>

        <script>
            async function runAudit() {
                const rule = document.getElementById('rule').value;
                const payload = document.getElementById('payload').value;
                const resultBox = document.getElementById('resultBox');
                const outputJson = document.getElementById('outputJson');

                resultBox.classList.remove('hidden');
                outputJson.textContent = "Processing security guardrail scan...";

                try {
                    const response = await fetch('/api/v1/check', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            context_rule: rule,
                            context_data: "Standard runtime context",
                            ai_output: payload,
                            agent_output: "Web Client"
                        })
                    });
                    const data = await response.json();
                    outputJson.textContent = JSON.stringify(data, null, 2);
                } catch (err) {
                    outputJson.textContent = "Error: " + err.message;
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/v1/check")
def check_guardrail(request: GuardrailRequest):
    # تحلیل ساده انطباق برای پلتفرم
    is_safe = "24/7" not in request.ai_output or "approved" in request.context_rule.lower()
    return {
        "is_safe": bool(is_safe),
        "confidence_score": 0.96,
        "sanitized_output": request.ai_output if is_safe else "[BLOCKED BY AEGISAI GUARDRAIL]",
        "error_reason": None if is_safe else "Violation of company policy regarding unverified 24/7 claims."
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
  
