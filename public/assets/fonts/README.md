# Fonts

Self hosted so that no visitor's IP reaches a Google server on a page load. `site.js`
argues that no consent banner is needed because the analytics are cookieless; loading the
fonts from `fonts.googleapis.com` contradicted that, since the font request carries the IP
and the referring URL to a third party before the visitor has done anything.

These are the exact files Google's own CSS serves for the `latin` subset, downloaded once
and committed. Not re subsetted, not re compressed.

| file | family | axis or weight | source |
|---|---|---|---|
| `inter-latin.woff2` | Inter | variable, wght 100 to 900 | `fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7W0Q5nw.woff2` |
| `inter-latin-italic.woff2` | Inter | static italic 400 | `fonts.gstatic.com/s/inter/v20/UcCM3FwrK3iLTcvneQg7Ca725JhhKnNqk4j1ebLhAm8SrXTc2dtRipWFsevceSGM.woff2` |
| `poppins-500-latin.woff2` | Poppins | static 500 | `fonts.gstatic.com/s/poppins/v24/pxiByp8kv8JHgFVrLGT9Z1xlFd2JQEk.woff2` |

Inter v20, Poppins v24, fetched 2026-08-04. Both are licensed under the SIL Open Font
License 1.1, so redistributing them here is fine; the two upstream `OFL-*.txt` files are
kept alongside verbatim.

Inter arrives as a single variable font covering the whole weight axis, which is why one
file serves 400, 500 and 600. That is also what Google was already sending, so nothing got
heavier: the site simply gained a real 600 for the 26 `<strong>` elements that the browser
used to fake by smearing 400.

## The latin subset is a constraint

These files cover `U+0000-00FF` plus a handful of punctuation ranges. That is every
character the site uses today and every character Portuguese needs. A character outside it,
say a contributor's name with `ł` or `ș`, would silently render in Helvetica for that one
glyph.

`scripts/check` guards this, so adding such a character fails the check rather than
degrading quietly. If the content genuinely needs one, refetch with `latin-ext` added and
extend the `unicode-range` in `site.css` and the allowed set in `scripts/checks.py`
together.

## Refetching

Ask Google's CSS endpoint with a browser user agent, which is what makes it return `woff2`
rather than `ttf`, then take the URLs under the `/* latin */` comments:

```sh
curl -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" \
  "https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,500;0,600;1,400&family=Poppins:wght@500&display=swap"
```
