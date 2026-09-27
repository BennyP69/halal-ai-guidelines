#!/usr/bin/env python3
"""Halal AI Guidelines helper: search the owner's approved sources, read a source in full,
and verify that a quote really appears on a source page.

  python3 halal.py search "english words" [--ar "كلمات عربية"] [--no-youtube]
  python3 halal.py read URL
  python3 halal.py verify URL "exact quoted words"
  python3 halal.py recheck        (re-verify every «quote» in library.md against its links)
  python3 halal.py --selftest

On Windows, type `python` (or `py`) instead of `python3`.
Stdlib only (plus the yt-dlp CLI for YouTube). Network errors are reported per source,
never silently dropped, so "no results" and "source unreachable" are never confused.
"""
import contextlib
import html
import io
import ipaddress
import json
import re
import socket
import subprocess
import sys
import tempfile
import unicodedata
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126 Safari/537.36"}
YT_CHANNELS = [
    "GtownMasjid", "ManhajulHaqq", "markaz_raziyayn", "musunnah", "DaarusSunnah",
    "SalafiAudioUNLIMITED", "SalafiRecordings", "theguidedpath1", "Yasin_ibn_jamal",
    "TheTrueSalafiyyah", "MahinAhmedRahi", "ArRisaalahPublications", "adamibnzuber",
]
# Sites with no script-friendly search. The AI searches these with its own web-search tool.
WEB_SEARCH_SITES = ["binbaz.org.sa", "binothaimeen.net", "alfawzan.af.org.sa",
                    "alifta.gov.sa", "troid.org"]
UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
MIN_TEXT = 200  # fewer characters than this = an empty shell page, not an answer


# ---------------------------------------------------------------- fetch
def check_public(url):
    """Only http(s) links to public internet addresses. Links come from web-search results,
    so a hostile page must not be able to steer `read` at local files or the owner's network."""
    p = urllib.parse.urlsplit(url)
    if p.scheme not in ("http", "https") or not p.hostname:
        raise RuntimeError("only http(s) web links can be read")
    try:
        infos = socket.getaddrinfo(p.hostname, None)
    except socket.gaierror as e:
        raise RuntimeError(f"cannot find {p.hostname} ({e})")
    for info in infos:
        ip = ipaddress.ip_address(info[4][0].split("%")[0])
        if not ip.is_global:
            raise RuntimeError(f"{p.hostname} points to a private/local address ({ip}); refused")
    # ponytail: checked before connecting, not pinned; a DNS-rebinding host could still swap
    # addresses. Pin the resolved IP if this ever runs unattended on a server.


class _CheckedRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_public(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_OPENER = urllib.request.build_opener(_CheckedRedirects)


def to_uri(url):
    """Arabic letters and spaces in a link become %-escapes; existing escapes are kept."""
    return urllib.parse.quote(url, safe=":/?#[]@!$&'()*+,;=%~")


def same_page(requested, final):
    """False when a page ID (3+ digit path number) in the requested link is missing from the
    link we landed on, i.e. the site redirected to a different page."""
    want = re.findall(r"/(\d{3,})(?=/|$)", urllib.parse.urlsplit(requested).path)
    got = urllib.parse.unquote(urllib.parse.urlsplit(final).path)
    return all(re.search(rf"/{n}(/|$)", got) for n in want)


def fetch(url, timeout=25):
    url = to_uri(url)
    p = urllib.parse.urlsplit(url)
    if (p.hostname or "").endswith("binbaz.org.sa") and re.fullmatch(r"/[a-z]+/\d+/?", p.path):
        # binbaz sends /fatwas/N/ (no title part) to an UNRELATED fatwa, while
        # /fatwas/N/<anything> lands on fatwa N. same_page() below still double-checks.
        url = urllib.parse.urlunsplit(p._replace(path=p.path.rstrip("/") + "/x"))
    check_public(url)
    with _OPENER.open(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        if not same_page(url, r.geturl()):
            raise RuntimeError("redirected to a different page "
                               f"({urllib.parse.unquote(r.geturl())}); find the current link")
        return r.read().decode("utf-8", "ignore")


def html_to_text(s):
    s = re.sub(r"(?is)<(script|style|noscript|svg|header|footer|nav)\b.*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h[1-6]|tr)>", "\n", s)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    s = re.sub(r"[ \t\u00a0]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n\n", s).strip()


def main_html(h):
    """The page's main answer without menus and 'related' sidebars: the <article> with the most
    text, else <main>, else the whole page."""
    blocks = re.findall(r"(?is)<article\b.*?</article>", h) or re.findall(r"(?is)<main\b.*?</main>", h)
    best = max(blocks, key=lambda b: len(html_to_text(b)), default="")
    return best if len(html_to_text(best)) >= MIN_TEXT else h


def page_title(h):
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", h)
    return html_to_text(m.group(1)) if m else ""


# ---------------------------------------------------------------- search
def search_abukhadeejah(q):
    u = ("https://abukhadeejah.com/wp-json/wp/v2/search?per_page=10&search="
         + urllib.parse.quote(q))
    return [{"title": html.unescape(x["title"]), "url": x["url"]} for x in json.loads(fetch(u))]


def search_salafitranslations(q, ar=None):
    esc = lambda t: t.replace("'", "")  # PocketBase filter string; quotes stripped, never injected
    parts = [f"content~'{esc(q)}'", f"title~'{esc(q)}'"]
    if ar:
        parts.append(f"arabic_content~'{esc(ar)}'")
    u = ("https://salafitranslations.com/api/collections/fatwas/records?perPage=10"
         "&fields=title,author,slug&filter=" + urllib.parse.quote("(" + " || ".join(parts) + ")"))
    items = json.loads(fetch(u)).get("items", [])
    return [{"title": f'{x["title"]} ({x.get("author", "")})',
             "url": "https://salafitranslations.com/" + x["slug"]} for x in items]


def search_youtube_channel(ch, q):
    url = f"https://www.youtube.com/@{ch}/search?query=" + urllib.parse.quote(q)
    out = subprocess.run(["yt-dlp", "--flat-playlist", "--playlist-end", "3",
                          "--print", "%(id)s|%(title)s", url],
                         capture_output=True, encoding="utf-8", errors="replace", timeout=90)
    hits = []
    for line in out.stdout.splitlines():
        vid, _, title = line.partition("|")
        if len(vid) == 11:  # real video ids only; skips playlists that channel search can return
            hits.append({"title": f"{title} [@{ch}]",
                         "url": f"https://www.youtube.com/watch?v={vid}"})
    if not hits and out.returncode != 0:
        raise RuntimeError(out.stderr.strip().splitlines()[-1] if out.stderr.strip() else "yt-dlp failed")
    return hits


def cmd_search(q, ar=None, youtube=True):
    jobs = {"abukhadeejah.com": lambda: search_abukhadeejah(q),
            "salafitranslations.com": lambda: search_salafitranslations(q, ar)}
    if ar:
        jobs["abukhadeejah.com (arabic)"] = lambda: search_abukhadeejah(ar)
    if youtube:
        for ch in YT_CHANNELS:
            jobs[f"youtube @{ch}"] = (lambda c=ch: search_youtube_channel(c, q))
            if ar:
                jobs[f"youtube @{ch} (arabic)"] = (lambda c=ch: search_youtube_channel(c, ar))
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {k: ex.submit(f) for k, f in jobs.items()}
        results = {}
        for k, f in futs.items():
            try:
                results[k] = f.result()
            except Exception as e:  # report, never hide
                results[k] = f"UNREACHABLE: {str(e)[:120]}"
    total = 0
    for k, v in results.items():
        if isinstance(v, str):
            print(f"\n## {k}: {v}")
            continue
        print(f"\n## {k}: {len(v)} hit(s)")
        for h in v:
            print(f"- {h['title']}\n  {h['url']}")
        total += len(v)
    print(f"\n== {total} hit(s) from script-searchable sources.")
    print("== NOT searched by this script (search these with your web-search tool, "
          "e.g. 'site:binbaz.org.sa <arabic terms>'): " + ", ".join(WEB_SEARCH_SITES))
    print("== YouTube hits are leads only: titles/captions are not verified quotes.")


# ---------------------------------------------------------------- read
def read_salafitranslations(slug):
    u = ("https://salafitranslations.com/api/collections/fatwas/records?perPage=1&filter="
         + urllib.parse.quote(f"slug='{slug}'"))
    items = json.loads(fetch(u)).get("items", [])
    if not items:
        raise RuntimeError("no record with that slug")
    x = items[0]
    parts = [f"TITLE: {x.get('title')}", f"AUTHOR: {x.get('author')}",
             f"SOURCE: {html_to_text(x.get('source') or '')}"]
    if x.get("arabic_content"):
        parts.append("ARABIC ORIGINAL:\n" + html_to_text(x["arabic_content"]))
    parts.append("ENGLISH (site translation):\n" + html_to_text(x.get("content") or ""))
    if x.get("footnotes"):
        parts.append("FOOTNOTES:\n" + html_to_text(x["footnotes"]))
    return "\n\n".join(parts)


def read_binothaimeen(url):
    # The site is built by JavaScript: a plain download is an empty shell. Its own data API
    # returns the full Arabic Q&A, keyed by the ID at the end of the real page link.
    m = re.search(UUID, urllib.parse.unquote(url))
    if not m:
        raise RuntimeError("binothaimeen.net: use the page link that ends in an ID "
                           "(.../ar/voice_library/lessonDetails/<section>/<title>/<id>). "
                           "Old /content/<number> links open a blank page; web-search the title.")
    x = json.loads(fetch(f"https://shekhapi.binothaimeen.net/lessons/audios/show/{m.group(0)}/0/1"))
    if not x.get("success") or not x.get("data"):
        raise RuntimeError(f"site API has no item {m.group(0)}")
    x = x["data"]
    body = html_to_text(((x.get("objective") or {}).get("content") or {}).get("ar") or "")
    return (f"TITLE: {(x.get('title') or {}).get('ar', '')}\n"
            f"SOURCE: official site data for item {m.group(0)}\n\n{body}")


def vtt_to_text(path):
    lines, prev, stamp = [], None, "00:00:00"
    for ln in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        if "-->" in ln or not ln.strip() or ln.startswith(("WEBVTT", "Kind:", "Language:")):
            ts = re.match(r"(\d\d:\d\d:\d\d)", ln)
            if ts:
                stamp = ts.group(1)
            continue
        t = re.sub(r"<[^>]+>", "", ln).strip()
        if t and t != prev:
            lines.append(f"[{stamp}] {t}")
            prev = t
    return "\n".join(lines)


def read_youtube(url):
    with tempfile.TemporaryDirectory() as d:
        out = subprocess.run(["yt-dlp", "--skip-download", "--write-subs", "--write-auto-subs",
                              "--sub-langs", "ar,en,en-orig,ar-orig", "--sub-format", "vtt",
                              "--print", "before_dl:TITLE: %(title)s | CHANNEL: %(channel)s | DATE: %(upload_date)s",
                              "-o", f"{d}/%(id)s.%(ext)s", url],
                             capture_output=True, encoding="utf-8", errors="replace", timeout=180)
        err = (out.stderr.strip().splitlines() or [""])[-1][:200]
        files = sorted(Path(d).glob("*.vtt"))
        if not files:
            # a failed download (e.g. HTTP 429 rate limit) is NOT "this video has no captions"
            raise RuntimeError(f"yt-dlp failed: {err}" if out.returncode != 0 and err
                               else "no captions available for this video")
        parts = [out.stdout.strip()] + [
            f"CAPTIONS ({f.name.split('.')[-2]}, auto-captions may contain errors):\n"
            + vtt_to_text(f) for f in files]
        if out.returncode != 0:
            parts.append(f"NOTE: some caption tracks failed to download: {err}")
        return "\n\n".join(parts)


def cmd_read(url, quiet=False):
    host = re.sub(r"^www\.", "", urllib.parse.urlsplit(url).hostname or "")
    if host == "salafitranslations.com":
        text = read_salafitranslations(urllib.parse.urlsplit(url).path.strip("/"))
    elif host in ("youtube.com", "m.youtube.com", "youtu.be"):
        text = read_youtube(url)
    elif host == "binothaimeen.net":
        text = read_binothaimeen(url)
    else:
        try:
            page = fetch(url)
        except OSError as e:  # network errors; our own safety refusals pass through unchanged
            raise RuntimeError(f"{e} (try your web-fetch tool; if that fails too, "
                               "report this source as unreachable)")
        if "Just a moment" in page[:3000]:
            raise RuntimeError("site blocks scripts (Cloudflare). Open it with your web-fetch tool.")
        text = html_to_text(main_html(page))
        if len(text) < MIN_TEXT:
            raise RuntimeError(f"only {len(text)} characters of text: the page is probably built "
                               "by JavaScript. Open it with your web-fetch tool.")
        text = f"PAGE TITLE: {page_title(page)}\n\n{text}"
    if not quiet:
        print(f"URL: {url}\n\n{text}")
    return text


# ---------------------------------------------------------------- verify
AR_DIACRITICS = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed\u0640]")


def normalize(s):
    # NFKD + drop combining marks: "Ribā"/"Jāhiliyyah" match "Riba"/"Jahiliyyah", and Arabic
    # harakat/hamza-seats fold the same way; the explicit Arabic folds below then still apply.
    s = unicodedata.normalize("NFKD", html.unescape(s)).lower()
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = unicodedata.normalize("NFKC", s)
    s = AR_DIACRITICS.sub("", s).replace("ʿ", "").replace("ʾ", "")
    s = re.sub("[إأآٱ]", "ا", s).replace("ى", "ي").replace("ة", "ه")
    s = re.sub(r"[\u2018\u2019\u201c\u201d'\"«»]", "", s)
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def page_for_matching(url):
    return normalize(re.sub(r"\[\d\d:\d\d:\d\d\] ", "", cmd_read(url, quiet=True)))


def cmd_verify(url, quote):
    q = normalize(quote)
    if len(q.split()) < 2:
        print("TOO SHORT: one word proves nothing. Verify a whole phrase.")
        return 1
    try:
        page = page_for_matching(url)
    except Exception as e:
        print(f"UNVERIFIED: could not read source ({e})")
        return 2
    i = page.find(q)
    if i < 0:
        print("NOT FOUND: do not present this as a quote from this source.")
        return 1
    print("FOUND: the quote appears in the page's main text.")
    print(f"CONTEXT (normalised): ...{page[max(0, i - 120):i + len(q) + 120]}...")
    if len(q.split()) < 5:
        print("NOTE: short quote. Check the context above really says what you claim.")
    return 0


def cmd_recheck(path=None):
    """Re-verify every «quote» in library.md against the links in its own record."""
    lib = Path(path or HERE / "library.md").read_text(encoding="utf-8")
    records = re.split(r"\n(?=### )", lib.split("\n---\n", 1)[1])  # skip the format template
    cache, total, bad = {}, 0, 0
    for rec in records:
        if not rec.startswith("### "):
            continue
        print(f"\n### {rec.splitlines()[0][4:].strip()}")
        urls = dict.fromkeys(u.rstrip(".,;:") for u in re.findall(r"https?://[^\s()<>«»\"]+", rec))
        for u in urls:
            if u not in cache:
                try:
                    cache[u] = page_for_matching(u)
                except Exception as e:
                    cache[u] = e
            if isinstance(cache[u], Exception):
                print(f"  UNREADABLE  {u}\n              {str(cache[u])[:150]}")
        quotes = re.findall(r"«([^»]+)»", rec)
        for qt in quotes:
            total += 1
            hit = next((u for u in urls if isinstance(cache[u], str) and normalize(qt) in cache[u]), None)
            if hit:
                print(f"  FOUND       «{' '.join(qt.split())[:50]}» on {urllib.parse.unquote(hit)[:90]}")
            else:
                bad += 1
                print(f"  NOT FOUND   «{' '.join(qt.split())[:50]}»")
        if not quotes:
            print("  (no «quotes» in this record)")
    print(f"\n== {total - bad}/{total} quotes FOUND ({date.today()}).")
    return 1 if bad else 0


def selftest():
    assert normalize("«إِنَّمَا الأعمالُ»") == normalize("انما الاعمال")
    assert normalize("Ribā-Based  Loan!") == normalize("riba based loan")
    assert normalize("Jāhiliyyah ʿArafāt") == normalize("jahiliyyah arafat")
    assert normalize("هذا يعتبر من الربا") in normalize("قال: هَذَا يُعْتَبَرُ مِنَ الرِّبَا.")
    assert normalize("قمار") not in normalize("تجارة حلال")
    assert normalize(html_to_text("<b>Hello</b>,  WORLD")) == "hello world"
    assert html_to_text("<p>a</p><script>x</script><p>b</p>").split() == ["a", "b"]
    # links: only public http(s); Arabic/spaces escaped; redirects to another page ID caught
    for bad in ("file:///etc/hosts", "ftp://example.com/x", "http://127.0.0.1/",
                "http://10.0.0.1/", "http://172.16.1.21:86/ar/home", "http://169.254.169.254/"):
        try:
            check_public(bad)
            raise AssertionError(f"not refused: {bad}")
        except RuntimeError:
            pass
    assert to_uri("https://x.org/a b/حكم") == "https://x.org/a%20b/%D8%AD%D9%83%D9%85"
    assert to_uri("https://x.org/a%20b?q=1") == "https://x.org/a%20b?q=1"
    assert same_page("https://binbaz.org.sa/fatwas/12835/x", "https://binbaz.org.sa/fatwas/12835/%D8%AD")
    assert not same_page("https://binbaz.org.sa/fatwas/12835/", "https://binbaz.org.sa/fatwas/8842/a")
    assert same_page("https://abukhadeejah.com/a-post/", "https://abukhadeejah.com/a-post/")
    # verify reads the answer, not menus or "related fatwa" lists
    page = ("<nav>الربا حرام</nav><article class='fatwa'>" + "سؤال وجواب " * 30
            + "</article><article>الربا حرام</article>")
    assert "الربا" not in html_to_text(main_html(page))
    with contextlib.redirect_stdout(io.StringIO()):  # one word is refused up front, before any fetch
        assert cmd_verify("https://unused.invalid/", "الربا") == 1
    try:
        read_binothaimeen("https://binothaimeen.net/content/2433")
        raise AssertionError("old binothaimeen link accepted")
    except RuntimeError:
        pass
    # Windows: every text read/subprocess must say UTF-8, or Arabic is garbled / crashes
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "a.vtt").write_bytes("WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nهذا يعتبر من الربا\n"
                                        .encode("utf-8"))
        assert vtt_to_text(Path(d) / "a.vtt") == "[00:00:01] هذا يعتبر من الربا"
    src = Path(__file__).read_text(encoding="utf-8")
    assert not re.search(r"text=Tru" r"e|read_text\((errors|\))", src)
    print("selftest ok")


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):  # Windows pipes default to cp1252 and crash on Arabic
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    if a[0] == "--selftest":
        selftest()
    elif a[0] == "search" and len(a) >= 2:
        ar = a[a.index("--ar") + 1] if "--ar" in a[:-1] else None
        cmd_search(a[1], ar, youtube="--no-youtube" not in a)
    elif a[0] == "read" and len(a) == 2:
        try:
            cmd_read(a[1])
        except Exception as e:
            print(f"UNREADABLE: {e}")
            sys.exit(2)
    elif a[0] == "verify" and len(a) == 3:
        sys.exit(cmd_verify(a[1], a[2]))
    elif a[0] == "recheck" and len(a) <= 2:
        sys.exit(cmd_recheck(a[1] if len(a) == 2 else None))
    else:
        print(__doc__)
        sys.exit(64)
