# Security and privacy

Undertone is closed source, so here is exactly what it does with your data and how to check it yourself.

## What stays on your Mac

- **Audio.** System audio (the call) and your microphone are transcribed on your Mac with Apple's SpeechAnalyzer. Audio is never written to disk and never uploaded. Audio or video files you attach in Ask are also transcribed on your Mac.
- **Everything Undertone keeps.** Meetings, transcripts, recaps, tasks, the glossary, people notes, briefings, artifacts and chat are JSON files in `~/Library/Application Support/Undertone`. [DATA.md](DATA.md) lists every file and its format.
- **Keys and sign-ins.** AI keys, connector tokens and the free-credits sign-in are stored in your macOS Keychain.
- **Calendar.** Read through macOS Calendar to show and brief upcoming meetings. Undertone never creates or changes events.

## What leaves your Mac, and where it goes

Undertone connects only to:

1. **The AI you chose**, to explain terms, draft answers, recaps, briefings and follow-ups. It sends text: parts of the transcript, the terms it found, your profile (name and role) and context gathered from your tools. Depending on your choice that's `api.openai.com`, `api.anthropic.com`, `generativelanguage.googleapis.com`, OpenRouter or another OpenAI-compatible endpoint you entered, or a model on your Mac (Ollama, LM Studio). With Claude Code or Cursor, the request goes through that app's own CLI and its connection. Images you attach in Ask are sent to that AI.

   **Free credits** are the one case that goes through a server of ours. If you start with free credits instead of your own AI, requests go to `ai.getundertone.app`, which passes them to Google Gemini and counts what each one costs. That server keeps your email, your credit balance, daily totals of requests and tokens, and the answers to the bonus form if you send it. It does not store what was sent or answered. Switch to your own AI in Settings › AI & Memory and nothing goes through it.
2. **The tools you connected** (Slack, Notion, Jira, Linear and others), through their MCP servers, to search for the meaning of a term or context for a task. Only read-only tools are allowed: anything that sends, posts, creates, edits or deletes is refused.
3. **Sign-in pages** for those tools, in your browser, when you connect one.
4. **Updates.** Every few hours Undertone reads `getundertone.app/appcast.xml` to see if there's a new version, and downloads it from GitHub when there is.
5. **The usage count, only if you leave it on.** "Count me as a user" sends a random ID, the app version, the macOS version and the interface language once at install and at most once a week to `stats.getundertone.app`. Turning it off deletes what was sent.
6. **Usage stats, only if you leave them on.** "Share anonymous usage stats" sends coarse events to PostHog (`us.i.posthog.com`): app opened, setup steps, permissions granted or denied, meeting started or ended (its length and the call app, like Zoom), the AI provider's name, how many hints were shown or opened, recap written, and errors (their kind, never their text). Each carries a random ID, the app version, the macOS version and the language. Never what was said, meeting titles, attendee names, glossary terms, keys or tokens. Switch it off in setup or Settings › About.

[amem](https://getamem.com/), if you install it, runs on your Mac.

## Check it yourself

1. Install a network monitor: [Little Snitch](https://www.obdev.at/products/littlesnitch/), [LuLu](https://objective-see.org/products/lulu.html) (free) or [Proxyman](https://proxyman.io/).
2. Start a call with Undertone listening, and expand a hint.
3. Watch Undertone's connections. You'll see only your AI provider and the MCP servers you connected; with a local model and no tools, you'll see none.
4. Compare the amount of data sent with a call's audio: hints send a few kilobytes of text, not megabytes of audio.

You can also open `~/Library/Application Support/Undertone/events.log` to see what Undertone did and when, and read the files listed in [DATA.md](DATA.md).

## Removing your data

Quit Undertone and delete `~/Library/Application Support/Undertone`. Keys are under `co.slaven.meetinghints` in Keychain Access.

## Reporting a vulnerability

Please don't open a public issue. Use GitHub's [private vulnerability reporting](https://github.com/sslugic/undertone/security/advisories/new) for this repository. You'll get a reply within a few days.
