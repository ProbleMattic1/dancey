import os, json, requests

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

def post_to_slack(text: str):
    if not SLACK_WEBHOOK:
        return False
    data = {"text": text}
    r = requests.post(SLACK_WEBHOOK, json=data, timeout=5)
    return r.ok

def post_to_discord(content: str):
    if not DISCORD_WEBHOOK:
        return False
    data = {"content": content}
    r = requests.post(DISCORD_WEBHOOK, json=data, timeout=5)
    return r.ok

def notify_result(title: str, summary: dict):
    # Lightweight formatter
    text = f"*{title}*\n```\n{json.dumps(summary, indent=2)[:3500]}\n```"
    ok = False
    try:
        ok = post_to_slack(text) or ok
    except Exception:
        pass
    try:
        ok = post_to_discord(f"**{title}**\n```json\n{json.dumps(summary, indent=2)[:1800]}\n```") or ok
    except Exception:
        pass
    return ok
