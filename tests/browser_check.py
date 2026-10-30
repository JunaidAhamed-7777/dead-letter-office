#!/usr/bin/env python3
"""Real Chromium flow checks; starts its own loopback server in this process."""
import json
import os
from pathlib import Path
import shutil
import sys
import threading
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from server import make_server
from playwright.sync_api import sync_playwright, expect


def main():
    server = make_server(0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}"
    checks, errors, external = [], [], []
    report = {"checks": checks, "page_errors": errors, "external_requests": external}
    try:
        with sync_playwright() as p:
            executable = os.getenv("CHROMIUM_PATH") or shutil.which("chromium")
            browser = p.chromium.launch(headless=True, **({"executable_path": executable} if executable else {}))
            context = browser.new_context(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce", accept_downloads=True)
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("request", lambda request: external.append(request.url) if not request.url.startswith((url, "data:", "blob:")) else None)
            page.goto(url)
            expect(page.locator("#ask-button")).to_be_enabled()
            checks.append("Actual archive API loads; search enabled")
            page.locator("#ask-button").click()
            expect(page.locator("#question")).to_have_attribute("aria-invalid", "true")
            checks.append("Empty validation keeps focus and inline error")
            page.locator("#question").fill("Was the lighthouse burning that night?")
            page.locator("#question").press("Control+Enter")
            expect(page.locator(".finding")).to_have_attribute("data-status", "uncertain")
            expect(page.locator(".finding-summary")).to_contain_text("disagree")
            expect(page.locator(".answer-quote")).to_have_count(3)
            checks.append("Real model search preserves three lighthouse passages and conflict notice")
            page.screenshot(path=str(ROOT / "evidence" / "desktop.png"), full_page=True)
            first = page.locator(".citation").first
            first.click()
            expect(page.locator("#letter-dialog")).to_be_visible()
            expect(page.locator(".highlight-passage")).to_have_count(1)
            page.keyboard.press("Escape")
            expect(page.locator("#letter-dialog")).not_to_be_visible()
            expect(first).to_be_focused()
            checks.append("Citation opens exact paragraph; Escape closes and restores focus")
            with page.expect_download() as download_info:
                page.get_by_role("button", name="Save findings .txt").click()
            download = download_info.value
            text = Path(download.path()).read_text()
            assert "L02-P1" in text and "L03-P1" in text and "Fictional collection" in text
            checks.append("Local findings download contains literal evidence and both conflict IDs")
            page.locator("#clear-question").click()
            expect(page.locator("#question")).to_have_value("")
            page.locator("#question").fill("How do I configure a Kubernetes cluster?")
            page.locator("#ask-button").click()
            expect(page.locator(".finding")).to_have_attribute("data-status", "unknown")
            expect(page.locator(".source-card")).to_have_count(0)
            checks.append("Out-of-domain search produces no invented evidence")
            page.locator("#nav-letters").click()
            expect(page.locator(".letter-card")).to_have_count(12)
            page.locator(".letter-card").first.click()
            expect(page.locator("#letter-dialog")).to_be_visible()
            page.go_back()
            expect(page.locator("#ask-view")).to_be_visible()
            expect(page.locator("#letter-dialog")).not_to_be_visible()
            expect(page.locator("#nav-ask")).to_be_focused()
            checks.append("Browser Back closes the old view's letter and focuses destination navigation")
            page.route("**/api/ask", lambda route: route.fulfill(status=500, content_type="application/json", body='{"error":"test failure"}'))
            page.locator("#question").fill("Why did the night train never leave?")
            page.locator("#ask-button").click()
            expect(page.locator(".error-state")).to_be_visible()
            expect(page.locator("#question")).to_have_value("Why did the night train never leave?")
            page.unroute("**/api/ask")
            page.get_by_role("button", name="Search again", exact=True).click()
            expect(page.locator(".finding")).to_be_visible()
            checks.append("Server failure retains query; retry recovers")
            for width in (390, 320):
                page.set_viewport_size({"width": width, "height": 844})
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"Overflow at {width}px"
                page.locator("#nav-letters").click()
                page.locator(".letter-card").first.click()
                expect(page.locator("#close-letter")).to_be_visible()
                page.keyboard.press("Escape")
                page.locator("#nav-ask").click()
            page.screenshot(path=str(ROOT / "evidence" / "mobile.png"), full_page=True)
            checks.append("320px and 390px layouts have no horizontal overflow; mobile dialog closes")
            assert page.evaluate("localStorage.length === 0 && sessionStorage.length === 0")
            assert not external, external
            assert not errors, errors
            checks.append("No external browser requests, persistent query storage, or JS page errors")
            browser.close()
            report["status"] = "passed"
    except Exception:
        report["status"] = "failed_or_blocked"
        report["error"] = traceback.format_exc()
        raise
    finally:
        server.shutdown()
        server.server_close()
        (ROOT / "evidence" / "browser-checks.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
