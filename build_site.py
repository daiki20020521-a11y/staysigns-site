#!/usr/bin/env python3
"""Publish staged, locally stored editorial pages to GitHub Pages.
All text is committed in articles.json. No AI API or paid service is called.
"""
import datetime as dt
import html
import json
import pathlib
import shutil
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent
DEST = ROOT / "_site"
BASE = "https://daiki20020521-a11y.github.io/staysigns-site/"
LAUNCH = dt.date(2026, 10, 17)

def esc(value):
    return html.escape(str(value), quote=True)

def layout(title, summary, inner, home_link="../index.html"):
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{esc(summary)}">
<title>{esc(title)}｜StaySigns Studio</title>
<style>*{{box-sizing:border-box}}body{{margin:0;background:#f4f9f8;color:#1b3d43;font-family:-apple-system,BlinkMacSystemFont,"Noto Sans JP","Hiragino Kaku Gothic ProN",sans-serif}}header{{padding:22px;background:#123f48;color:white}}header a{{color:white;text-decoration:none}}main{{max-width:790px;margin:35px auto;padding:30px 24px;background:white;border:1px solid #d7e4e0;border-radius:15px}}h1{{font-size:clamp(26px,5vw,36px);line-height:1.45}}h2{{font-size:22px;margin-top:38px}}p{{line-height:2;color:#48646b}}.sub{{color:#0f8070}}footer{{max-width:790px;margin:30px auto;padding:12px 24px;color:#5c7278;font-size:13px}}a{{color:#087566}}@media(max-width:760px){{main{{margin:0;border-radius:0}}}}</style>
</head><body><header><a href="{home_link}">← StaySigns Studio</a></header>
<main>{inner}</main><footer>StaySigns Studio｜施設ごとの運用・法令・翻訳内容は必ず確認してください。</footer></body></html>"""

def build():
    if DEST.exists():
        shutil.rmtree(DEST)
    (DEST / "articles").mkdir(parents=True)
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    shutil.copy2(ROOT / "demo.html", DEST / "demo.html")
    articles = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))
    today = dt.date.today()
    published = [x for x in articles if LAUNCH + dt.timedelta(weeks=x["week"]) <= today]
    links = "".join(f'<li><a href="articles/{esc(p["slug"])}.html">{esc(p["title"])}</a> — {esc(p["summary"])}</li>' for p in published)
    block = '<section><h2>宿泊運営に役立つ記事</h2><ul style="line-height:2.1">' + links + '</ul></section>'
    home = home.replace('<p class="notice">', block + '<p class="notice">', 1)
    (DEST / "index.html").write_text(home, encoding="utf-8")
    urls = ["index.html", "demo.html"]
    for post in published:
        section_html = "".join(f'<h2>{esc(heading)}</h2><p>{esc(body)}</p>' for heading, body in post["sections"])
        inner = f'<div class="sub">宿泊施設の運営メモ</div><h1>{esc(post["title"])}</h1><p>{esc(post["summary"])}</p>' + section_html + '<hr><p>案内書を作る際は <a href="../demo.html">StaySigns無料デモ</a> もお試しください。</p>'
        destination = "articles/" + post["slug"] + ".html"
        (DEST / destination).write_text(layout(post["title"], post["summary"], inner), encoding="utf-8")
        urls.append(destination)
    (DEST / ".nojekyll").touch()
    (DEST / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: " + BASE + "sitemap.xml\n", encoding="utf-8")
    root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for path in urls:
        ET.SubElement(ET.SubElement(root, "url"), "loc").text = BASE + path
    (DEST / "sitemap.xml").write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))
    print(f"Published {len(published)} staged articles on {today.isoformat()}.")

if __name__ == "__main__":
    build()
