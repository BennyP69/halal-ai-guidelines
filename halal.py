#!/usr/bin/env python3
"""Halal AI Guidelines helper: search the owner's approved sources, read a source in full,
and verify that a quote really appears on a source page.

  python3 halal.py search "english words" [--ar "كلمات عربية"] [--no-youtube]
  python3 halal.py read URL
  python3 halal.py verify URL "exact quoted words"
  python3 halal.py --selftest

Stdlib only (plus the yt-dlp CLI for YouTube). Network errors are reported per source,
never silently dropped, so "no results" and "source unreachable" are never confused.
"""
import html
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

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


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")


def html_to_text(s):
    s = re.sub(r"(?is)<(script|style|noscript|svg|header|footer|nav)\b.*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h[1-6]|tr)>", "\n", s)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    s = re.sub(r"[ \t\u00a0]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n\n", s).strip()


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
                         capture_output=True, text=True, timeout=90)
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


def read_youtube(url):
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["yt-dlp", "--skip-download", "--write-subs", "--write-auto-subs",
                        "--sub-langs", "ar,en,en-orig,ar-orig", "--sub-format", "vtt",
                        "--print", "before_dl:TITLE: %(title)s | CHANNEL: %(channel)s | DATE: %(upload_date)s",
                        "-o", f"{d}/%(id)s.%(ext)s", url],
                       capture_output=True, text=True, timeout=180)
        files = sorted(Path(d).glob("*.vtt"))
        if not files:
            raise RuntimeError("no captions available for this video")
        out = []
        for f in files:
            lines, prev, stamp = [], None, "00:00:00"
            for ln in f.read_text(errors="ignore").splitlines():
                if "-->" in ln or not ln.strip() or ln.startswith(("WEBVTT", "Kind:", "Language:")):
                    ts = re.match(r"(\d\d:\d\d:\d\d)", ln)
                    if ts:
                        stamp = ts.group(1)
                    continue
                t = re.sub(r"<[^>]+>", "", ln).strip()
                if t and t != prev:
                    lines.append(f"[{stamp}] {t}")
                    prev = t
            out.append(f"CAPTIONS ({f.name.split('.')[-2]}, auto-captions may contain errors):\n"
                       + "\n".join(lines))
        return "\n\n".join(out)


def cmd_read(url, quiet=False):
    host = urllib.parse.urlparse(url).netloc.replace("www.", "")
    if host == "salafitranslations.com":
        text = read_salafitranslations(urllib.parse.urlparse(url).path.strip("/"))
    elif host in ("youtube.com", "m.youtube.com", "youtu.be"):
        text = read_youtube(url)
    else:
        try:
            text = html_to_text(fetch(url))
        except Exception as e:
            raise RuntimeError(f"{e} (if blocked, open it with your web-fetch tool instead)")
        if "Just a moment" in text[:300]:
            raise RuntimeError("site blocks scripts (Cloudflare). Open it with your web-fetch tool.")
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


def cmd_verify(url, quote):
    try:
        text = cmd_read(url, quiet=True)
    except Exception as e:
        print(f"UNVERIFIED: could not read source ({e})")
        return 2
    page = normalize(re.sub(r"\[\d\d:\d\d:\d\d\] ", "", text))
    if normalize(quote) in page:
        print("FOUND: the quote appears on the source page.")
        return 0
    print("NOT FOUND: do not present this as a quote from this source.")
    return 1


def selftest():
    assert normalize("«إِنَّمَا الأعمالُ»") == normalize("انما الاعمال")
    assert normalize("Ribā-Based  Loan!") == normalize("riba based loan")
    assert normalize("Jāhiliyyah ʿArafāt") == normalize("jahiliyyah arafat")
    assert normalize("هذا يعتبر من الربا") in normalize("قال: هَذَا يُعْتَبَرُ مِنَ الرِّبَا.")
    assert normalize("قمار") not in normalize("تجارة حلال")
    assert normalize(html_to_text("<b>Hello</b>,  WORLD")) == "hello world"
    assert html_to_text("<p>a</p><script>x</script><p>b</p>").split() == ["a", "b"]
    print("selftest ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    if a[0] == "--selftest":
        selftest()
    elif a[0] == "search" and len(a) >= 2:
        ar = a[a.index("--ar") + 1] if "--ar" in a else None
        cmd_search(a[1], ar, youtube="--no-youtube" not in a)
    elif a[0] == "read" and len(a) == 2:
        try:
            cmd_read(a[1])
        except Exception as e:
            print(f"UNREADABLE: {e}")
            sys.exit(2)
    elif a[0] == "verify" and len(a) == 3:
        sys.exit(cmd_verify(a[1], a[2]))
    else:
        print(__doc__)
        sys.exit(64)
