#!/usr/bin/env python3
"""Structural checks for the caroco.pt static site.

Run it from anywhere: scripts/check

Every check here exists because the thing it guards fails SILENTLY. Merging a pull
request is what publishes caroco.pt, there is no staging step, so a mistake that
looks fine in the browser is a mistake that is live. See CLAUDE.md for the
invariants these encode.

Standard library only, by design. This repo has no dependencies and no build step.
"""

import datetime
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
BLOCKS = ROOT / ".github" / "blocks"

SITE = "https://caroco.pt"

# 404.html is deliberately different: no description, no canonical, no og block,
# and it carries noindex. Every check that talks about indexable pages excludes it.
NOT_INDEXABLE = {"404.html"}

# Files the dash rule applies to. Listed explicitly rather than globbed so that
# binaries are never read and so that pedidos/ can never be included by accident:
# a member's request file may contain anything and CLAUDE.md forbids editing it.
DASH_SCOPE = [
    "public/robots.txt",
    "public/sitemap.xml",
    "public/assets/site.css",
    "public/assets/site.js",
    "public/assets/fonts/README.md",
    "README.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    ".github/pull_request_template.md",
]

# Hosts a page load is allowed to reach. Everything else must be served from this
# repo. The fonts used to come from fonts.googleapis.com, which sent every
# visitor's IP to Google before they had done anything, and contradicted the
# argument in site.js that cookieless analytics need no consent banner. Adding a
# host here should be a deliberate decision, visible in a diff.
ALLOWED_ORIGINS = {
    "caroco.pt",
    "static.cloudflareinsights.com",  # the analytics beacon, see site.js
}

# Elements whose src or href causes a request when the page loads. A plain text
# link is not one of these: it only reaches a third party if the visitor clicks it.
LOADING_TAGS = r"link|script|img|source|iframe|video|audio|embed|object"

# Nothing on this site needs a 300 KB image. The realistic way one arrives is
# straight off a phone, where a portrait meant for a 108 px circle weighs 4 MB,
# and nobody notices because it looks identical in the browser.
IMAGE_BUDGET = 300 * 1024

# Portraits are displayed in a 108 px circle, so 216 covers a 2x screen and
# anything beyond that is bytes no visitor can see. The eight files were once as
# large as 760 px, which is where two thirds of the weight of /orgaos-sociais went.
# The short side is what matters: object-fit crops the long one.
PORTRAIT_MIN = 216
PORTRAIT_MAX = 400

# U+2012 figure dash, U+2013 en dash, U+2014 em dash, U+2015 horizontal bar, plus the HTML
# entity spellings of the two that matter. Written as escapes so that this file, which
# enforces the rule, does not itself contain the characters it rejects.
DASH_LITERAL = re.compile("[\u2012\u2013\u2014\u2015]")
DASH_ENTITY = re.compile(r"&(?:mdash|ndash);|&#(?:8211|8212);|&#x201[34];", re.I)

# Shared markup blocks. Byte identical across their scope today, and that is a
# property worth keeping: an eight file edit that lands on seven files leaves one
# page stale with no visible symptom. "all" means every page, "indexable" means
# every page except 404.html.
SHARED_BLOCKS = [
    ("head-assets.html", "all"),
    ("lang-nav.html", "all"),
    ("tabs-nav.html", "all"),
    ("footer.html", "all"),
    ("social-head.html", "indexable"),
]

# The tabs nav is identical everywhere except for which link carries this, so it
# is removed before the blocks are compared. Check 4 verifies it separately.
ARIA_CURRENT = ' aria-current="page"'


class Report:
    """Collects failures and warnings, then renders them for a terminal and for
    the GitHub pull request page."""

    def __init__(self):
        self.failures = []
        self.warnings = []

    def fail(self, where, pt, en):
        self.failures.append((where, pt, en))

    def warn(self, where, pt, en):
        self.warnings.append((where, pt, en))

    def render_terminal(self):
        for label, items in (("FALHA / FAIL", self.failures), ("AVISO / WARNING", self.warnings)):
            for where, pt, en in items:
                print(f"\n{label}  {where}")
                print(f"  PT  {pt}")
                print(f"  EN  {en}")

    def render_summary(self):
        """Append a readable summary to the pull request page.

        Non technical association members open pull requests here (see
        CONTRIBUTING.md), and "job failed, see log" is useless to them. So every
        message names the file and the fix, in both languages.
        """
        path = os.environ.get("GITHUB_STEP_SUMMARY")
        if not path:
            return
        lines = []
        if self.failures:
            lines.append("## Verificações falharam / Checks failed\n")
            for where, pt, en in self.failures:
                lines.append(f"**`{where}`**\n")
                lines.append(f"- PT: {pt}")
                lines.append(f"- EN: {en}\n")
        else:
            lines.append("## Tudo certo / All checks passed\n")
        if self.warnings:
            lines.append("## Avisos, não bloqueiam / Warnings, non blocking\n")
            for where, pt, en in self.warnings:
                lines.append(f"**`{where}`**\n")
                lines.append(f"- PT: {pt}")
                lines.append(f"- EN: {en}\n")
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")


def pages():
    """Every page, sorted, as (filename, text)."""
    return [(p.name, p.read_text(encoding="utf-8")) for p in sorted(PUBLIC.glob("*.html"))]


def url_for(name):
    """The real URL of a page. Cloudflare serves missao.html at /missao, see the
    html_handling setting in wrangler.jsonc."""
    return "/" if name == "index.html" else "/" + name[: -len(".html")]


def rel(path):
    return str(Path(path).relative_to(ROOT)) if Path(path).is_absolute() else str(path)


# ---------------------------------------------------------------- check 1


def check_span_parity(report):
    """Both languages live in the DOM as sibling spans and site.css hides the
    inactive one. So a missing translation is invisible to anyone browsing in
    Portuguese, including whoever wrote, reviewed and merged the change. Only an
    English visitor sees the hole. Counting is exact: every class="pt" and
    class="en" in this repo is a span with a single class."""
    for name, text in pages():
        pt = text.count('class="pt"')
        en = text.count('class="en"')
        if pt != en:
            report.fail(
                f"public/{name}",
                f"{pt} blocos com class=\"pt\" e {en} com class=\"en\". "
                "Cada texto precisa das duas línguas, lado a lado.",
                f"{pt} blocks with class=\"pt\" and {en} with class=\"en\". "
                "Every piece of text needs both languages, side by side.",
            )


# ---------------------------------------------------------------- check 2


def check_dashes(report):
    """No em-dashes or en-dashes anywhere. README.md and CLAUDE.md both state this
    as absolute. Scoped to files the maintainer writes: pedidos/ is excluded
    because a member's request text must never be edited."""
    targets = [f"public/{n}" for n, _ in pages()] + DASH_SCOPE
    for target in targets:
        path = ROOT / target
        if not path.exists():
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            hit = DASH_LITERAL.search(line) or DASH_ENTITY.search(line)
            if hit:
                report.fail(
                    f"{target}:{lineno}",
                    f"travessão ou meia risca em \"{hit.group(0)}\": "
                    "use uma vírgula, dois pontos, parênteses ou um ponto médio ·",
                    f"em-dash or en-dash in \"{hit.group(0)}\": "
                    "use a comma, colon, parentheses, or a middle dot ·",
                )


# ---------------------------------------------------------------- check 3


def check_shared_blocks(report):
    """The head, the language toggle, the tabs nav and the legal footer are
    duplicated across the pages on purpose: the nav must be real markup in the
    served HTML, not injected by JavaScript, and the legal footer has to be on
    every page for the Google for Nonprofits requirement. Duplication is fine.
    Duplication that has silently drifted apart is not."""
    for filename, scope in SHARED_BLOCKS:
        ref_path = BLOCKS / filename
        if not ref_path.exists():
            continue
        ref = ref_path.read_text(encoding="utf-8").strip("\n")
        for name, text in pages():
            if scope == "indexable" and name in NOT_INDEXABLE:
                continue
            haystack = text.replace(ARIA_CURRENT, "") if filename == "tabs-nav.html" else text
            if ref not in haystack:
                report.fail(
                    f"public/{name}",
                    f"o bloco partilhado .github/blocks/{filename} não aparece aqui palavra "
                    "por palavra. Copie o ficheiro de referência para dentro desta página. "
                    "Se a mudança é intencional, mude também a referência, e todas as outras páginas.",
                    f"the shared block .github/blocks/{filename} does not appear here verbatim. "
                    "Copy the reference file into this page. If the change is intentional, change "
                    "the reference too, and every other page.",
                )


# ---------------------------------------------------------------- check 4


def check_page_identity(report):
    """README.md tells you to make a new page by copying contactos.html and then
    changing the title, description, canonical and og tags. Every one of those is
    a thing you can forget, and a canonical pointing at the wrong page is a real
    SEO bug that deploys with no visible symptom at all."""
    for name, text in pages():
        where = f"public/{name}"
        url = url_for(name)
        expected = SITE + url

        title = re.search(r"<title>(.*?)</title>", text, re.S)
        if not title or not title.group(1).strip():
            report.fail(where, "falta o <title>.", "the <title> is missing or empty.")

        current = re.findall(r'<a href="([^"]+)"' + re.escape(ARIA_CURRENT), text)

        if name in NOT_INDEXABLE:
            if current:
                report.fail(
                    where,
                    'esta página não é indexável e não deve ter aria-current="page".',
                    'this page is not indexable and should carry no aria-current="page".',
                )
            if 'content="noindex"' not in text:
                report.fail(
                    where,
                    'falta <meta name="robots" content="noindex" />.',
                    'the <meta name="robots" content="noindex" /> tag is missing.',
                )
            continue

        if len(current) != 1:
            report.fail(
                where,
                f'aria-current="page" aparece {len(current)} vezes na navegação, deve aparecer '
                "exatamente uma.",
                f'aria-current="page" appears {len(current)} times in the nav, it must appear '
                "exactly once.",
            )
        elif current[0] != url:
            report.fail(
                where,
                f'aria-current="page" está no separador {current[0]}, devia estar em {url}.',
                f'aria-current="page" is on the {current[0]} tab, it belongs on {url}.',
            )

        for label, pattern in (
            ("canonical", r'<link rel="canonical" href="([^"]+)"'),
            ("og:url", r'<meta property="og:url" content="([^"]+)"'),
        ):
            found = re.search(pattern, text)
            if not found:
                report.fail(
                    where,
                    f"falta a etiqueta {label}, que devia apontar para {expected}.",
                    f"the {label} tag is missing, it should point at {expected}.",
                )
            elif found.group(1) != expected:
                report.fail(
                    where,
                    f"{label} aponta para {found.group(1)}, devia apontar para {expected}. "
                    "Isto acontece quando se copia outra página e não se muda a etiqueta.",
                    f"{label} points at {found.group(1)}, it should point at {expected}. "
                    "This happens when a page is copied from another one and the tag is not changed.",
                )

        if not re.search(r'<meta name="description" content="[^"]+"', text):
            report.fail(where, "falta a meta description.", "the meta description is missing.")


# ---------------------------------------------------------------- check 5


def check_links(report):
    """Every internal link and asset reference must resolve to a file that exists,
    using the same extensionless rule Cloudflare uses. A typo here deploys a dead
    link with no warning."""
    for name, text in pages():
        where = f"public/{name}"
        for target in re.findall(r'(?:href|src)="(/[^"#?]*)"', text):
            clean = target.rstrip("/") or "/"
            if clean == "/":
                resolved = PUBLIC / "index.html"
            elif "." in Path(clean).name:
                resolved = PUBLIC / clean.lstrip("/")
            else:
                resolved = PUBLIC / (clean.lstrip("/") + ".html")
            if not resolved.exists():
                report.fail(
                    where,
                    f"a ligação {target} não corresponde a nenhum ficheiro "
                    f"(procurei {rel(resolved)}).",
                    f"the link {target} does not match any file "
                    f"(looked for {rel(resolved)}).",
                )

    # And the reverse: a page nobody links to is a page nobody finds.
    linked = set(tabs_hrefs(next(t for n, t in pages() if n == "index.html")))
    for name, _ in pages():
        if name in NOT_INDEXABLE:
            continue
        if url_for(name) not in linked:
            report.fail(
                f"public/{name}",
                "esta página existe mas não está na navegação de nenhuma página. "
                "Acrescente o separador aos oito ficheiros HTML.",
                "this page exists but is in no page's navigation. "
                "Add the tab to all eight HTML files.",
            )


def tabs_hrefs(text):
    block = re.search(r'<nav class="tabs".*?</nav>', text, re.S)
    return re.findall(r'<a href="([^"]+)"', block.group(0)) if block else []


# ---------------------------------------------------------------- check 6


def check_sitemap(report):
    """Adding a page means adding it to sitemap.xml, which README.md lists as the
    last step of a multi step procedure, exactly where steps get dropped."""
    path = PUBLIC / "sitemap.xml"
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        report.fail("public/sitemap.xml", f"XML inválido: {exc}", f"invalid XML: {exc}")
        return

    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    listed = {loc.text.strip() for loc in tree.getroot().iterfind(".//s:loc", ns)}
    expected = {SITE + url_for(n) for n, _ in pages() if n not in NOT_INDEXABLE}
    navigated = {SITE + h for h in tabs_hrefs(next(t for n, t in pages() if n == "index.html"))}

    for missing in sorted(expected - listed):
        report.fail(
            "public/sitemap.xml",
            f"{missing} é uma página do site mas não está no sitemap.",
            f"{missing} is a page on the site but is not in the sitemap.",
        )
    for extra in sorted(listed - expected):
        report.fail(
            "public/sitemap.xml",
            f"{extra} está no sitemap mas não corresponde a nenhuma página.",
            f"{extra} is in the sitemap but matches no page.",
        )
    for missing in sorted(expected - navigated):
        report.fail(
            "public/index.html",
            f"{missing} é uma página do site mas não aparece na navegação.",
            f"{missing} is a page on the site but does not appear in the navigation.",
        )

    # lastmod is the one element Google actually reads out of a sitemap, and a
    # malformed date makes it ignore the whole entry rather than complain.
    for url in tree.getroot().iterfind(".//s:url", ns):
        loc = url.find("s:loc", ns)
        lastmod = url.find("s:lastmod", ns)
        label = loc.text.strip() if loc is not None and loc.text else "?"
        if lastmod is None or not (lastmod.text or "").strip():
            report.fail(
                "public/sitemap.xml",
                f"{label} não tem <lastmod>.",
                f"{label} has no <lastmod>.",
            )
            continue
        value = lastmod.text.strip()
        try:
            datetime.date.fromisoformat(value[:10])
        except ValueError:
            report.fail(
                "public/sitemap.xml",
                f"<lastmod> de {label} é \"{value}\", que não é uma data. Use AAAA-MM-DD.",
                f"the <lastmod> for {label} is \"{value}\", which is not a date. Use YYYY-MM-DD.",
            )


# ---------------------------------------------------------------- check 7


def font_faces(css):
    """Every @font-face block in site.css, as (src path, unicode-range text)."""
    out = []
    for block in re.findall(r"@font-face\s*\{(.*?)\}", css, re.S):
        src = re.search(r"url\(\s*['\"]?([^'\")]+)", block)
        rng = re.search(r"unicode-range:\s*([^;]+);", block)
        out.append((src.group(1) if src else None, rng.group(1) if rng else None))
    return out


def parse_unicode_range(text):
    """A CSS unicode-range value as a set of code points."""
    points = set()
    for part in text.split(","):
        part = part.strip().upper().removeprefix("U+")
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            points.update(range(int(lo, 16), int(hi, 16) + 1))
        elif "?" in part:
            points.update(range(int(part.replace("?", "0"), 16), int(part.replace("?", "F"), 16) + 1))
        else:
            points.add(int(part, 16))
    return points


def check_fonts(report):
    """The fonts are self hosted and subsetted to latin, which is enough for
    Portuguese but is a real constraint, not an implementation detail: a character
    outside the subset falls back to a system font mid word. And a woff2 path with
    a typo does not error, it silently renders the whole site in Helvetica, which
    is the kind of regression that looks like a design change."""
    css_path = PUBLIC / "assets" / "site.css"
    css = css_path.read_text(encoding="utf-8")
    faces = font_faces(css)

    if not faces:
        report.fail(
            "public/assets/site.css",
            "não há nenhum bloco @font-face. As fontes são alojadas aqui, não no Google.",
            "there is no @font-face block. The fonts are hosted here, not by Google.",
        )
        return

    # Any url('/...') in the stylesheet, font or otherwise.
    for ref in sorted(set(re.findall(r"url\(\s*['\"]?(/[^'\")]+)", css))):
        if not (PUBLIC / ref.lstrip("/")).exists():
            report.fail(
                "public/assets/site.css",
                f"o CSS pede {ref}, que não existe. Um caminho errado não dá erro, "
                "o site passa a usar a fonte do sistema.",
                f"the CSS asks for {ref}, which does not exist. A wrong path raises no "
                "error, the site just falls back to a system font.",
            )

    if not (PUBLIC / "assets" / "fonts" / "OFL-Inter.txt").exists() or not (
        PUBLIC / "assets" / "fonts" / "OFL-Poppins.txt"
    ).exists():
        report.fail(
            "public/assets/fonts",
            "falta um dos ficheiros de licença OFL. Redistribuir estas fontes obriga a "
            "incluir o texto da licença.",
            "one of the OFL licence files is missing. Redistributing these fonts requires "
            "the licence text to travel with them.",
        )

    ranges = [r for _, r in faces if r]
    if len(ranges) != len(faces):
        report.fail(
            "public/assets/site.css",
            "há um @font-face sem unicode-range. Sem ele o browser descarrega a fonte "
            "mesmo para páginas que não precisam dela.",
            "there is an @font-face with no unicode-range. Without it the browser "
            "downloads the font even for pages that do not need it.",
        )

    covered = set()
    for rng in ranges:
        covered |= parse_unicode_range(rng)

    for name, text in pages():
        outside = {ch for ch in text if ord(ch) not in covered}
        if outside:
            listing = ", ".join(f"{ch} (U+{ord(ch):04X})" for ch in sorted(outside))
            report.fail(
                f"public/{name}",
                f"estes caracteres estão fora do subconjunto latino das fontes: {listing}. "
                "Ou reescreva o texto, ou volte a buscar as fontes com um subconjunto maior "
                "(ver public/assets/fonts/README.md).",
                f"these characters fall outside the fonts' latin subset: {listing}. "
                "Either reword the text, or refetch the fonts with a wider subset "
                "(see public/assets/fonts/README.md).",
            )


# ---------------------------------------------------------------- check 8


def check_no_third_party(report):
    """Loading a font, script or image from another host tells that host the
    visitor's IP address before the visitor has done anything. site.js argues that
    no consent banner is needed because the analytics are cookieless; that argument
    only holds while nothing else phones out. A text link a visitor may choose to
    click is fine and is not counted here.

    This reads the repository, not the running page: the beacon script itself then
    posts to cloudflareinsights.com, which no source scan can see. That is the
    reason to keep ALLOWED_ORIGINS short rather than to trust it as complete."""
    sources = [(f"public/{n}", t) for n, t in pages()]

    for where, text in sources:
        for tag in re.findall(r"<(?:" + LOADING_TAGS + r")\b[^>]*>", text, re.I):
            for ref in re.findall(r'(?:href|src)="([^"]+)"', tag):
                host = re.match(r'(?:https?:)?//([^/]+)', ref)
                if host and host.group(1) not in ALLOWED_ORIGINS:
                    report.fail(
                        where,
                        f"esta página carrega algo de {host.group(1)}. Ponha o ficheiro em "
                        "public/ e sirva-o daqui, ou acrescente o host a ALLOWED_ORIGINS "
                        "em scripts/checks.py, deliberadamente.",
                        f"this page loads something from {host.group(1)}. Put the file in "
                        "public/ and serve it from here, or add the host to ALLOWED_ORIGINS "
                        "in scripts/checks.py, deliberately.",
                    )

    js = (PUBLIC / "assets" / "site.js").read_text(encoding="utf-8")
    loads = re.findall(r"""(?:\.src|\.href)\s*=\s*['"]([^'"]+)|(?:fetch|import)\(\s*['"]([^'"]+)""", js)
    for a, b in loads:
        ref = a or b
        host = re.match(r'(?:https?:)?//([^/]+)', ref)
        if host and host.group(1) not in ALLOWED_ORIGINS:
            report.fail(
                "public/assets/site.js",
                f"o JavaScript carrega algo de {host.group(1)}, que não está em "
                "ALLOWED_ORIGINS em scripts/checks.py.",
                f"the JavaScript loads something from {host.group(1)}, which is not in "
                "ALLOWED_ORIGINS in scripts/checks.py.",
            )


def image_size(path):
    """Width and height straight out of the file header, so there is no image
    library to install. Returns None for a format not handled here."""
    data = path.read_bytes()

    if data[:8] == b"\x89PNG\r\n\x1a\n":
        # IHDR is always the first chunk, and its width and height are the first
        # two big endian 32 bit values of its payload.
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")

    if data[:2] == b"\xff\xd8":
        # Walk the marker segments to the start of frame, which is the only place
        # a JPEG records its dimensions. SOF0 through SOF15, skipping the four
        # that are not frame headers.
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            length = int.from_bytes(data[i + 2:i + 4], "big")
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                return (int.from_bytes(data[i + 7:i + 9], "big"),
                        int.from_bytes(data[i + 5:i + 7], "big"))
            i += 2 + length
    return None


def check_images(report):
    """Three things a browser cannot tell you are wrong, because the page looks
    right either way: an image far larger than the box it is drawn in, a portrait
    too small to survive a 2x screen, and an img with no width and height, which
    makes the page jump as it loads."""
    for path in sorted(PUBLIC.rglob("*")):
        if path.suffix.lower() not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
            continue
        size = path.stat().st_size
        if size > IMAGE_BUDGET:
            rel = path.relative_to(ROOT)
            report.fail(
                str(rel),
                f"esta imagem tem {size // 1024} KB, acima do limite de "
                f"{IMAGE_BUDGET // 1024} KB. Reduza-a ao tamanho a que é mostrada.",
                f"this image is {size // 1024} KB, over the {IMAGE_BUDGET // 1024} KB "
                "budget. Resize it to the size it is actually displayed at.",
            )

    for name, text in pages():
        where = f"public/{name}"
        for tag in re.findall(r"<img\b[^>]*>", text, re.I):
            src = re.search(r'src="([^"]+)"', tag)
            has_w = re.search(r'\bwidth="', tag)
            has_h = re.search(r'\bheight="', tag)
            label = src.group(1) if src else tag[:60]

            if not (has_w and has_h):
                report.fail(
                    where,
                    f"o <img> de {label} não tem width e height, por isso a página "
                    "salta enquanto carrega. Ponha as dimensões a que é mostrado.",
                    f"the <img> for {label} has no width and height, so the page jumps "
                    "as it loads. Add the dimensions it is displayed at.",
                )

            if not src or 'class="portrait"' not in tag:
                continue

            target = PUBLIC / src.group(1).lstrip("/")
            if not target.is_file():
                continue  # check_links already reports a missing file
            size = image_size(target)
            if size is None:
                continue
            short = min(size)
            if short < PORTRAIT_MIN:
                report.fail(
                    where,
                    f"{label} tem {size[0]}x{size[1]}, e o lado curto ({short} px) é "
                    f"menor que {PORTRAIT_MIN} px, por isso fica desfocado num ecrã 2x.",
                    f"{label} is {size[0]}x{size[1]}, and its short side ({short} px) is "
                    f"under {PORTRAIT_MIN} px, so it looks blurry on a 2x screen.",
                )
            elif short > PORTRAIT_MAX:
                report.fail(
                    where,
                    f"{label} tem {size[0]}x{size[1]}, e o lado curto ({short} px) passa "
                    f"{PORTRAIT_MAX} px. É mostrado num círculo de 108 px: reduza-o.",
                    f"{label} is {size[0]}x{size[1]}, and its short side ({short} px) is "
                    f"over {PORTRAIT_MAX} px. It is shown in a 108 px circle: resize it.",
                )


# ---------------------------------------------------------------- entry point


CHECKS = [
    ("línguas / languages", check_span_parity),
    ("travessões / dashes", check_dashes),
    ("blocos partilhados / shared blocks", check_shared_blocks),
    ("identidade da página / page identity", check_page_identity),
    ("ligações / links", check_links),
    ("sitemap", check_sitemap),
    ("fontes / fonts", check_fonts),
    ("nada de terceiros / no third parties", check_no_third_party),
    ("imagens / images", check_images),
]


def main():
    if not PUBLIC.is_dir():
        print(f"cannot find {PUBLIC}", file=sys.stderr)
        return 2

    report = Report()
    for label, fn in CHECKS:
        before = len(report.failures)
        fn(report)
        status = "ok" if len(report.failures) == before else "FALHA / FAIL"
        print(f"  {status:<14} {label}")

    report.render_terminal()
    report.render_summary()

    if report.failures:
        print(f"\n{len(report.failures)} problema(s) / problem(s).")
        return 1
    print("\nTudo certo. / All good.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
