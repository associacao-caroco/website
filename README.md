# caroco.pt

Official website of **Associação Caroço**, a non-profit cultural association based in
Lavacolhos, Fundão, Portugal.

Live at <https://caroco.pt>.

Static HTML and CSS. No build step, no dependencies, no framework.

## Formatting rule

Never use em-dashes or en-dashes anywhere, in the site content or in commit messages.
Use commas, colons, parentheses, or middle dots instead.

## Structure

```
wrangler.jsonc          Cloudflare config: serves public/ as static assets
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
  assets/
    caroco-mark.png     logo
    oliveiras.jpg       photo, olive trees regrowing after fire
    gardunha.jpg        photo, geodesic marker on the Gardunha
    site.css            all styling
    site.js             PT/EN language toggle
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

Pushing to `main` triggers a rebuild and deploy through the Cloudflare git integration
(Workers and Pages, `old-waterfall-5b2c`, Settings, Builds).

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
