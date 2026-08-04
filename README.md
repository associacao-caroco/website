# caroco.pt

Official website of **Associação Caroço**, a non-profit cultural association based in
Lavacolhos, Fundão, Portugal.

Live at <https://caroco.pt>.

Static HTML and CSS. No build step, no dependencies, no framework.

## Changes go through pull requests

`main` is protected. Nobody pushes to it, including maintainers: every change lands by
merging a pull request, and merging is what publishes the site. See
[CONTRIBUTING.md](CONTRIBUTING.md) for how members request a change without touching any
code, and [CLAUDE.md](CLAUDE.md) for the rules a Claude Code session follows here.

## Checks

```sh
scripts/check
```

Standard library Python, no dependencies, about a second. The same script runs on every
pull request, and when something fails the explanation appears on the pull request page in
Portuguese and in English.

It exists because merging is what publishes the site, there is no staging step, and the
mistakes worth catching are the ones that look fine in the browser: a paragraph added in
Portuguese but not English is hidden by the language toggle from everyone except an English
visitor; a page created by copying another one can keep the source page's canonical tag and
quietly tell Google it is a duplicate; an edit meant for all eight files that lands on
seven leaves one page stale with no symptom.

The four blocks that are duplicated across every page (the head asset lines, the language
toggle, the tabs nav, the legal footer) have reference copies in `.github/blocks/`. The
check asserts each one appears verbatim wherever it belongs, so drift is loud instead of
silent. Changing a shared block means changing the reference and all eight files together.

## Formatting rule

Never use em-dashes or en-dashes anywhere, in the site content or in commit messages.
Use commas, colons, parentheses, or middle dots instead.

## Structure

```
wrangler.jsonc          Cloudflare config: serves public/ as static assets
CONTRIBUTING.md         how members request changes, in PT and EN
CLAUDE.md               working rules for Claude Code sessions in this repo
pedidos/                change requests from members, one file per request
scripts/
  check                 run this before opening a pull request
  checks.py             the checks themselves, standard library only
.github/
  pull_request_template.md
  workflows/checks.yml  runs scripts/check on every pull request
  blocks/               reference copies of the five shared markup blocks
public/
  index.html            /                  Inicio / Home
  missao.html           /missao            Missao / Mission
  o-que-fazemos.html    /o-que-fazemos     O que fazemos / What we do
  o-lugar.html          /o-lugar           O lugar / The place
  orgaos-sociais.html   /orgaos-sociais    Orgaos sociais / Governance
  noticias.html         /noticias          Noticias / News
  contactos.html        /contactos         Contactos / Contact
  404.html
  robots.txt
  sitemap.xml
  favicon.ico           16, 32 and 48 px, requested unconditionally by crawlers
  assets/
    caroco-mark.png     logo
    apple-touch-icon.png  180x180, opaque: iOS composites transparency to black
    icon-192.png        192x192, for Android home screens
    og-caroco.jpg       1200x630 card shown when a link is shared
    oliveiras.jpg       photo, olive trees regrowing after fire
    gardunha.jpg        photo, geodesic marker on the Gardunha
    team-*.jpg          portraits for the team section on /orgaos-sociais
    site.css            all styling
    site.js             PT/EN language toggle
    fonts/              Inter and Poppins, self hosted, see fonts/README.md
```

Cloudflare resolves `/missao` to `missao.html` automatically, so URLs stay extensionless.
Unknown paths serve `404.html`.

## Editing

**Content.** Every page keeps both languages in the DOM. A block looks like:

```html
<span class="pt">Texto em portugues</span>
<span class="en">Text in English</span>
```

`site.js` sets `data-lang` on `<html>` and `site.css` hides the other language. Always
edit both languages together, or one of them silently goes stale.

**Navigation.** The `<nav class="tabs">` block is duplicated in all eight HTML files by
design, so the links exist in the served HTML rather than being injected by JavaScript.
Changing the nav means editing all eight files. Only the `aria-current="page"` attribute
differs between them: it sits on the tab matching the current page.

**Team portraits.** `/orgaos-sociais` lists the governing bodies and then a profile
per member. Portraits are square JPEGs, roughly 500 to 760 px, displayed at 108 px in a
circle and rendered grayscale by CSS, so colour originals are fine. Keep them square, or
the circle crops unevenly. Alexandra Belo and Vitor Mingacho share one entry, as in the
source material.

**Fonts.** Inter and Poppins are served from `public/assets/fonts/`, not from
`fonts.googleapis.com`. Two reasons. Requesting a stylesheet from Google sends every
visitor's IP address to Google before the visitor has done anything, which is the transfer
a Munich court found unlawful without consent in 2022, and it contradicted the note in
`site.js` arguing that no consent banner is needed because the analytics are cookieless.
And the Google stylesheet only declared Inter 400 and 500, so all 26 `<strong>` elements
on the site were faux bolded by the browser rather than rendered in a real 600.

The files are the latin subset only, which covers Portuguese but is a constraint rather
than an implementation detail: a character outside it falls back to a system font mid word.
`scripts/check` enforces that. `public/assets/fonts/README.md` records the exact upstream
URLs, the versions, and how to refetch them.

**Legal footer.** Every page carries the association's legal details (name, NIPC, CAE,
registered office, contact email). Google for Nonprofits requires the organisation
details to be visible on the official website, and putting them on every page removes
any doubt about which page a reviewer lands on. Do not remove this footer.

**New page.** Copy `contactos.html`, change the `<title>`, meta description, canonical,
`og:` tags, and the body content. Then add the tab to the nav in every file and add the
URL to `sitemap.xml`.

## Local preview

Any static file server works, for example:

```sh
cd public && python3 -m http.server 8000
```

Note that `python3 -m http.server` does not do extensionless routing, so browse to
`/missao.html` locally. On Cloudflare, `/missao` is the real URL.

Closer to production, if Node is available:

```sh
npx wrangler dev
```

## Deployment

Cloudflare Workers static assets, Worker `old-waterfall-5b2c`, in Ana Teresa's Cloudflare
account. The custom domain caroco.pt is attached to that Worker.

A commit landing on `main` triggers a rebuild and deploy through the Cloudflare git
integration (Workers and Pages, `old-waterfall-5b2c`, Settings, Builds). Since `main` is
protected, in practice that means merging a pull request is what deploys.

Manual deploy, if ever needed:

```sh
npx wrangler deploy
```

**Do not rename the Worker in `wrangler.jsonc`.** `old-waterfall-5b2c` is the Worker that
owns the caroco.pt custom domain. A different name creates a second Worker and the live
site keeps serving the old one.

Cloudflare and browsers cache aggressively. Verify with a hard refresh (Cmd+Shift+R) or
an incognito window.

## DNS and email: do not touch

Email for @caroco.pt runs on **Hostinger**, not Google. The MX, SPF, DKIM, DMARC,
`autoconfig` and `autodiscover` records live in Cloudflare DNS and point to Hostinger.

Deploying this site never requires changing any of them. If you do any work in the
Cloudflare DNS panel, screenshot the record table first, and check afterwards that

```sh
dig +short MX caroco.pt
dig +short TXT caroco.pt
```

produce identical output to before.

## Rollback

The previous single-file version of the site (612 KB, all assets inlined as base64) is
kept outside this repo at `Caroço/website/code/index.html` and is byte-identical to what
was live before this repo existed. To roll back, upload it as a new deployment on the
`old-waterfall-5b2c` Worker.

## Context

This multi-page structure exists because Google for Nonprofits declined to activate
Google Workspace for Nonprofits on caroco.pt while the site was a single page. The
reviewer asked for distinct tabs linking to separate pages, each populated with relevant
information, and for the registered organisation details to be displayed. Keep those
properties intact when editing.
