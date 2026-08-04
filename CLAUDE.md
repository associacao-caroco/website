# Working rules for this repo

## Never push to `main`

`main` is protected and every change is published by merging a pull request. Merging is
Luca's decision, always. Do not merge, do not use admin bypass, do not ask for the
protection to be lifted for a one off change.

The loop is:

1. `git checkout -b <topic>` off an up to date `main`.
2. Commit the change.
3. `git push -u origin <topic>`.
4. `gh pr create` with a description of what changed and why.
5. Report the PR URL and stop. Luca reviews and merges.

Pushing to `main` deploys to <https://caroco.pt> immediately, which is exactly why it is
closed off.

## Picking up a change request from an association member

Members open a pull request containing only a text file under `pedidos/`, describing what
they want changed. See [CONTRIBUTING.md](CONTRIBUTING.md) for the flow they follow.

To act on one:

1. `gh pr checkout <number>` to get onto their branch. Most requests arrive from a fork,
   so pushing back to it needs "Allow edits by maintainers" left on. If it is off, the
   push is rejected: in that case open a second PR that closes theirs, and say why.
2. Read their file in `pedidos/`, and ask Luca about anything ambiguous rather than
   guessing at content about the association or about a named person.
3. Implement the change in `public/`, committing to that same branch, and push. The
   request file stays in the branch as the record of what was asked.
4. Comment on the pull request summarising what was implemented and anything left open.
5. Stop. Luca approves and merges.

Never edit a member's request text to match what was built. If the implementation had to
deviate, say so in the pull request comment.

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

## Verifying

After a deploy, Cloudflare's edge can serve a stale asset or a 404 for a newly added file
for a short window. Retry with a cache buster (`curl -s "https://caroco.pt/x?v=$RANDOM"`)
before treating it as a real failure. It has never yet been one.
