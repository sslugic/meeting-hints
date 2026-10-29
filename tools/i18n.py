#!/usr/bin/env python3
"""Localize the Undertone site. Standard library only.

docs/index.html is the English source. Run from the repository root after editing it:

    python3 tools/i18n.py            # refresh en.json and rebuild every language page
    python3 tools/i18n.py check      # only validate docs/i18n/*.json against en.json

What a run does:
  1. Rewrites the generated blocks in docs/index.html (between <!--i18n:NAME--> markers):
     hreflang/canonical links, the root-only language auto-detect script, and the two language menus.
  2. Extracts every visible string into docs/i18n/en.json. A string is a run of text plus inline markup
     (<b>, <a>, <span>, <br>, ...) inside one element, or a translatable attribute (alt, aria-label,
     title, placeholder, aria-roledescription, data-play, data-pause, and the description/og meta tags).
     Keys are a slug of the text plus a hash of it, so they stay stable until the English text changes.
     Elements with translate="no" (and script, style, svg, pre) are left alone.
  3. Builds docs/<code>/index.html for every language from docs/i18n/<code>.json, with the right
     <html lang>/dir, relative paths moved one level up, and its own canonical and menu state.
     Missing or invalid translations fall back to English and are reported.

To translate a new or changed string, add its key from en.json to each docs/i18n/<code>.json and re-run.
Translations must keep the same tags (with the same attributes) as the English string; order may change.
"""
import hashlib
import html
import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
SOURCE = os.path.join(DOCS, "index.html")
I18N = os.path.join(DOCS, "i18n")
BASE_URL = "https://getundertone.app/"
STORAGE_KEY = "undertone-lang"

# (code, name in its own language, short label for the nav)
LANGS = [
    ("en", "English", "EN"),
    ("es", "Español", "ES"),
    ("fr", "Français", "FR"),
    ("de", "Deutsch", "DE"),
    ("it", "Italiano", "IT"),
    ("pt-BR", "Português (Brasil)", "PT"),
    ("nl", "Nederlands", "NL"),
    ("pl", "Polski", "PL"),
    ("tr", "Türkçe", "TR"),
    ("ru", "Русский", "RU"),
    ("uk", "Українська", "UK"),
    ("ar", "العربية", "AR"),
    ("hi", "हिन्दी", "HI"),
    ("ja", "日本語", "JA"),
    ("ko", "한국어", "KO"),
    ("zh-Hans", "简体中文", "简体"),
    ("zh-Hant", "繁體中文", "繁體"),
]
RTL = {"ar"}

INLINE = {"a", "abbr", "b", "br", "code", "em", "i", "kbd", "mark", "q", "s", "small", "span", "strong",
          "sub", "sup", "time", "u", "wbr"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
OPAQUE = {"script", "style", "svg", "pre"}
ATTRS = {"alt", "aria-label", "aria-roledescription", "title", "placeholder", "data-play", "data-pause"}
META_KEYS = {"description", "og:title", "og:description", "twitter:title", "twitter:description"}

GLOBE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
         'aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 '
         '6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/></svg>')
CHEV = ('<svg class="chev" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round" aria-hidden="true"><path d="M3 4.5l3 3 3-3"/></svg>')


# ---------------------------------------------------------------- generated blocks

def page_path(code):
    return "" if code == "en" else code + "/"


def head_block(code):
    out = ['<link rel="canonical" href="%s%s">' % (BASE_URL, page_path(code))]
    for c, _, _ in LANGS:
        out.append('<link rel="alternate" hreflang="%s" href="%s%s">' % (c, BASE_URL, page_path(c)))
    out.append('<link rel="alternate" hreflang="x-default" href="%s">' % BASE_URL)
    return "\n".join(out)


def detect_block():
    codes = json.dumps([c for c, _, _ in LANGS if c != "en"])
    return """<script>
  // Root page only: send first-time visitors to their language. A manual choice (stored by the language
  // menu) wins, ?lang=en always stays on English, and without JS everyone gets English.
  (function () {
    var codes = %s;
    function pick(tag) {
      tag = String(tag || "").toLowerCase();
      var base = tag.split("-")[0];
      if (base === "zh") return /-(hant|tw|hk|mo)(-|$)/.test(tag) ? "zh-Hant" : "zh-Hans";
      if (base === "pt") return "pt-BR";
      if (base === "en") return "en";
      return codes.indexOf(base) >= 0 ? base : null;
    }
    try {
      if (/[?&]lang=en(&|$)/.test(location.search)) return;
      var saved = null, target = null;
      try { saved = localStorage.getItem("%s"); } catch (e) {}
      if (saved) target = codes.indexOf(saved) >= 0 ? saved : null;
      else {
        var prefs = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language];
        for (var i = 0; i < prefs.length; i++) { var m = pick(prefs[i]); if (m) { target = m === "en" ? null : m; break; } }
      }
      if (target) location.replace(target + "/" + location.search + location.hash);
    } catch (e) {}
  })();
</script>""" % (codes, STORAGE_KEY)


def menu_block(cur, where, label):
    """Language menu with root-relative links; build() moves them one level up for language pages."""
    items = []
    for c, name, _ in LANGS:
        href = "./?lang=en" if c == "en" else c + "/"
        current = ' aria-current="page"' if c == cur else ""
        items.append('<li><a href="%s" hreflang="%s" lang="%s" data-lang="%s"%s>%s</a></li>'
                     % (href, c, c, c, current, name))
    name, short = [(n, s) for c, n, s in LANGS if c == cur][0]
    if where == "nav":
        summary = '<summary aria-label="%s">%s<span class="lang-cur" translate="no">%s</span>%s</summary>' % (
            label, GLOBE, short, CHEV)
    else:
        summary = '<summary>%s<span class="lang-cur" translate="no">%s</span>%s</summary>' % (GLOBE, name, CHEV)
    return '<details class="lang">%s<ul class="lang-menu" translate="no">%s</ul></details>' % (summary, "".join(items))


def set_block(s, name, content):
    pat = re.compile(r"<!--i18n:%s-->.*?<!--/i18n:%s-->" % (re.escape(name), re.escape(name)), re.S)
    if not pat.search(s):
        sys.exit("marker <!--i18n:%s--> not found in docs/index.html" % name)
    return pat.sub(lambda m: "<!--i18n:%s-->%s<!--/i18n:%s-->" % (name, content, name), s, count=1)


# ---------------------------------------------------------------- parsing

class Node(object):
    def __init__(self, tag, raw, attrs, start, end):
        self.tag, self.raw, self.attrs, self.start, self.end = tag, raw, dict(attrs), start, end
        self.children = []
        self.no = self.attrs.get("translate") == "no"


class Text(object):
    def __init__(self, start, end):
        self.start, self.end = start, end


class Parser(HTMLParser):
    def __init__(self, src):
        HTMLParser.__init__(self, convert_charrefs=False)
        self.src = src
        self.lines = [0]
        for m in re.finditer("\n", src):
            self.lines.append(m.end())
        self.root = Node("#root", "", [], 0, len(src))
        self.stack = [self.root]

    def off(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def _add(self, tag, attrs, void):
        st = self.off()
        raw = self.get_starttag_text()
        node = Node(tag, raw, attrs, st, st + len(raw))
        self.stack[-1].children.append(node)
        if not void and tag not in VOID:
            self.stack.append(node)

    def handle_starttag(self, tag, attrs):
        self._add(tag, attrs, False)

    def handle_startendtag(self, tag, attrs):
        self._add(tag, attrs, True)

    def handle_endtag(self, tag):
        st = self.off()
        en = self.src.index(">", st) + 1
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack[i].end = en
                del self.stack[i:]
                return

    def handle_data(self, data):
        st = self.off()
        self.stack[-1].children.append(Text(st, st + len(data)))

    def _ref(self):
        st = self.off()
        m = re.compile(r"&#?[0-9A-Za-z]+;?").match(self.src, st)
        self.stack[-1].children.append(Text(st, m.end()))

    def handle_entityref(self, name):
        self._ref()

    def handle_charref(self, name):
        self._ref()

    def handle_comment(self, data):
        self.stack[-1].children.append(Node("#comment", "", [], 0, 0))


def plain(raw):
    return html.unescape(re.sub(r"<[^>]*>", "", raw))


def has_letters(raw):
    return any(ch.isalpha() for ch in plain(raw))


def make_key(raw):
    words = re.findall(r"[a-z0-9]+", plain(raw).lower())[:5]
    slug = "_".join(words)[:40] or "x"
    return slug + "_" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:6]


def extract(src):
    """Return a list of (start, end, english_raw, is_attribute) translation units in document order."""
    parser = Parser(src)
    parser.feed(src)
    parser.close()
    units = []

    def inline_ok(n):
        if isinstance(n, Text):
            return True
        return n.tag in INLINE and all(inline_ok(c) for c in n.children)

    def flush(run):
        if not any(isinstance(c, Text) and src[c.start:c.end].strip() for c in run):
            for c in run:
                if isinstance(c, Node):
                    walk(c)
            return
        start, end = run[0].start, run[-1].end
        raw = src[start:end]
        start += len(raw) - len(raw.lstrip())
        end -= len(raw) - len(raw.rstrip())
        raw = src[start:end]
        if has_letters(raw):
            units.append((start, end, raw, False))

    def attrs(n):
        if n.tag in ("#root", "#comment"):
            return
        names = set(ATTRS)
        if n.tag == "meta" and (n.attrs.get("name") in META_KEYS or n.attrs.get("property") in META_KEYS):
            names.add("content")
        for m in re.finditer(r"""\s([A-Za-z_:][-A-Za-z0-9_:.]*)\s*=\s*("([^"]*)"|'([^']*)')""", n.raw):
            if m.group(1).lower() in names:
                g = 3 if m.group(3) is not None else 4
                val = m.group(g)
                if val.strip() and has_letters(val):
                    units.append((n.start + m.start(g), n.start + m.end(g), val, True))

    def walk(n):
        attrs(n)
        if n.tag in OPAQUE or n.no:
            return
        run = []
        for c in n.children:
            if inline_ok(c):
                run.append(c)
                if isinstance(c, Node):
                    visit_attrs(c)
            else:
                if run:
                    flush(run)
                run = []
                if isinstance(c, Node):
                    walk(c)
        if run:
            flush(run)

    def visit_attrs(n):
        # attributes on inline elements (alt, aria-label, title) are units of their own
        attrs(n)
        if not n.no:
            for c in n.children:
                if isinstance(c, Node):
                    visit_attrs(c)

    walk(parser.root)
    # drop units nested inside another unit (an attribute inside a translated run, or a revisited run)
    units = sorted(set(units), key=lambda u: (u[0], -u[1]))
    out, last_end = [], -1
    for u in units:
        if u[0] >= last_end:
            out.append(u)
            last_end = u[1]
        elif u[1] > last_end:
            sys.exit("overlapping translation units at offset %d" % u[0])
    return out


# ---------------------------------------------------------------- validation and build

def tags(s):
    return sorted(re.findall(r"<[^>]*>", s))


def problem(en, tr, is_attr):
    if not isinstance(tr, str) or not tr.strip():
        return "empty"
    if is_attr:
        if "<" in tr or '"' in tr:
            return 'attribute text may not contain < or "'
        return None
    if tags(en) != tags(tr):
        return "markup differs from English"
    if re.search(r"&(?![#A-Za-z0-9]+;)", tr):
        return "bare & (write &amp;)"
    return None


def load(code):
    path = os.path.join(I18N, code + ".json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def fix_paths(s):
    def rel(m):
        v = m.group(2)
        if re.match(r"(?:[a-z]+:|#|/)", v):
            return m.group(0)
        v = "../" + (v[2:] if v.startswith("./") else v)
        return '%s"%s"' % (m.group(1), v)
    return re.sub(r'(\s(?:href|src|poster)=)"([^"]*)"', rel, s)


def build_page(src, units, code, tr):
    out = src
    for st, en, raw, is_attr in sorted(units, key=lambda u: -u[0]):
        t = tr.get(make_key(raw))
        if t is None or problem(raw, t, is_attr):
            continue
        out = out[:st] + t + out[en:]
    label = tr.get(make_key("Language"), "Language")
    out = set_block(out, "head", head_block(code))
    out = set_block(out, "detect", "")
    out = set_block(out, "menu-nav", menu_block(code, "nav", label))
    out = set_block(out, "menu-foot", menu_block(code, "foot", label))
    out = re.sub(r"<!--/?i18n:[a-z-]+-->\n?", "", out)
    html_tag = '<html lang="%s"%s>' % (code, ' dir="rtl"' if code in RTL else "")
    out = out.replace('<html lang="en">', html_tag, 1)
    out = fix_paths(out)
    note = "<!-- Generated by tools/i18n.py from docs/index.html and docs/i18n/%s.json. Edit those, not this file. -->\n" % code
    return out.replace("<!doctype html>\n", "<!doctype html>\n" + note, 1)


def check(units, src, codes):
    en = {}
    attr_keys = set()
    for st, e, raw, is_attr in units:
        k = make_key(raw)
        en[k] = raw
        if is_attr:
            attr_keys.add(k)
    ok = True
    for code in codes:
        tr = load(code)
        if tr is None:
            print("%-8s missing docs/i18n/%s.json (page falls back to English)" % (code, code))
            ok = False
            continue
        missing = [k for k in en if k not in tr]
        stale = [k for k in tr if k not in en]
        bad = [(k, problem(en[k], tr[k], k in attr_keys)) for k in en if k in tr]
        bad = [(k, p) for k, p in bad if p]
        status = "ok" if not (missing or bad) else "NEEDS WORK"
        print("%-8s %d/%d translated, %d missing, %d invalid, %d stale  %s"
              % (code, len(en) - len(missing) - len(bad), len(en), len(missing), len(bad), len(stale), status))
        for k in missing[:20]:
            print("    missing  %s: %s" % (k, en[k][:90]))
        for k, p in bad[:20]:
            print("    invalid  %s: %s" % (k, p))
        if missing or bad:
            ok = False
    return ok


def main(argv):
    with open(SOURCE, encoding="utf-8") as f:
        src = f.read()
    new = set_block(src, "head", head_block("en"))
    new = set_block(new, "detect", detect_block())
    new = set_block(new, "menu-nav", menu_block("en", "nav", "Language"))
    new = set_block(new, "menu-foot", menu_block("en", "foot", "Language"))
    codes = [c for c, _, _ in LANGS if c != "en"]

    units = extract(new)
    if argv[1:2] == ["check"]:
        return 0 if check(units, new, argv[2:] or codes) else 1

    if new != src:
        with open(SOURCE, "w", encoding="utf-8") as f:
            f.write(new)
    os.makedirs(I18N, exist_ok=True)
    en = {}
    for st, e, raw, is_attr in units:
        en.setdefault(make_key(raw), raw)
    with open(os.path.join(I18N, "en.json"), "w", encoding="utf-8") as f:
        json.dump(en, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("en       %d strings -> docs/i18n/en.json" % len(en))

    for code in codes:
        tr = load(code) or {}
        page = build_page(new, units, code, tr)
        os.makedirs(os.path.join(DOCS, code), exist_ok=True)
        with open(os.path.join(DOCS, code, "index.html"), "w", encoding="utf-8") as f:
            f.write(page)
    print("built    %d language pages under docs/<code>/index.html" % len(codes))
    check(units, new, codes)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
