# Skie Design Studio: site build brief for Cursor

These four HTML files are design previews made in Claude. Each opens in a browser as is.
Use them as the visual and content reference for the real site pages.

| File | Becomes | Notes |
|---|---|---|
| studio-home.html | `/` (studio home, with a card for each of the four products) | Has two views: `#home` (the page) and `#plan` (site plan, reference only, don't build it) |
| cheklists.html | `/cheklists` | Has two views: `#checklists` (the page) and `#studio` (an older studio sketch, ignore it) |
| reveal.html | `/reveal` | One page |
| marginalia.html | `/marginalia` | One page |
| (today's homepage, in your current code) | `/skie-finance` | Skie Finance's product page. Move the current skiedesignstudio.com page here as is; change its footer to "© 2026 Skie Design Studio" and add an "All products" link |

## Strip before building
- The yellow review bar at the top, the "Hide notes" button, and every yellow note (`.note`, `.ph`, `.q`, `.qbox`). They mark open questions, not content.
- The tab switcher script (hash views). Each page should be its own route.
- Links to claude.ai artifacts. "About ..." links on the studio home go to `/skie-finance`, `/cheklists`, `/reveal`, `/marginalia`.

## Shared design (keep consistent across every page)
- Fonts (Google Fonts): Fraunces for headings (one italic accent word per heading), Inter for body, JetBrains Mono for small uppercase labels.
- Light ground `#eef3f3`, alt band `#dde6e7`, ink `#13262a`, dark band `#0f2a2c`. Each file has a full dark-mode token set in `:root`.
- One accent per product: Skie Finance teal `#145f63`, ChekLists violet `#6a1fd1`, Reveal dusk blue `#2c4f7c`, Marginalia red pencil `#8a3a32`.
- Product page pattern: header with section links, hero (status line, H1, lede, two buttons, visual), numbered sections, one dark band, closing call to action, footer "© 2026 Skie Design Studio" with "← All products".
- The three product files differ slightly in CSS (spacing, label style). Pull the shared parts into one stylesheet and set the accent per page with a `--accent` variable.

## Suggested first prompt in Cursor
> Read site-designs/CURSOR-BRIEF.md and the four HTML files in site-designs/. Create the site pages listed in the table, using one shared stylesheet with per-page accent colours. Remove the review bar, yellow notes and tab-switching script. Keep the copy as written. Move the current homepage (Skie Finance) to /skie-finance and put the studio home at /.

## Still open (from SD)
iOS/Android plans per app, real screenshots, ChekLists and Marginalia privacy wording. The studio home's tagline, About text and contact email are final.
