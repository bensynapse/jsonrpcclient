"""Check the built, versioned docs site in a real browser.

Usage: python .github/scripts/check_site.py SITE_DIR AXE_JS

SITE_DIR is what .github/scripts/build_docs_site.py makes. This serves it at
http://localhost:8765/jsonrpcclient/, the same path as on GitHub Pages, with
the root 404.html for any missing page, as Pages does. Set CHECK_SITE_PORT to
use another port.

The stable docs at the root: every page in the sitemap, plus the 404 page, in
light and dark mode at desktop and phone widths. Each release line under
/4.x/ and so on: every page in its sitemap, in light and dark mode at desktop
width. It fails if:

- axe-core finds a serious or critical accessibility problem,
- a page scrolls sideways, has a JavaScript error, or has no visible h1,
  description or canonical link,
- a link to another page of the site, or to an anchor on it, is broken,
- the root sitemap lists anything but root pages, or a canonical link names
  anything but a root page,
- a line's page with no root twin isn't marked noindex,
- the version selector is missing or doesn't list every line, or picking a
  line from a root page doesn't land on the same page in that line,
- /stable/ doesn't redirect to the root.

Needs playwright (pip install playwright, then playwright install chromium).
"""

import functools
import json
import os
import re
import sys
import threading
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, sync_playwright

# CHECK_SITE_PORT picks another port, to run two checks at once.
PORT = int(os.environ.get("CHECK_SITE_PORT", "8765"))
BASE = f"http://localhost:{PORT}/jsonrpcclient/"
LIVE = "https://bensynapse.github.io/jsonrpcclient/"
VIEWPORTS = {"desktop": (1280, 900), "phone": (375, 812)}


class Handler(SimpleHTTPRequestHandler):
    """Serve the site under /jsonrpcclient/, with 404.html for missing pages."""

    def translate_path(self, path: str) -> str:
        path = path.split("?", 1)[0].split("#", 1)[0]
        if not path.startswith("/jsonrpcclient/"):
            return ""
        return super().translate_path(path[len("/jsonrpcclient") :])

    def send_error(self, code: int, message: Any = None, explain: Any = None) -> None:
        if code != 404:
            super().send_error(code, message, explain)
            return
        body = (Path(self.directory) / "404.html").read_bytes()
        self.send_response(404)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        pass


class Server(ThreadingHTTPServer):
    def handle_error(self, request: Any, client_address: Any) -> None:
        # The browser often drops a connection it no longer needs.
        if not isinstance(sys.exc_info()[1], ConnectionError):
            super().handle_error(request, client_address)


def record(errors: list[str], exc: Exception) -> None:
    errors.append(str(exc))


def page_info(page: Page) -> dict[str, Any]:
    return page.evaluate(
        """() => {
        const q = (s) => document.querySelector(s);
        const h1 = [...document.querySelectorAll(".md-content h1")]
          .filter((h) => h.offsetParent !== null);
        const doc = document.documentElement;
        return {
          h1: h1.length,
          description: (q('meta[name="description"]') || {}).content || "",
          canonical: (q('link[rel="canonical"]') || {}).getAttribute?.("href") || "",
          robots: (q('meta[name="robots"]') || {}).content || "",
          overflow: doc.scrollWidth > doc.clientWidth,
          links: [...document.querySelectorAll("a[href]")].map((a) => a.href),
          ids: [...document.querySelectorAll("[id]")].map((e) => e.id),
          versions: [...document.querySelectorAll(".md-version__link")]
            .map((a) => a.href),
        };
      }"""
    )


def axe_problems(page: Page, axe: str) -> list[str]:
    page.add_script_tag(content=axe)
    violations: list[dict[str, Any]] = page.evaluate(
        """async () => {
        const result = await axe.run(document, {
          runOnly: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "best-practice"],
        });
        return result.violations.map((v) => ({
          id: v.id, impact: v.impact, nodes: v.nodes.map((n) => n.target.join(" ")),
        }));
      }"""
    )
    return [
        f"{v['id']} ({v['impact']}): {', '.join(v['nodes'][:3])}"
        for v in violations
        if v["impact"] in ("serious", "critical")
    ]


def sitemap(path: Path) -> list[str]:
    return re.findall(r"<loc>(.*?)</loc>", path.read_text())


class Checker:
    def __init__(self, site: Path, axe: str) -> None:
        self.site = site
        self.axe = axe
        self.problems: list[str] = []
        self.links: set[str] = set()
        self.ids: dict[str, set[str]] = {}
        self.visits = 0
        self.root_pages = [
            url.replace(LIVE, BASE) for url in sitemap(site / "sitemap.xml")
        ]
        self.versions = json.loads((site / "versions.json").read_text())
        self.homes = [f"{BASE}{v['version']}/" for v in self.versions]
        for url in self.root_pages:
            if any(url.startswith(home) for home in [*self.homes, BASE + "stable/"]):
                self.problems.append(
                    f"root sitemap lists {url}, which isn't a root page"
                )

    def visit(
        self, page: Page, errors: list[str], url: str, where: str
    ) -> dict[str, Any]:
        errors.clear()
        response = page.goto(url, wait_until="networkidle")
        self.visits += 1
        expected = 404 if url.endswith("no-such-page/") else 200
        status = response.status if response else None
        if status != expected:
            self.problems.append(f"{where}: status {status}")
        info = page_info(page)
        if info["h1"] != 1:
            self.problems.append(f"{where}: {info['h1']} visible h1")
        if not info["description"]:
            self.problems.append(f"{where}: no description")
        if info["overflow"]:
            self.problems.append(f"{where}: the page scrolls sideways")
        if expected == 200:
            self.check_canonical(info, url, where)
            if sorted(info["versions"]) != sorted(self.homes):
                self.problems.append(
                    f"{where}: version selector lists {info['versions']}"
                )
        self.problems.extend(f"{where}: JavaScript error {e}" for e in errors)
        self.problems.extend(f"{where}: {p}" for p in axe_problems(page, self.axe))
        self.links.update(info["links"])
        self.ids[url] = set(info["ids"])
        return info

    def check_canonical(self, info: dict[str, Any], url: str, where: str) -> None:
        canonical = info["canonical"]
        if not canonical:
            self.problems.append(f"{where}: no canonical link")
            return
        local = canonical.replace(LIVE, BASE)
        if not canonical.startswith(LIVE) or local not in self.root_pages:
            self.problems.append(f"{where}: canonical {canonical} isn't a stable page")
        home = next((h for h in self.homes if url.startswith(h)), None)
        if home is None:
            if local != url:
                self.problems.append(f"{where}: canonical {canonical} isn't this page")
            return
        twin = BASE + url[len(home) :]
        if local == twin:
            if "noindex" in info["robots"]:
                self.problems.append(f"{where}: noindex, but the root has this page")
        elif local != BASE or "noindex" not in info["robots"]:
            self.problems.append(f"{where}: canonical {canonical}, expected {twin}")

    def run(self) -> None:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            for scheme in ("light", "dark"):
                for name, (width, height) in VIEWPORTS.items():
                    pages = [*self.root_pages, BASE + "no-such-page/"]
                    if name == "desktop":
                        for v in self.versions:
                            locs = sitemap(self.site / v["version"] / "sitemap.xml")
                            home = f"{BASE}{v['version']}/"
                            pages.extend(u.replace(LIVE, home) for u in locs)
                    context = browser.new_context(
                        viewport={"width": width, "height": height},
                        color_scheme=scheme,
                        is_mobile=name == "phone",
                    )
                    page = context.new_page()
                    errors: list[str] = []
                    page.on("pageerror", functools.partial(record, errors))
                    for url in pages:
                        self.visit(page, errors, url, f"{url} ({scheme}, {name})")
                    context.close()
            context = browser.new_context()
            self.check_switching(context.new_page())
            context.close()
            browser.close()

    def check_switching(self, page: Page) -> None:
        """Pick each line from a root page, and follow a /stable/ address."""
        for v in self.versions:
            page.goto(BASE + "requests/#ids", wait_until="networkidle")
            page.hover(".md-version")
            page.click(f".md-version__link[href='{BASE}{v['version']}/']")
            expected = f"{BASE}{v['version']}/requests/#ids"
            try:
                page.wait_for_url(expected, timeout=10_000)
            except PlaywrightError:
                self.problems.append(
                    f"selector on /requests/ picked {v['version']}: {page.url}"
                )
        page.goto(BASE + "stable/requests/")
        try:
            page.wait_for_url(BASE + "requests/", timeout=10_000)
        except PlaywrightError:
            self.problems.append(f"/stable/requests/ went to {page.url}")

    def check_links(self) -> None:
        status: dict[str, int] = {}
        for link in sorted(self.links):
            # The banners and the 404 page link to the live site's address.
            url, fragment = urldefrag(link.replace(LIVE, BASE))
            if not url.startswith(BASE):
                continue
            if url not in status:
                status[url] = fetch_status(url)
            if status[url] != 200:
                self.problems.append(f"broken link: {link} ({status[url]})")
            elif fragment and url in self.ids and fragment not in self.ids[url]:
                self.problems.append(f"broken anchor: {link}")


def fetch_status(url: str) -> int:
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return int(response.status)
    except urllib.error.HTTPError as exc:
        return exc.code


def main(site: Path, axe: str) -> int:
    handler = functools.partial(Handler, directory=str(site))
    server = Server(("localhost", PORT), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    checker = Checker(site, axe)
    checker.run()
    checker.check_links()
    server.shutdown()
    for problem in checker.problems:
        print(problem)
    lines = ", ".join(v["version"] for v in checker.versions)
    print(
        f"{checker.visits} page views (lines {lines}), {len(checker.problems)} problems"
    )
    return 1 if checker.problems else 0


def parse_args(argv: list[str]) -> tuple[Path, str]:
    if len(argv) != 2:
        raise SystemExit(__doc__)
    return Path(argv[0]), Path(argv[1]).read_text()


if __name__ == "__main__":
    sys.exit(main(*parse_args(sys.argv[1:])))
