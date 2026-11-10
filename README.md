<div align="center">

# L&D Command Center

[![CI](https://github.com/Hatemshalaby15071979/L-D-Command-Center/actions/workflows/pylint.yml/badge.svg)](https://github.com/Hatemshalaby15071979/L-D-Command-Center/actions)
![licence](https://img.shields.io/badge/licence-MIT-blue)
![python](https://img.shields.io/badge/python-3.10%2B-3776ab)
![status](https://img.shields.io/badge/status-1.0.0%20released-brightgreen)

**A study, language, and career workstation that runs on your own computer — not in the cloud.**

</div>

## What it is

L&D Command Center is a desktop app for learning languages, preparing for exams,
and working on your career. It runs entirely on your machine. There is no account
to sign up for, no monthly fee, and nothing leaves your computer unless *you*
connect a local AI model yourself.

If you are a student who wants to practice a language, drill for an exam, or build
a better resume, this is built for you — you do not need to be a programmer to use
it.

## What you can do

- **Language Lab** — 30 ready-made lesson packs for Spanish, Japanese, and German,
  with audio, flashcards, and grammar drills.
- **Conversation practice** — speak with persona tutors through your microphone and
  get accent feedback.
- **Level exams** — final tests from A1 to C1, with a recommendation on what to
  study next.
- **Career tools** — build a resume, pull in your GitHub or LinkedIn, search jobs,
  draft cover letters, and rehearse interviews.
- **Skills Arena** — turn your own documents into reading, writing, and listening
  practice.
- **Placement quiz** — a 12-question test that places you between A1 and B1.

## Before you start

You will need:

- **Windows** (the packaged app is built for Windows)
- **Python 3.10 or newer**
- **LM Studio** running locally at `http://localhost:1234/v1` with a model loaded
  (for example `google/gemma-4-12b-qat`)
- the `tkinter` and `httpx` packages

The AI features use a model you run yourself. Without a model loaded, the app
opens but the AI-assisted parts stay quiet.

## Get it and run it

1. Download the latest Windows build from the [Releases](releases) page.
2. Before running it, compare the SHA-256 printed in the release notes with the
   `ldcc-build.json` file that ships next to the download. They should match.
3. Double-click `ldcc.exe`.

Prefer to run from source? Use the `RUN_LDCC.bat` launcher — not PowerShell,
which mangles Python arguments.

## Straight answers about safety and what is real

- **It runs locally.** No account, no telemetry, no cloud sync. Your files and
  conversations stay on your computer.
- **Builds are verifiable.** Every release publishes a SHA-256 hash so you can
  confirm the file you downloaded has not been altered.
- **Signed when a certificate is set up.** If a code-signing certificate is
  configured, the build is Authenticode-signed. If not, the release notes say so
  plainly and Windows will show an "unknown publisher" warning — that is expected,
  not a defect.
- **Tested.** 1,056 automated tests pass and the code is 92% covered (measured
  2026-11-10). All CI checks are green.
- **The pricing tiers you may see on the website are a plan, not a store.** There
  is no payment, no account system, and nothing to buy yet.

## Status

<!-- docs-sync:start -->
**Version 1.0.0 — released 10 November 2026.** The current Windows build is on the [Releases](releases) page. The CI badge at the top of this file is the live build status; it is always current, so we do not print a frozen number here.
<!-- docs-sync:end -->

## For developers

- Written in Python with Tkinter. Entry point: `desktop_shell/app.py`.
- Built and signed by `.github/workflows/windows-build.yml` and `release.yml`.
- Production, signing, and deployment notes live in `docs/`.

## Author

Built by **Hatem Shalaby** — Contact Centre Operations & AI Implementation Lead,
WFM & CX Transformation.

## Licence

MIT
