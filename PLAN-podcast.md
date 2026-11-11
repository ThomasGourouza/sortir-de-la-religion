# Video podcast of the essay (French, max 1 h)

## Context
The user wants a video podcast (max 1 h, French, one narrator) of *Sortir de la religion sans en fonder une autre ?*, showing the essay's sections, titles and images, with the table of contents always visible (14 parts listed, current part expanded to its sections, current section highlighted). Before producing it, they want 5 French voice candidates to compare in a browser. `.env.local` holds `ELEVENLABS_API_KEY` (only key). Tools present: ffmpeg, python3 + Pillow.

1 h of speech is about 8,500 words versus 137,000 in the essay: the narration is a condensed rewrite (~6 %), not a reading.

## Step 0: housekeeping
- Copy this plan to `PLAN-podcast.md` at the repo root (memory rule).
- Add `.env.local` and `podcast/out/` to `.gitignore` (the key is currently untracked and unignored).

## Step 1: voice samples (deliverable first, then stop for the user's choice)
`podcast/voix.py` (stdlib only, `urllib`):
- Read the key from `.env.local`.
- `GET /v1/shared-voices?language=fr&use_cases=narrative_story` (+ `/v1/voices` for voices already in the account): pick 5 native French voices, mixed genders, suited to long narration (calm, warm, documentary).
- Same sample text for all (~600 chars, e.g. the opening of the prologue plus the Stirner quote, to test German/Latin names and quotes), model `eleven_multilingual_v2`, `POST /v1/text-to-speech/{voice_id}` → `podcast/out/voix/<name>.mp3`.
- Write `podcast/out/voix/index.html`: one card per voice (name, gender, accent, description, `<audio controls>`), served with `python3 -m http.server`, opened in Chrome.
- Cost: ~3,000 characters of quota.

## Step 2: script
`podcast/script.md`, same structure as the essay: `## Partie` / `### Section` headings copied verbatim from `texte/sortir-de-la-religion.md` so they map to the essay's ids, each followed by the narration. Budget: ~300 words intro, ~600 per part, ~700 conclusion, total ≤ 8,500 words. Sections not narrated are still listed in the TOC.
- Drafted per part by parallel agents with common rules (follow CLAUDE.md "Répondre en spécialiste" rules: the essay's terms, verdicts in first person as the author's, attested vs constructed debates, réserves respected, French quotes only, no em/en dash, written for the ear: short sentences, no parentheses or references).
- I review the whole for consistency and length; user can edit it before audio.

## Step 3: audio
`podcast/podcast.py audio`: one TTS call per narrated section with the chosen voice (cache: skip if the mp3 exists, so editing one section only re-synthesises that one), `previous_text`/`next_text` for continuity. Check `/v1/user/subscription` first: ~60,000 characters needed; abort with a message if the quota is short.

## Step 4: video
`podcast/podcast.py video` (Pillow + ffmpeg):
- Parse headings with `lire_article`, `structurer`, `slug` imported from `build/build.py` (main-guarded, safe to import); images from `build/images.json`: section `portrait`/`figure` first, else the part's `partimage` (`images/art/partie-*-grand.jpg`), cover for the intro.
- One 1920x1080 PNG per narrated section: left column TOC (14 parts, current part expanded with its sections, current section highlighted), right: part title, section title, image, caption. Serif system font (Georgia), sepia palette from `css/style.css`.
- ffmpeg: each PNG + its mp3 → clip (`-loop 1 -tune stillimage`), concat → `podcast/out/sortir-de-la-religion.mp4`, with chapter metadata; also `chapitres.txt` (timestamps for a YouTube description).
- Skipped: animations / Ken Burns. Add if static slides feel too flat.

## Verification
- Step 1: page opens, 5 players play.
- Step 3: total audio duration printed, must be ≤ 60 min.
- Step 4: `ffprobe` duration and chapters; extract 3 frames (intro, a middle part, conclusion) and look at them: TOC highlight moves, images and titles correct.
