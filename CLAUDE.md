# Working rules for this repo

## Never push to `main`

`main` is protected and every change is published by merging a pull request. Merging is
Luca's decision, always. Do not merge, do not use admin bypass, do not ask for the
protection to be lifted for a one off change.

The loop is:

1. `git checkout -b <topic>` off an up to date `main`.
2. Make the change, then run `scripts/check` and fix anything it reports.
3. Commit the change.
4. `git push -u origin <topic>`.
5. `gh pr create` with a description of what changed and why.
6. Report the PR URL and stop. Luca reviews and merges.

Pushing to `main` deploys to <https://caroco.pt> immediately, which is exactly why it is
closed off.

## Picking up a change request from an association member

Members open an issue built from the form in `.github/ISSUE_TEMPLATE/pedido.yml`, which
carries the `pedido` label. See [CONTRIBUTING.md](CONTRIBUTING.md) for the flow they
follow. A request that arrives by email is filed here as an issue by Luca, so an issue is
always the record.

To act on one:

1. `gh issue view <number>` to read it, and ask Luca about anything ambiguous rather than
   guessing at content about the association or about a named person.
2. `git checkout -b <topic>` off an up to date `main`.
3. Implement the change in `public/`, then run `scripts/check`.
4. `gh pr create` with `Closes #<number>` in the description, so merging the pull request
   closes the request.
5. Comment on the issue summarising what was implemented and anything left open, and
   paste the preview link so the member can see the change before it is published.
6. Stop. Luca approves and merges.

Every pull request gets a preview of the whole site at

```
https://<branch-name>-old-waterfall-5b2c.anateresavicente.workers.dev
```

Cloudflare Workers Builds creates it, and the same link is in the build check summary on
the pull request page. A member will not find it there, which is why step 5 pastes it into
the issue. The preview serves the real pages and resolves extensionless URLs, so `/missao`
works on it.

That link needs no login. Anybody who has it sees the page.

If the issue gives a publication date, repeat it at the top of the pull request
description, and say in the issue comment that the preview link is public, so the member
knows not to pass it on before the date. Merging publishes the change, so a pull request
that must not go live yet waits, and Luca decides when it merges.

Never edit a member's request text to match what was built. That means the issue body
stays as they wrote it. If the implementation had to deviate, say so in the comment.

## Content invariants

These are load bearing, see [README.md](README.md) for the reasoning:

- Both languages in the DOM, always edited together. `<span class="pt">` and
  `<span class="en">` counts stay in step.
- No em-dashes or en-dashes anywhere, in the site or in commit messages.
- The legal footer stays on every page.
- The nav is static markup duplicated across all eight HTML files, not injected by
  JavaScript.
- Do not rename the Worker in `wrangler.jsonc`.
- Never touch the MX, SPF, DKIM, DMARC, `autoconfig`, or `autodiscover` DNS records.
- No credentials in this repository. It is public.

`scripts/check` enforces the first four of these mechanically, plus the canonical and
`og:url` tags, internal links, and the sitemap. It runs on every pull request. Run it
locally before pushing rather than discovering a failure afterwards.

Six shared blocks have reference copies in `.github/blocks/` and must appear verbatim in
every page they belong to: the head asset lines, the social and structured data block
(seven indexable pages only, `404.html` is `noindex`), the skip link, the language toggle,
the tabs nav, and the legal footer. Changing one of them means changing the reference and
all eight files together, which is the point: an eight file edit that lands on seven files
is otherwise silent.

`pedidos/` holds the requests that arrived before the issue form existed, one file per
request. Nothing new is filed there. It is excluded from the dash check on purpose: a
member's request file may contain anything and must never be edited.

## Verifying

After a deploy, Cloudflare's edge can serve a stale asset or a 404 for a newly added file
for a short window. Retry with a cache buster (`curl -s "https://caroco.pt/x?v=$RANDOM"`)
before treating it as a real failure. It has never yet been one.
