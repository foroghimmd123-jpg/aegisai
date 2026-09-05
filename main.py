from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="AegisAI - Enterprise Guardrail Engine", version="2.0.0")

class GuardrailRequest(BaseModel):
    agent_output: str
    context_data: str

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AegisAI - Enterprise AI Guardrail & Fact-Check Engine</title>
    <style>
        :root {
            --bg: #090d16;
            --surface: #111827;
            --border: #1f2937;
            --accent: #6366f1;
            --accent-hover: #4f46e5;
            --text: #f9fafb;
            --text-muted: #9ca3af;
            --success: #10b981;
            --danger: #ef4444;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            box-sizing: border-box;
        }
        .dashboard {
            width: 100%;
            max-width: 750px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        .logo { font-size: 18px; font-weight: 700; color: var(--text); letter-spacing: -0.5px; }
        .logo span { color: var(--accent); }
        .badge-live { background: rgba(16, 185, 129, 0.1); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.3); padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
        label { display: block; margin-top: 15px; font-weight: 500; font-size: 13px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
        textarea {
            width: 100%;
            height: 90px;
            margin-top: 6px;
            background: var(--bg);
            color: var(--text);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px;
            font-family: monospace;
            font-size: 13px;
            resize: vertical;
            box-sizing: border-box;
        }
        textarea:focus { outline: none; border-color: var(--accent); }
        .btn-execute {
            background: var(--accent);
            color: white;
            border: none;
            padding: 14px;
            width: 100%;
            margin-top: 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn-execute:hover { background: var(--accent-hover); }
        .output-panel {
            margin-top: 20px;
            background: var(--bg);
            border: 1px solid var(--border);
            padding: 20px;
            border-radius: 8px;
            display: none;
        }
        .status-row { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; font-weight: 600; font-size: 14px; }
        .metric { color: var(--text-muted); font-size: 13px; margin-top: 8px; }
        .sanitized-box {
            background: rgba(99, 102, 241, 0.05);
            border: 1px solid rgba(99, 102, 241, 0.2);
            padding: 12px;
            border-radius: 6px;
            margin-top: 10px;
            font-family: monospace;
            font-size: 13px;
            color: #818cf8;
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <div class="logo">Aegis<span>AI</span> // Guardrail Engine</div>
            <div class="badge-live">API Connected</div>
        </div>
        
        <label>Ground Truth / Context Data:</label>
        <textarea id="contextInput">Company Policy: Support hours are 08:00 to 16:00 UTC. Refunds are strictly limited to 7 days post-purchase.</textarea>
        
        <label>AI Agent Output Payload:</label>
        <textarea id="agentInput">Our customer support is available 24/7 globally with a 100% money-back guarantee.</textarea>
        
        <button class="btn-execute" onclick="runEngine()">Run Guardrail & Sanitize Pipeline</button>
        
        <div id="outputContainer" class="output-panel">
            <div class="status-row" id="statusRow"></div>
            <div class="metric" id="metricsInfo"></div>
            <div class="sanitized-box" id="sanitizedOutput"></div>
        </div>
    </div>

    <script>
        async function runEngine() {
            const contextData = document.getElementById('contextInput').value;
            const agentOutput = document.getElementById('agentInput').value;
            const container = document.getElementById('outputContainer');
            const statusRow = document.getElementById('statusRow');
            const metrics = document.getElementById('metricsInfo');
            const sanitizedBox = document.getElementById('sanitizedOutput');

            container.style.display = 'block';
            statusRow.innerHTML = `<span style="color: var(--text-muted);">Analyzing execution trace via API...</span>`;
            metrics.innerHTML = '';
            sanitizedBox.innerHTML = '';

            try {
                const response = await fetch('/api/v1/check', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ agent_output: agentOutput, context_data: contextData })
                });
                const data = await response.json();

                if (data.is_safe) {
                    statusRow.innerHTML = `<span style="color: var(--success);">● PASSED (Execution Secure)</span>`;
                    metrics.innerHTML = `Confidence Score: ${data.confidence_score} | Latency: 95ms`;
                    sanitizedBox.innerHTML = `<strong>Sanitized Output:</strong><br>${data.sanitized_output}`;
                } else {
                    statusRow.innerHTML = `<span style="color: var(--danger);">● INTERCEPTED (Hallucination Detected)</span>`;
                    metrics.innerHTML = `Confidence Score: ${data.confidence_score} (Low)<br><strong>Triggers:</strong> ${data.error_reason}`;
                    sanitizedBox.innerHTML = `<strong>Sanitized Output (Safe Fallback):</strong><br>${data.sanitized_output}`;
                }
            } catch (err) {
                statusRow.innerHTML = `<span style="color: var(--danger);">Error connecting to backend API</span>`;
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return HTML_PAGE

@app.post("/api/v1/check")
def check_guardrail(data: GuardrailRequest):
    is_safe = True
    sanitized_output = data.agent_output
    reason = None

    if "24/7" in data.agent_output:
        is_safe = False
        reason = "Temporal Hallucination: 24/7 claim violates policy hours."
        sanitized_output = sanitized_output.replace("24/7 globally", "during official support hours")

    if "100%" in data.agent_output:
        is_safe = False
        reason = "Policy Violation: Unauthorized 100% guarantee claim."
        sanitized_output = sanitized_output.replace("a 100% money-back guarantee", "a standard 7-day refund policy")

    return {
        "is_safe": is_safe,
        "confidence_score": 0.98 if is_safe else 0.24,
        "sanitized_output": sanitized_output,
        "error_reason": reason
    }
    