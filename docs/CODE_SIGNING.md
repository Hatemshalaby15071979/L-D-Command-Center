# Windows code signing — what it is, what to buy, how it is wired

This document covers the Authenticode signing stage for `dist/ldcc.exe`. The
pipeline is already built for it: `desktop_shell/sign_build.ps1` runs between
the PyInstaller build and the build manifest, in both
`.github/workflows/windows-build.yml` and `.github/workflows/release.yml`.
Until a certificate is configured the step logs a notice, writes an
`unsigned` record, and the build continues. Nothing else needs to change when
the certificate arrives — only the two repository secrets.

---

## 1. What signing actually changes

An Authenticode signature is a certificate from a public CA, bound to a
verified identity, attached to the PE file along with a timestamp.

| | Unsigned | Signed |
|---|---|---|
| SmartScreen dialog | "Windows protected your PC — Unknown publisher", Run button hidden behind "More info" | Publisher name shown; warning fades as reputation accrues |
| Corporate Defender / AppLocker | Frequently blocked | Allowed by most policies |
| Antivirus false positives | Common on PyInstaller output — the bootloader is a known false-positive magnet | Materially fewer |
| User trust | "Is this malware?" | "This is from a named publisher" |

Signing does not make the binary trustworthy. It makes it **attributable** —
which is what SmartScreen and enterprise policy actually check.

---

## 2. The options

| Option | What it is | Fits you if | Does not fit if |
|---|---|---|---|
| **Self-signed** | Your own CA, installed manually on each machine | You only run the build on your own PCs | Anyone else downloads it — the warning is identical to unsigned |
| **OV code signing** (Organisation Validation) | CA verifies your legal identity, issues a signing certificate | You want a real publisher name; you accept a reputation warm-up period | You need the warning gone on day one |
| **EV code signing** (Extended Validation) | Stricter audit, hardware-bound key | You need immediate SmartScreen trust | Budget is tight — EV costs more and requires a token |
| **Azure Artifact Signing** (formerly Trusted Signing) | Microsoft-hosted signing service, no hardware token, pay per signature | You can pass Microsoft's identity validation | Your identity validation is rejected — this is the common failure mode |

### The constraint that catches most people

Since June 2023, CA/Browser Forum rules require the private key of a publicly
trusted code-signing certificate to live on **FIPS 140-2 Level 2 hardware** —
a USB token or an HSM. You cannot download a `.pfx` and keep it on disk any
more, at least not from a CA that follows the rules. Practical consequences:

- A physical token means signing happens on a machine the token is plugged
  into. CI cannot use it unless the CA offers a cloud-signing portal.
- Many CAs now sell "cloud code signing" — you upload the hash through a web
  UI or an API and get a signature back. That is the shape you want for CI.
- Some resellers still issue file-based `.pfx` certificates. Verify before
  paying; if the CA is not on the CA/Browser Forum's list, SmartScreen will
  not trust it either.

### Azure Artifact Signing eligibility

Microsoft opened Trusted Signing to individual developers in public preview in
late 2024, which removed the "organisation only" barrier. Identity validation
is still mandatory, and it checks verifiable business history — historically
three years. **Confirm your eligibility before building the pipeline around
it.** If validation fails, you have wasted nothing: the current workflow is
CA-agnostic.

---

## 3. What to ask a CA for

If you buy an OV or EV certificate, ask these four questions explicitly:

1. *"Is the private key HSM-backed or token-based, and can I sign from CI?"*
   You want "cloud signing API" or "hosted HSM", not "we ship a USB token".
2. *"Can I export the certificate as a `.pfx` for `signtool /f`?"*
   If yes, the workflow below works unchanged. If no, use the CA's signing
   tool instead of `signtool` and adapt the script.
3. *"Does the certificate support RFC 3161 timestamping?"* It must — without a
   timestamp the signature dies when the certificate expires.
4. *"How long is the validity, and what does renewal cost?"* Typically one
   year. Renewal means a new secret and a new release.

Budget expectation: an OV certificate is a few hundred USD per year; EV is
more. Prices move — check current quotes rather than trusting a figure here.

---

## 4. Wiring it in (PFX / file-based path)

### 4.1 Add the secrets

```bash
# encode the .pfx as a single base64 line
base64 -w0 codesign.pfx > codesign.pfx.b64
```

In the repository: **Settings → Secrets and variables → Actions → New
repository secret**

| Name | Value |
|---|---|
| `LDCC_SIGN_PFX_BASE64` | contents of `codesign.pfx.b64` |
| `LDCC_SIGN_PFX_PASSWORD` | the `.pfx` export password |

Do not commit the `.pfx`, the `.b64`, or the password. `check_deployment_policy.py`
will not catch a committed `.pfx` — it only scans the PyInstaller staging tree
— so this is on you.

### 4.2 What the pipeline does

`sign_build.ps1`:

1. Decodes `LDCC_SIGN_PFX_BASE64` into a temp file under `%TEMP%`.
2. Finds the newest `signtool.exe` under `Windows Kits\10\bin\*\x64`.
3. Runs `signtool sign /fd SHA256 /td SHA256 /tr <timestamp> /f <pfx> /d "L&D Command Center"`.
4. Runs `signtool verify /pa /v` and checks `Get-AuthenticodeSignature.Status -eq "Valid"`.
5. Writes `dist/ldcc-signature.json` with the subject, thumbprint, issuer and
   expiry.
6. Deletes the temp `.pfx` in a `finally` block.

Exit codes: `0` signed, `3` no certificate configured, `1` signing or
verification failed, `2` artifact missing. The workflows treat `3` as a pass.

### 4.3 Order of operations — do not reorder

```
PyInstaller build  →  sign  →  write_build_manifest.py  →  verify_build.ps1  →  upload
```

Signing rewrites the PE header, so any SHA-256 taken before signing will not
match the shipped file. The manifest runs after signing for exactly this
reason, and it reads `ldcc-signature.json` to record the signing status
alongside the hash.

### 4.4 Local signing

```powershell
$env:LDCC_SIGN_PFX_PATH = "C:\keys\codesign.pfx"
$env:LDCC_SIGN_PFX_PASSWORD = "..."
pwsh -File desktop_shell\sign_build.ps1 -ExePath dist\ldcc.exe
```

Then check it yourself:

```powershell
Get-AuthenticodeSignature .\dist\ldcc.exe | Format-List Status, StatusMessage, SignerCertificate
```

`Status` must be `Valid`. `UnknownError` usually means the timestamp server was
unreachable; `NotSigned` means the sign call silently did nothing.

---

## 5. Wiring it in (Azure Artifact Signing path)

If you go the Microsoft route, replace the sign step with the hosted action.
`sign_build.ps1` is not used on this path.

```yaml
      - name: Sign executable (Azure Artifact Signing)
        uses: azure/trusted-signing-action@v0
        with:
          azure-tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          azure-client-id: ${{ secrets.AZURE_CLIENT_ID }}
          azure-client-secret: ${{ secrets.AZURE_CLIENT_SECRET }}
          endpoint: https://eus.codesigning.azure.net/
          trusted-signing-account-name: ${{ secrets.AZURE_SIGNING_ACCOUNT }}
          certificate-profile-name: ${{ secrets.AZURE_SIGNING_PROFILE }}
          files-folder: dist
          files-folder-filter: exe
          file-digest: SHA256
          timestamp-rfc3161: http://timestamp.acs.microsoft.com
          timestamp-digest: SHA256
```

Keep the step in the same position — before the manifest — and write a
`dist/ldcc-signature.json` afterwards (or let the manifest record
`"signature": {"status": "unknown"}`, which is honest but less useful).

Federated credentials (OIDC) are preferable to a client secret if you are
comfortable adding a federated identity to an Entra app registration.

---

## 6. If you ship unsigned

That is the current default and it is a legitimate choice. The build already
produces `dist/ldcc-build.json` with the SHA-256 and `dist/ldcc-signature.json`
with `"status": "unsigned"`, and the release notes say so. Tell users to:

```powershell
Get-FileHash .\ldcc.exe -Algorithm SHA256
# compare against the sha256 field in ldcc-build.json
```

The SmartScreen warning will appear. There is no way around that other than a
certificate.

---

## 7. Renewal

- The signature stays valid after expiry **only if it was timestamped**. Both
  workflows timestamp via `http://timestamp.digicert.com`.
- Renew before `notAfter` (recorded in `ldcc-signature.json`), replace
  `LDCC_SIGN_PFX_BASE64` and `LDCC_SIGN_PFX_PASSWORD`, and cut a new release.
- Old releases do not need re-signing; their timestamps remain valid.
