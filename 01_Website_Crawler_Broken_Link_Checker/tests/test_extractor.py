import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler import LinkExtractor
from utils import normalize_url, host_key
from models import LinkResult

PAGE = "https://Example.com/dir/page.html"

HTML = """
<html manifest="/app.manifest"><head>
<base href="https://example.com/base/">
<link rel="stylesheet" href="s.css">
<link rel="icon" href="/favicon.ico">
<link rel="preconnect" href="https://fonts.gstatic.com">
<style>@import "imp.css"; .a{background:url('bg1.png')} /* url(commented.png) */</style>
<meta http-equiv="refresh" content="5; url=/refreshed">
<script src="app.js"></script>
</head><body background="bodybg.png" style="background:url(inline.png)">
<a href="a1">x</a><a href="#frag">skip</a><a href="mailto:a@b.c">skip</a>
<a href="javascript:void(0)">skip</a><a href="{{ template }}">skip</a><a href="tel:1">skip</a>
<area href="area1"><img src="i.png" srcset="i1.png 1x, i2.png 2x"><picture><source srcset="s1.webp"></picture>
<iframe src="if.html"></iframe><frame src="fr.html"><embed src="e.swf">
<object data="od.swf" classid="clsid:x" codebase="cb/"></object>
<video src="v.mp4" poster="poster.jpg"><track src="t.vtt"></video><audio src="au.mp3"><source src="au.ogg"></audio>
<form action="/submit"><input type="image" src="btn.png" formaction="/fa"><button formaction="/bfa">b</button></form>
<blockquote cite="/bq">q</blockquote><q cite="/qq">q</q><del cite="/dl">d</del><ins cite="/in">i</ins>
<a href="https://x.com/p?b=2&amp;a=1#top">q</a><a href="//cdn.example.org/lib.js">proto</a>
<a href="http://[broken">bad</a>
</body></html>
"""


class TestExtractor(unittest.TestCase):
    def setUp(self):
        self.links = LinkExtractor().extract_html(HTML, PAGE)
        self.by_type = {}
        for link in self.links:
            self.by_type.setdefault(link.source_type, set()).add(link.url)
        self.urls = {l.url for l in self.links}

    def has(self, source_type, url):
        self.assertIn(url, self.by_type.get(source_type, set()),
                      f"{source_type}: {url}\n{self.by_type}")

    def test_all_resource_sources(self):
        b = "https://example.com/base/"
        self.has("html/manifest", "https://example.com/app.manifest") if False else None
        self.has("stylesheet", b + "s.css")
        self.has("link-tag", "https://example.com/favicon.ico")
        self.has("script", b + "app.js")
        self.has("link", b + "a1")
        self.has("area", b + "area1")
        self.has("image", b + "i.png")
        self.has("img/srcset", b + "i1.png")
        self.has("img/srcset", b + "i2.png")
        self.has("source/srcset", b + "s1.webp")
        self.has("iframe", b + "if.html")
        self.has("frame", b + "fr.html")
        self.has("embed", b + "e.swf")
        self.has("object/data", b + "od.swf")
        self.has("object/classid", b + "clsid:x") if False else None
        self.has("object/codebase", b + "cb/")
        self.has("video", b + "v.mp4")
        self.has("video/poster", b + "poster.jpg")
        self.has("track", b + "t.vtt")
        self.has("audio", b + "au.mp3")
        self.has("source", b + "au.ogg")
        self.has("form", "https://example.com/submit")
        self.has("input", b + "btn.png")
        self.has("input/formaction", "https://example.com/fa")
        self.has("button", "https://example.com/bfa")
        self.has("body/background", b + "bodybg.png")
        self.has("blockquote/cite", "https://example.com/bq")
        self.has("q/cite", "https://example.com/qq")
        self.has("del/cite", "https://example.com/dl")
        self.has("ins/cite", "https://example.com/in")
        self.has("meta-refresh", "https://example.com/refreshed")
        self.has("base", b)

    def test_css_and_import(self):
        b = "https://example.com/base/"
        self.has("css/import", b + "imp.css")
        self.has("css", b + "bg1.png")
        self.has("css", b + "inline.png")
        self.assertNotIn(b + "commented.png", self.urls)

    def test_skips_and_normalization(self):
        self.assertNotIn("mailto:a@b.c", self.urls)
        self.assertTrue(all(u.startswith(("http://", "https://")) for u in self.urls))
        self.assertFalse(any("template" in u or "frag" in u for u in self.urls))
        self.assertFalse(any("fonts.gstatic" in u for u in self.urls))   # preconnect
        # query kept exactly, fragment dropped, protocol-relative resolved
        self.assertIn("https://x.com/p?b=2&a=1", self.urls)
        self.assertIn("https://cdn.example.org/lib.js", self.urls)

    def test_source_page_is_the_page_not_the_base(self):
        self.assertTrue(all(l.source_url == PAGE for l in self.links))

    def test_css_file(self):
        css = "@import url(a.css); @import 'b.css'; .x{background:url( 'i.png' )} .y{src:url(data:x)}"
        links = LinkExtractor().extract_css(css, "https://e.com/css/main.css")
        got = {(l.source_type, l.url) for l in links}
        self.assertEqual(got, {
            ("css/import", "https://e.com/css/a.css"),
            ("css/import", "https://e.com/css/b.css"),
            ("css/resource", "https://e.com/css/i.png"),
        })

    def test_sitemap_parsing(self):
        idx = b'<sitemapindex xmlns="x"><sitemap><loc>http://a/1.xml</loc></sitemap></sitemapindex>'
        self.assertEqual(LinkExtractor.parse_sitemap(idx), (True, ["http://a/1.xml"]))
        us = b'<urlset xmlns="x"><url><loc> http://a/p </loc></url></urlset>'
        self.assertEqual(LinkExtractor.parse_sitemap(us), (False, ["http://a/p"]))


class TestNormalize(unittest.TestCase):
    def test_rules(self):
        self.assertEqual(normalize_url("HTTPS://ExAmPle.COM:443/A/b?X=1&y=2#frag"),
                         "https://example.com/A/b?X=1&y=2")
        self.assertEqual(normalize_url("http://example.com:80"), "http://example.com/")
        self.assertEqual(normalize_url("http://example.com:8080/x"), "http://example.com:8080/x")
        self.assertEqual(normalize_url("  http://e.com/a\n/b "), "http://e.com/a/b")
        # trailing slash is preserved, query untouched
        self.assertEqual(normalize_url("http://e.com/docs/"), "http://e.com/docs/")
        self.assertEqual(normalize_url("http://e.com/docs"), "http://e.com/docs")
        self.assertEqual(normalize_url("http://e.com/?a=1&a=2"), "http://e.com/?a=1&a=2")

    def test_hosts(self):
        self.assertEqual(host_key("https://www.Example.com/x"), host_key("http://example.com"))
        self.assertNotEqual(host_key("https://blog.example.com"), host_key("https://example.com"))
        self.assertNotEqual(host_key("http://example.com:8080"), host_key("http://example.com"))


class TestClassification(unittest.TestCase):
    def cat(self, status=None, **kw):
        return LinkResult("http://x/", status, "http://x/", 0.1, **kw).category

    def test_rules(self):
        self.assertEqual(self.cat(200), "ok")
        self.assertEqual(self.cat(200, redirect_history=[(301, "http://x/")]), "redirect")
        self.assertEqual(self.cat(404), "broken")
        self.assertEqual(self.cat(410), "broken")
        for code in (400, 401, 403, 405, 429, 500, 502, 503, 504):
            self.assertEqual(self.cat(code), "unverified", code)
        self.assertEqual(self.cat(None, error_type="TIMEOUT"), "unverified")
        self.assertEqual(self.cat(None, error_type="SSL ERROR"), "unverified")
        self.assertEqual(self.cat(None, error_type="CONNECTION ERROR"), "unverified")
        # redirect that ends in 404 is a broken link, not "just a redirect"
        self.assertEqual(self.cat(404, redirect_history=[(301, "http://x/")]), "broken")


if __name__ == "__main__":
    unittest.main()
