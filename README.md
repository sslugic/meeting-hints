<p align="center"><img src="docs/assets/icon-256.png" width="96" alt="Undertone"></p>

# Undertone

**Your company's jargon, explained while it's being said.**

Undertone is a macOS app that listens along to your calls. When a code name, acronym or internal project comes up, it explains it from your team's own Slack, Notion, Jira and other tools, in a small panel beside the call. Before a meeting it briefs you; afterwards you get the recap, your tasks, a follow-up draft and new terms to learn.

**Website and download:** https://getundertone.app

- Free during the beta, with your own AI: an OpenAI, Anthropic or Gemini key, a local Ollama or LM Studio model, or your Claude Code or Cursor sign-in.
- macOS 26 or later on Apple silicon. Signed and notarized by Apple.

## What this repository is for

The Undertone app is closed source. This public repository holds:

- **[Releases](https://github.com/sslugic/undertone/releases):** the notarized `.dmg` for every version, with release notes.
- **[Issues](https://github.com/sslugic/undertone/issues):** bug reports and feature requests.
- **[SECURITY.md](SECURITY.md):** what leaves your Mac, what doesn't, and how to check it yourself.
- **[DATA.md](DATA.md) and [schemas/](schemas):** every file Undertone stores on your Mac and its format.
- **[docs/](docs):** the website.

## Website translations

The site is available in 17 languages. `docs/index.html` is the English source; `docs/<code>/index.html` pages are generated. After editing the English page, run:

```sh
python3 tools/i18n.py          # refresh docs/i18n/en.json and rebuild every language page
python3 tools/i18n.py check    # list missing or invalid translations
```

New or changed strings fall back to English until their keys are added to `docs/i18n/<code>.json`.

## Privacy in one paragraph

Calls and your microphone are transcribed on your Mac with Apple's speech recognition; audio is never uploaded. Text from the call goes only to the AI you choose, and Undertone only reads from the tools you connect (it never sends, posts or edits). There is no Undertone server, account or telemetry. Everything Undertone keeps is stored as files in `~/Library/Application Support/Undertone`, and keys stay in your Keychain. See [SECURITY.md](SECURITY.md) for how to verify this with a network monitor.

## Reporting a problem

Open an [issue](https://github.com/sslugic/undertone/issues) with your macOS version, Undertone version (Profile & Settings) and what happened. Please don't paste meeting transcripts or anything confidential. For security issues, see [SECURITY.md](SECURITY.md).
