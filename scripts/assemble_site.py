#!/usr/bin/env python3
"""Assemble multi-page site from design previews and Skie Finance source."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESIGNS = ROOT / "site-designs"

FONTS_LINK = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,400;1,9..144,500&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">"""

SITE_CSS = ROOT / "css" / "site.css"
SKIE_CSS = ROOT / "css" / "skie.css"


def extract_style(html: str) -> str:
    """Extract the main <style> block (largest) from preview HTML."""
    blocks = re.findall(r"<style>(.*?)</style>", html, re.DOTALL)
    if not blocks:
        return ""
    return max(blocks, key=len).strip()


def strip_draft_ui(html: str) -> str:
    html = re.sub(r'<div class="review">.*?</div>\s*', "", html, flags=re.DOTALL)
    html = re.sub(r'<span class="note">.*?</span>\s*', "", html, flags=re.DOTALL)
    html = re.sub(r'<div class="qbox"[^>]*>.*?</div>\s*', "", html, flags=re.DOTALL)
    html = re.sub(r"<script>.*?</script>\s*", "", html, flags=re.DOTALL)
    html = re.sub(r'<span class="q"[^>]*>.*?</span>', "", html, flags=re.DOTALL)
    html = re.sub(r'<span class="ph"[^>]*>(.*?)</span>', r"\1", html, flags=re.DOTALL)
    html = re.sub(r"https://claude\.ai/artifact/[^\"']+", lambda m: "#", html)
    html = re.sub(r'href="#studio"', 'href="/"', html)
    html = re.sub(r'href="#checklists"', 'href="/cheklists"', html)
    html = re.sub(r'href="#home"', 'href="/"', html)
    html = re.sub(r'href="#top"', 'href="/"', html)
    html = re.sub(r'href="https://skiedesignstudio\.com"', 'href="/skie-finance"', html)
    return html


def skie_source_html() -> str:
    import subprocess

    skie = ROOT / "skie-finance" / "index.html"
    if skie.exists() and 'data-product="skie"' in skie.read_text():
        # Rebuild body from committed one-pager when possible.
        try:
            return subprocess.check_output(
                ["git", "show", "fe0d914:index.html"],
                cwd=ROOT,
                stderr=subprocess.DEVNULL,
            ).decode()
        except subprocess.CalledProcessError:
            return skie.read_text()
    return subprocess.check_output(
        ["git", "show", "HEAD:index.html"],
        cwd=ROOT,
        stderr=subprocess.DEVNULL,
    ).decode()


def write_skie_finance():
    text = skie_source_html()
    if "<style>" not in text:
        raise SystemExit("Skie source missing inline styles")
    m = re.search(r"<style>(.*?)</style>", text, re.DOTALL)
    if not m:
        raise SystemExit("No style in index.html")
    skie_css = m.group(1)
    replacements = {
        "--shu": "--accent",
        "--shu-deep": "--accent-deep",
        "--sumi": "--ink",
        "--sumi-soft": "--muted",
        "--sumi-mute": "--faint",
        "--paper": "--bg",
        "--paper-deep": "--band",
        "--paper-edge": "--line",
        "--rule": "--line",
    }
    for old, new in replacements.items():
        skie_css = skie_css.replace(old, new)
    SKIE_CSS.write_text(skie_css)

    body = re.search(r"<body>(.*)</body>", text, re.DOTALL).group(1)
    body = body.replace('src="assets/', 'src="/assets/')
    body = body.replace(
        """<header class="topbar">
    <div class="mark">
      <div class="seal" aria-hidden="true">S</div>
      <div>Skie<span class="ja"> &nbsp;·&nbsp; intentional spending</span></div>
    </div>
    <nav class="nav">
      <a href="#features">Features</a>
      <a href="#budgets">Budgets</a>
      <a href="#trak">TRAK</a>
      <a href="#privacy">Privacy</a>
    </nav>
  </header>""",
        """<header class="top product-top">
    <div class="wrap product-top__inner">
      <a class="brand" href="/skie-finance"><span class="mark" aria-hidden="true">S</span><b>Skie Finance</b><small>· intentional spending</small></a>
      <nav class="nav" aria-label="Skie Finance">
        <a href="/">← All products</a>
        <a href="#features">Features</a>
        <a href="#budgets">Budgets</a>
        <a href="#trak">TRAK</a>
        <a href="#privacy">Privacy</a>
      </nav>
    </div>
  </header>""",
    )
    body = body.replace(
        """<footer>
    <div>© 2026 Skie</div>
    <a href="mailto:info@skiedesignstudio.com">info@skiedesignstudio.com</a>
  </footer>""",
        """<footer class="site-footer"><div class="wrap site-footer__inner"><span>© 2026 Skie Design Studio</span><a href="/">← All products</a><a href="mailto:info@skiedesignstudio.com">info@skiedesignstudio.com</a></div></footer>""",
    )
    body = body.replace('class="page"', 'class="wrap skie-wrap"')

    body = body.replace(
        '<div class="wrap skie-wrap">\n\n  <header class="product-top">',
        '<header class="product-top">',
        1,
    )
    body = body.replace(
        "</header>\n\n  <!-- HERO -->",
        "</header>\n\n<div class=\"wrap skie-wrap\">\n\n  <!-- HERO -->",
        1,
    )

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Skie Finance — Track spending intentionally</title>
{FONTS_LINK}
<link rel="stylesheet" href="/css/site.css" />
<link rel="stylesheet" href="/css/skie.css" />
</head>
<body class="product" data-product="skie">
{body.strip()}
</body>
</html>
"""
    out = ROOT / "skie-finance" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)


def write_studio_home():
    html = (DESIGNS / "studio-home.html").read_text()
    html = strip_draft_ui(html)
    start = html.find('<main id="view-home">')
    end = html.find("</main>", start) + len("</main>")
    if start < 0:
        raise SystemExit("studio view-home not found")
    main = html[start : html.index("</main>", start) + len("</main>")]
    main = main.replace('<main id="view-home">', "<main>")
    main = main.replace('href="#home"', 'href="/"')
    main = main.replace('href="#p-skie"', 'href="/skie-finance"')
    main = main.replace('href="#p-cheklists"', 'href="/cheklists"')
    main = main.replace('href="#p-reveal"', 'href="/reveal"')
    main = main.replace('href="#p-marginalia"', 'href="/marginalia"')
    main = main.replace(
        'href="https://skiedesignstudio.com"',
        'href="/skie-finance"',
    )
    main = re.sub(
        r'<a class="main" href="[^"]*" target="_blank" rel="noopener">About ChekLists →</a>',
        '<a class="main" href="/cheklists">About ChekLists →</a>',
        main,
    )
    main = re.sub(
        r'<a class="main" href="[^"]*" target="_blank" rel="noopener">About Reveal →</a>',
        '<a class="main" href="/reveal">About Reveal →</a>',
        main,
    )
    main = re.sub(
        r'<a class="main" href="[^"]*" target="_blank" rel="noopener">About Marginalia →</a>',
        '<a class="main" href="/marginalia">About Marginalia →</a>',
        main,
    )
    main = re.sub(
        r'<a class="main" href="[^"]*" target="_blank" rel="noopener">About Skie Finance →</a>',
        '<a class="main" href="/skie-finance">About Skie Finance →</a>',
        main,
    )

    studio_css = extract_style(html)
    studio_css = re.sub(r"/\* review bar \*/.*?body\.clean.*?\n", "", studio_css, flags=re.DOTALL)
    studio_css = re.sub(r"/\* draft notes \*/.*?body\.clean.*?\n", "", studio_css, flags=re.DOTALL)
    studio_css = re.sub(r"/\* site plan view \*/.*", "", studio_css, flags=re.DOTALL)

    redirect = """<script>
(function () {
  var skie = ["features","budgets","trak","privacy","download"];
  var id = (location.hash || "").slice(1);
  if (skie.indexOf(id) > -1) location.replace("/skie-finance#" + id);
})();
</script>"""

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover" />
<title>Skie Design Studio</title>
{FONTS_LINK}
<link rel="stylesheet" href="/css/site.css" />
<style>{studio_css}</style>
</head>
<body class="studio">
{main}
{redirect}
<script>
(function(){{
  var btn=document.getElementById("copy-email");
  if(!btn)return;
  btn.addEventListener("click",function(){{
    var t=document.getElementById("email").textContent;
    navigator.clipboard.writeText(t).then(function(){{ btn.textContent="Copied"; setTimeout(function(){{ btn.textContent="Copy address"; }},2000); }});
  }});
}})();
</script>
</body>
</html>
"""
    (ROOT / "index.html").write_text(page)


def write_product_page(name: str, title: str, src_file: str, main_id: str, accent: str, extra_nav: str = ""):
    html = (DESIGNS / src_file).read_text()
    css = extract_style(html)
    css = re.sub(r"/\* review bar \*/.*?\.tabs.*?\n", "", css, flags=re.DOTALL)
    css = re.sub(r"/\* question placeholder \*/.*?\.qbox.*?\n", "", css, flags=re.DOTALL)
    css = re.sub(r"\.review.*?\n", "", css)
    css = re.sub(r"\.note.*?\n", "", css)
    css = re.sub(r"\.ph.*?\n", "", css)
    css = re.sub(r"body\.clean.*?\n", "", css)

    css_path = ROOT / "css" / f"{name}.css"
    css_path.write_text(css)

    html = strip_draft_ui(html)
    start = html.find(f'<main id="{main_id}">')
    if start < 0 and main_id in ("", "none"):
        start = html.find("<header>")
        if start < 0:
            raise SystemExit(f"no body in {src_file}")
        body = html[start : html.rfind("</footer>") + len("</footer>")]
    elif start >= 0:
        end = html.find("</main>", start) + len("</main>")
        body = html[start:end]
        body = re.sub(r'<main id="[^"]+">', "<main>", body, count=1)
    else:
        raise SystemExit(f"main {main_id} not found in {src_file}")

    body = body.replace('href="#studio"', 'href="/"')
    body = body.replace("See all products", "← All products")
    if name == "cheklists":
        body = body.replace(
            '<a class="brand" href="#checklists">',
            '<a class="brand" href="/cheklists">',
        )
        body = body.replace('<a href="#studio">← All products</a>', '<a href="/">← All products</a>')
        nav_fix = '<nav class="nav" aria-label="ChekLists sections">'
        if '<a href="/">← All products</a>' not in body:
            body = body.replace(
                nav_fix,
                nav_fix + '\n        <a href="/">← All products</a>',
            )
    else:
        body = re.sub(
            r"<nav aria-label=\"Page sections\">",
            '<nav aria-label="Page sections"><a href="/">← All products</a>',
            body,
            count=1,
        )
        body = body.replace("<span>Contact email, same as Skie</span>", '<a href="mailto:info@skiedesignstudio.com">info@skiedesignstudio.com</a>')
        body = re.sub(
            r'<a class="btn ghost" href="#closing"><span class="ph">Second button</span></a>',
            '<a class="btn ghost" href="mailto:info@skiedesignstudio.com">Contact the studio</a>',
            body,
        )

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover" />
<title>{title}</title>
{FONTS_LINK}
<link rel="stylesheet" href="/css/site.css" />
<link rel="stylesheet" href="/css/{name}.css" />
</head>
<body class="product" data-product="{accent}">
{body}
<footer class="site-footer"><div class="wrap site-footer__inner"><span>© 2026 Skie Design Studio</span><a href="/">← All products</a></div></footer>
</body>
</html>
"""
    if name == "cheklists":
        page = page.replace(
            '<footer><div class="wrap"><span>© 2026 Skie Design Studio</span><a href="#studio">← All products</a></div></footer>',
            '<footer class="site-footer"><div class="wrap site-footer__inner"><span>© 2026 Skie Design Studio</span><a href="/">← All products</a></div></footer>',
        )
    if name in ("reveal", "marginalia"):
        page = page.replace('<a href="#top">← All products</a>', '<a href="/">← All products</a>')
        page = page.replace(
            r'<a class="btn ghost" href="#closing"><span class="ph">Second button</span></a>',
            '<a class="btn ghost" href="mailto:info@skiedesignstudio.com">Contact the studio</a>',
        )
        # Do not append duplicate footer
        page = re.sub(
            r'\n<footer class="site-footer"><div class="wrap site-footer__inner">.*?</footer>\n</body>',
            "\n</body>",
            page,
            flags=re.DOTALL,
        )

    out_dir = ROOT / name
    out_dir.mkdir(exist_ok=True)
    (out_dir / "index.html").write_text(page)


def write_site_css():
    SITE_CSS.parent.mkdir(exist_ok=True)
    SITE_CSS.write_text(
        """:root {
  --bg: #eef3f3;
  --band: #dde6e7;
  --card: #f6f9f9;
  --line: #c9d6d8;
  --ink: #13262a;
  --muted: #566b6f;
  --faint: #7d9195;
  --accent: #145f63;
  --accent-deep: #0a4a50;
  --dark: #0f2a2c;
  --dark-ink: #e6efef;
  --dark-muted: #9fb6b8;
  --dark-line: #26474a;
  --btn: #13262a;
  --btn-ink: #f4f7f7;
  --f-display: "Fraunces", Georgia, "Times New Roman", serif;
  --f-body: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
  --f-mono: "JetBrains Mono", ui-monospace, Menlo, monospace;
  --skie: #145f63;
  --chek: #6a1fd1;
  --reveal: #2c4f7c;
  --marg: #8a3a32;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0d1a1c;
    --band: #122426;
    --card: #152a2d;
    --line: #28403f;
    --ink: #e4eeee;
    --muted: #a3b7b9;
    --faint: #7f9799;
    --accent: #6cc3c6;
    --accent-deep: #4a9a9d;
    --dark: #07292b;
    color-scheme: dark;
  }
}
body[data-product="skie"] { --accent: var(--skie); --accent-deep: #0a4a50; }
body[data-product="cheklists"] { --accent: var(--chek); --accent-deep: #5520a8; }
body[data-product="reveal"] { --accent: var(--reveal); --accent-deep: #1e3a5c; }
body[data-product="marginalia"] { --accent: var(--marg); --accent-deep: #6b2e28; }

* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--ink);
  font-family: var(--f-body);
  font-size: 16px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}
a { color: inherit; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }
.wrap { max-width: 1120px; margin: 0 auto; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
@media (min-width: 720px) {
  .wrap { padding-left: max(48px, env(safe-area-inset-left, 0px)); padding-right: max(48px, env(safe-area-inset-right, 0px)); }
}

.product-top { padding-block: 24px; border-bottom: 1px solid var(--line); }
.product-top__inner { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.brand { display: flex; align-items: center; gap: 12px; text-decoration: none; }
.brand .mark {
  width: 36px; height: 36px; border-radius: 50%;
  display: grid; place-items: center;
  background: var(--accent); color: var(--bg);
  font: 500 18px var(--f-display);
}
.brand b { font: 500 21px var(--f-display); color: var(--ink); }
.brand small { color: var(--faint); font-family: var(--f-display); font-size: 14px; font-weight: 400; }
.nav { display: flex; gap: 22px; font-family: var(--f-mono); font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted); flex-wrap: wrap; }
.nav a { text-decoration: none; }
.nav a:hover { color: var(--ink); }
@media (max-width: 640px) { .product-top .nav a:not([href="/"]) { display: none; } }

.site-footer { border-top: 1px solid var(--line); }
.site-footer__inner {
  display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap;
  padding-block: 26px; font-size: 13.5px; color: var(--faint);
}
.site-footer a { text-decoration: none; }
.site-footer a:hover { color: var(--ink); }
"""
    )


def main():
    # Backup original Skie before overwriting root index
    backup = ROOT / "index.html"
    if backup.exists() and not (ROOT / "skie-finance" / "index.html").exists():
        pass
    write_site_css()
    write_skie_finance()
    write_studio_home()
    write_product_page(
        "cheklists",
        "ChekLists — Checklists that become tasks",
        "cheklists.html",
        "view-checklists",
        "cheklists",
    )
    write_product_page(
        "reveal",
        "Reveal — Share the trip",
        "reveal.html",
        "none",
        "reveal",
    )
    write_product_page(
        "marginalia",
        "Marginalia — Keep the passages that stay with you",
        "marginalia.html",
        "none",
        "marginalia",
    )
    print("Site assembled.")


if __name__ == "__main__":
    main()