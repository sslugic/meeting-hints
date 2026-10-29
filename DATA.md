# What Undertone stores

Everything Undertone keeps is in `~/Library/Application Support/Undertone`, as JSON or plain text you can open and read. Nothing is stored anywhere else, except keys and sign-in tokens, which are in your macOS Keychain (`co.slaven.meetinghints`). Audio is never stored.

Dates are ISO 8601 strings. IDs are UUIDs. Formats for the main files are in [schemas/](schemas) as JSON Schema.

| File | What it holds |
|---|---|
| `meetings/<id>.json` | One file per meeting: title, app, start and end, attendees, transcript lines (time, text, and `"You"` for your microphone), hints, context brought up for questions put to you, the recap, answer reviews and score, the in-call chat, and the follow-up draft. [Schema](schemas/meeting.schema.json) |
| `tasks.json` | Your tasks: title, why, deadline as it was said, priority, status, the meeting it came from, and its space. [Schema](schemas/task.schema.json) |
| `context-index.json` | Background context: a short brief with sources for each open task and recent meeting, and when it was gathered. [Schema](schemas/context-brief.schema.json) |
| `briefings.json` | Briefings written before upcoming meetings: event title, start, attendees, the briefing text and the short readiness quiz written from it. |
| `people.json` | What your tools say about people you meet: name, email and a short note with sources. Only for people you looked up. |
| `memory.json` | What Undertone learned from past meetings: confirmed terms and their meanings, recap points and action items, and how often each attendee came up. |
| `spaces.json` | Your spaces: name, description and colour. |
| `archive.json` | Your artifacts: documents, slide decks and canvases you made, as Markdown (and HTML for canvases). |
| `chat.json` | Your Ask conversation. |
| `corrections.json` | Words you corrected ("Data dog" → "Datadog"), used to fix later transcripts. |
| `profile.json` | Your name, role and the terms you marked as known. |
| `quiz.json` | Glossary practice: for each term, how often you answered and got it right, your current streak, when you last practised and what your last wrong answer left out. |
| `quiz-history.json` | Your last 200 practice and meeting prep rounds: when, which mode or meeting, and each answer (right or not, % match, what was missed). |
| `study-guide.json` | The last study guide Undertone wrote from that history, and the terms it focused on. |
| `org.json` | An org chart you imported or attached in Ask: names, titles, emails, teams, locations and managers, as in your HR export. Delete it to remove it. |
| `background.txt` | Background you added for answer mode, such as a résumé or notes. |
| `context-pack.json` | Terms and notes gathered for a call (a few minutes before it when it's on your calendar), for live hints. |
| `sources.json`, `mcp-servers.json` | The tools you connected: names, addresses, available tools and whether each is on. No tokens; those are in the Keychain. |
| `attachments/` | Text taken from files you added to Ask, and resized copies of images you added. |
| `events.log` | A plain-text log of what Undertone did and when (calls detected, hints, lookups, errors). |

Settings such as your AI provider and model names are kept in the app's preferences (`defaults read co.slaven.meetinghints`).

To delete everything, quit Undertone and remove the folder above.
