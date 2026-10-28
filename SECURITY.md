# Security and privacy

Undertone is closed source, so here is exactly what it does with your data and how to check it yourself.

## What stays on your Mac

- **Audio.** System audio (the call) and your microphone are transcribed on your Mac with Apple's SpeechAnalyzer. Audio is never written to disk and never uploaded. Audio or video files you attach in Ask are also transcribed on your Mac.
- **Everything Undertone keeps.** Meetings, transcripts, recaps, tasks, the glossary, people notes, briefings, archive documents and chat are JSON files in `~/Library/Application Support/Undertone`. [DATA.md](DATA.md) lists every file and its format.
- **Keys and sign-ins.** AI keys and connector tokens are stored in your macOS Keychain.
- **Calendar.** Read through macOS Calendar to show and brief upcoming meetings. Undertone never creates or changes events.

## What leaves your Mac, and where it goes

Undertone has no server, no account, no analytics and no update check. It connects only to:

1. **The AI you chose**, to explain terms, draft answers, recaps, briefings and follow-ups. It sends text: parts of the transcript, the terms it found, your profile (name and role) and context gathered from your tools. Depending on your choice that's `api.openai.com`, `api.anthropic.com`, `generativelanguage.googleapis.com`, OpenRouter or another OpenAI-compatible endpoint you entered, or a model on your Mac (Ollama, LM Studio). With Claude Code or Cursor, the request goes through that app's own CLI and its connection. Images you attach in Ask are sent to that AI.
2. **The tools you connected** (Slack, Notion, Jira, Linear and others), through their MCP servers, to search for the meaning of a term or context for a task. Only read-only tools are allowed: anything that sends, posts, creates, edits or deletes is refused.
3. **Sign-in pages** for those tools, in your browser, when you connect one.

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
