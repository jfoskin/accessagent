import json
from playwright.sync_api import sync_playwright
from axe_core_python.sync_playwright import Axe
from pathlib import Path

axe = Axe()

TEST_URL = Path("test_page.html").resolve().as_uri()

with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto(TEST_URL)

    result = axe.run(page)

    browser.close()

violations = result["violations"]
print(f"{len(violations)} violations found.")
print(json.dumps(violations, indent=2))
