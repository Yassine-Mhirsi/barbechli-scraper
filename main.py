from playwright.sync_api import sync_playwright
import json

def capture_network_requests():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-extensions',
                '--disable-logging',
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 800, 'height': 600},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            java_script_enabled=True,
        )

        page = context.new_page()
        response_body = None

        def handle_request(request):
            if request.resource_type == "xhr" and 'https://barbechli.tn/find/?q={%22uid' in request.url:
                response = request.response()
                if response:
                    try:
                        nonlocal response_body
                        response_body = response.text()
                        with open('response_body.json', 'w', encoding='utf-8') as f:
                            json.dump(json.loads(response_body), f, indent=2, ensure_ascii=False)
                        print("Response body saved to response_body.json")
                        page.close()  # Close page instead of entire context
                    except Exception as e:
                        print(f"Error capturing response: {str(e)}")

        page.on('request', handle_request)

        try:
            page.goto("https://barbechli.tn/product/3191a01878c09e98dd1a6c854a89ca03")
        except Exception as e:
            if "Target page, context or browser has been closed" not in str(e):
                print(f"An error occurred: {e}")
        finally:
            if not response_body:
                print("Target request not found")
            context.close()
            browser.close()

        return response_body

if __name__ == "__main__":
    result = capture_network_requests()
    if result:
        print("\nResponse Body:")
        print(json.dumps(json.loads(result), indent=2))