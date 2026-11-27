# Security Policy

L&D Command Center is a local-first desktop application. It has no hosted service, no account
system, and no telemetry; it talks only to a model endpoint you run yourself. That removes most
of the usual server-side attack surface, and it does not remove the rest.

## Supported versions

| Version | Supported |
|---|---|
| 1.0.x   | Yes — the current release line |
| < 1.0   | No — please reproduce on 1.0.x before reporting |

## Reporting a vulnerability

**Reporting contact: to be filled in by the owner.** There is no monitored security mailbox or
private reporting channel published for this repository yet. Until the owner adds one (GitHub
Private Vulnerability Reporting is the intended route), please:

1. Do not open a public issue containing exploit details.
2. Do not include personal data, credentials, or anyone else's files in a report.
3. Re-check this file before sending: the contact will be published here, not guessed.

## What is in scope

- The desktop app and its controller (`desktop_shell/`), including file import and export.
- The local model client (`model-layer/`): request handling against an endpoint the user
  configures, and the assumption that the endpoint is trusted only because it is local.
- The storage layer: local files, their permissions, and what a crafted file can make the app do.
- The packaging and release path: code signing, the release workflow, and the Windows build.

## What is not in scope

- The model you run in LM Studio. Its behaviour and its vulnerabilities belong to that project.
- The security of a machine that is already compromised.
- Feature requests, crashes without a security consequence, and the content of generated lessons.

## Known limitations, stated rather than hidden

- The app has not had an external security review.
- The AI features inherit the model's behaviour; output is not a security boundary.
- Release signing depends on the owner's certificate; a build without it is unsigned and the
  release workflow reports that state rather than hiding it. See `docs/CODE_SIGNING.md`.
