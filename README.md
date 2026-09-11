# wedding

A one-page wedding invitation site. One file, no build step, no dependencies.

`index.html` is the whole site. Open it in a browser to see it; edit it in any
text editor to change it.

---

## Filling in the blanks

Every detail that belongs to you is wrapped in `<span class="slot">`, and shows
on the page as gold text with a dashed underline. Search the file for `class="slot"`
to find them all.

Replace the text inside each one. When you're done you can drop the
`class="slot"` attribute so the dashed underline goes away, or leave it — the
styling only exists to make the blanks findable.

The blanks, in order of appearance:

| Where | What goes there |
| --- | --- |
| Header plate | Both first names, the date, the venue and town, the dress code |
| Order of the day | The six times |
| Travel and rooms | Venue address, maps link, parking, trains, hotels |
| RSVP | The reply-by date, and your email address |
| FAQ | Answers to all five questions |
| Footer | Monogram initials, email, date, venue |

Two places hold the email address and need to match: the `.slot` in the RSVP
note, and the `TO` variable near the bottom of the `<script>` block.

```js
var TO = "your@email";
```

## How RSVPs work right now

There is no backend. When a guest submits the form, the page composes a
plain-text reply, shows it to them, and hands it to their own email app via a
`mailto:` link. Nothing can be silently lost, but replies arrive as individual
emails rather than as a list.

To collect them properly, pick one:

- **Google Form** — free. Delete the `<form>` and link the RSVP button at your
  form instead. Answers land in a spreadsheet.
- **Netlify Forms** — free tier, ~100 submissions a month, only if you host on
  Netlify. Add `netlify` and `name="rsvp"` to the `<form>` tag and remove the
  submit handler.
- **Formspree** — works on any host, free tier ~50 a month. Set the form's
  `action` to your Formspree endpoint and `method="POST"`.

## Publishing it

The site is static, so anything that serves files will do.

- **Netlify / Vercel / Cloudflare Pages** — drag the folder onto their dashboard.
  Free, custom domain supported, done in a minute.
- **GitHub Pages** — Settings → Pages → deploy from `main`, root folder.
  Note that Pages sites are public even when the repository is private.

## What it depends on

Three typefaces from Google Fonts: Bodoni Moda (headings), Jost (body), and
Pinyon Script (the *and* between the names, and the footer monogram). They load
over the network; if they fail, the page falls back to system serif and sans and
still reads correctly.

Nothing else. No framework, no package manager, no build.
