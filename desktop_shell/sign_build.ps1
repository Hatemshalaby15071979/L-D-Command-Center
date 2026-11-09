<#
.SYNOPSIS
    Authenticode-sign dist\ldcc.exe and record what happened.

.DESCRIPTION
    Runs as the stage between the PyInstaller build and the build manifest.
    Order matters: signing rewrites the PE, so the manifest's SHA-256 must be
    computed afterwards or it will not match the shipped file.

    Credentials are read from the environment (LDCC_SIGN_PFX_BASE64,
    LDCC_SIGN_PFX_PASSWORD) or from -PfxPath / -PfxPassword. When neither is
    present the script does not fail the build: it writes an "unsigned"
    signature record and exits 3, which the workflow treats as "ship unsigned".

    Always writes <Dist>\ldcc-signature.json so the artifact set is complete
    whether or not a certificate is configured.

.PARAMETER ExePath
    Path to the built executable.

.PARAMETER PfxPath
    Path to a .pfx/.p12 file. Overrides LDCC_SIGN_PFX_BASE64.

.PARAMETER PfxPassword
    Password for the .pfx. Defaults to LDCC_SIGN_PFX_PASSWORD.

.PARAMETER TimestampUrl
    RFC 3161 timestamp server. Without a timestamp the signature expires with
    the certificate and Windows starts warning again.

.OUTPUTS
    Exit code 0  signed and verified
    Exit code 1  signing or verification failed
    Exit code 2  usage error / artifact missing
    Exit code 3  no certificate configured (unsigned build, not an error)
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ExePath,

    [string]$PfxPath = $env:LDCC_SIGN_PFX_PATH,

    [string]$PfxPassword = $env:LDCC_SIGN_PFX_PASSWORD,

    [string]$TimestampUrl = "http://timestamp.digicert.com",

    [string]$Description = "L&D Command Center",

    [string]$RecordPath
)

$ErrorActionPreference = "Stop"

function Fail([string]$Message, [int]$Code) {
    Write-Host "SIGN FAIL: $Message"
    exit $Code
}

function Find-SignTool {
    $roots = @(
        "${env:ProgramFiles(x86)}\Windows Kits\10\bin",
        "$env:ProgramFiles\Windows Kits\10\bin"
    ) | Where-Object { $_ -and (Test-Path $_) }

    foreach ($root in $roots) {
        $candidate = Get-ChildItem -Path $root -Filter "signtool.exe" -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -match '\\x64\\' } |
            Sort-Object FullName -Descending |
            Select-Object -First 1
        if ($candidate) { return $candidate.FullName }
    }
    return $null
}

function Write-Record([hashtable]$Record, [string]$Path) {
    $json = $Record | ConvertTo-Json -Depth 5
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $json + "`n", $utf8)
    Write-Host "SIGN RECORD: $Path"
}

$resolved = Resolve-Path -LiteralPath $ExePath -ErrorAction SilentlyContinue
if (-not $resolved) {
    Fail "artifact not found: $ExePath" 2
}
$exe = $resolved.Path
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
    Fail "artifact is not a file: $exe" 2
}

$dist = Split-Path -Parent $exe
if (-not $RecordPath) { $RecordPath = Join-Path $dist "ldcc-signature.json" }

$baseRecord = @{
    artifact     = (Split-Path -Leaf $exe)
    timestampUrl = $TimestampUrl
    signedUtc    = $null
    status       = "unsigned"
    subject      = $null
    issuer       = $null
    thumbprint   = $null
    notAfter     = $null
    signTool     = $null
    reason       = $null
}

# ── resolve credentials ────────────────────────────────────────────────────
$tempPfx = $null
try {
    if (-not $PfxPath -and $env:LDCC_SIGN_PFX_BASE64) {
        $tempPfx = Join-Path ([System.IO.Path]::GetTempPath()) ("ldcc-sign-" + [guid]::NewGuid().ToString("N") + ".pfx")
        [System.IO.File]::WriteAllBytes($tempPfx, [Convert]::FromBase64String($env:LDCC_SIGN_PFX_BASE64))
        $PfxPath = $tempPfx
    }

    if (-not $PfxPath) {
        $baseRecord.reason = "no certificate configured (LDCC_SIGN_PFX_BASE64 / -PfxPath unset)"
        Write-Record $baseRecord $RecordPath
        Write-Host "SIGN SKIP: $($baseRecord.reason)"
        exit 3
    }

    if (-not (Test-Path -LiteralPath $PfxPath -PathType Leaf)) {
        Fail "certificate file not found: $PfxPath" 1
    }

    $signTool = Find-SignTool
    if (-not $signTool) {
        Fail "signtool.exe not found. Install the Windows SDK signing tools, or use the Azure Artifact Signing path in docs/CODE_SIGNING.md." 1
    }

    # ── sign ──────────────────────────────────────────────────────────────
    $signArgs = @(
        "sign",
        "/fd", "SHA256",
        "/td", "SHA256",
        "/tr", $TimestampUrl,
        "/f", $PfxPath,
        "/d", $Description,
        "/du", "https://github.com/hatemshalaby15071979/L-D-Command-Center"
    )
    if ($PfxPassword) { $signArgs += @("/p", $PfxPassword) }
    $signArgs += $exe

    # Never echo the .pfx password into the build log.
    $display = $signArgs -join ' '
    if ($PfxPassword) { $display = $display -replace [regex]::Escape($PfxPassword), '***' }
    Write-Host "SIGN: $display"
    & $signTool @signArgs
    if ($LASTEXITCODE -ne 0) { Fail "signtool sign exited $LASTEXITCODE" 1 }

    # ── verify ────────────────────────────────────────────────────────────
    & $signTool verify /pa /v $exe | Out-Host
    if ($LASTEXITCODE -ne 0) { Fail "signtool verify exited $LASTEXITCODE" 1 }

    $auth = Get-AuthenticodeSignature -FilePath $exe
    if ($auth.Status -ne "Valid") {
        Fail "signature status is '$($auth.Status)', expected Valid" 1
    }

    $baseRecord.status     = "signed"
    $baseRecord.signedUtc  = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $baseRecord.subject    = $auth.SignerCertificate.Subject
    $baseRecord.issuer     = $auth.SignerCertificate.Issuer
    $baseRecord.thumbprint = $auth.SignerCertificate.Thumbprint
    $baseRecord.notAfter   = $auth.SignerCertificate.NotAfter.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $baseRecord.signTool   = $signTool

    Write-Record $baseRecord $RecordPath
    Write-Host "SIGN OK: $($auth.SignerCertificate.Subject)"
    exit 0
}
finally {
    if ($tempPfx -and (Test-Path -LiteralPath $tempPfx)) {
        Remove-Item -LiteralPath $tempPfx -Force -ErrorAction SilentlyContinue
    }
}
