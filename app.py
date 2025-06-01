from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright, TimeoutError
from flask_cors import CORS
import traceback

app = Flask(__name__)
CORS(app)

def extract_m3u8(url):
    results = {
        "source_url": url,
        "videos": [],
        "errors": [],
        "debug": []
    }
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                viewport={"width": 1280, "height": 720},
                java_script_enabled=True,
                locale="en-US"
            )
            context.set_extra_http_headers({
                "Accept-Language": "en-US,en;q=0.9"
            })

            page = context.new_page()

            def handle_response(response):
                try:
                    ct = response.headers.get("content-type", "")
                    if ".m3u8" in response.url or "application/vnd.apple.mpegurl" in ct:
                        results["videos"].append({
                            "video_url": response.url,
                            "content_type": ct
                        })
                except Exception as e:
                    results["errors"].append(str(e))

            context.on("response", handle_response)
            page.goto(url, timeout=60000)
            page.wait_for_timeout(15000)
            browser.close()
    except Exception as e:
        results["errors"].append(str(e))
        results["debug"].append(traceback.format_exc())
    return results

@app.route("/extract", methods=["POST"])
def extract():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400
    result = extract_m3u8(url)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
