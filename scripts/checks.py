#!/usr/bin/env python3
"""Structural checks for the caroco.pt static site.

Run it from anywhere: scripts/check

Every check here exists because the thing it guards fails SILENTLY. Merging a pull
request is what publishes caroco.pt, there is no staging step, so a mistake that
looks fine in the browser is a mistake that is live. See CLAUDE.md for the
invariants these encode.

Standard library only, by design. This repo has no dependencies and no build step.
"""

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
    "README.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    ".github/pull_request_template.md",
]

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


# ---------------------------------------------------------------- entry point


CHECKS = [
    ("línguas / languages", check_span_parity),
    ("travessões / dashes", check_dashes),
    ("blocos partilhados / shared blocks", check_shared_blocks),
    ("identidade da página / page identity", check_page_identity),
    ("ligações / links", check_links),
    ("sitemap", check_sitemap),
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
