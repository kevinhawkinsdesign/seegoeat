# SeeGoEat

Personal travel recommendations by Kevin Hawkins — restaurants, bars, places to stay, and things to see across cities worldwide.

## seegoeat.com

Places are organised by city, then filtered by:

- **My Favorites** — personally reviewed and recommended
- **Food** — restaurants, cafés, fast food, coffee
- **Drinks** — bars, cocktail bars, speakeasies, nightlife
- **Places to Stay** — hotels and accommodation
- **Places to See** — landmarks, parks, museums, beaches, attractions

All map links open directly in Google Maps.

## Data source

The site loads all cities and places from the `seegoeat-app` Supabase project at page load — there is no hardcoded place data in `index.html`. This keeps the website and mobile app in sync automatically: add a place once (via a Supabase migration in `seegoeat-app`), and it shows up on both.

**One-time setup:** open `index.html` and set `SUPA_KEY` to the Supabase project's `anon` public key (Supabase dashboard → Settings → API). It's safe to commit — the anon key only grants what row-level security policies allow, and `cities`/`places` are public-read.

Search (the "✦ Ask AI" box) uses semantic search via a Supabase edge function (`search-places`) — see the `seegoeat-app` README for how that's set up. No API keys live in this repo's JavaScript.
