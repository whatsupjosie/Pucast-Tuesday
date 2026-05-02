<#
Verify PubCast merge/staging tree without deleting or changing source files.
Run from the PubCast root or pass -PubCastRoot. Outputs are written to _merge_verification/.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)] [string]$PubCastRoot = $PWD,
    [Parameter(Mandatory=$false)] [string]$PythonCommand = "python",
    [Parameter(Mandatory=$false)] [switch]$SkipPytest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step { param([string]$Message) Write-Host "==> $Message" }

function Get-FileReport {
    param([string]$Root, [string]$RelativePath)
    $full = Join-Path $Root $RelativePath
    if (Test-Path -LiteralPath $full) {
        $item = Get-Item -LiteralPath $full
        $hash = Get-FileHash -LiteralPath $full -Algorithm SHA256
        [pscustomobject]@{ Path=$RelativePath; Exists=$true; Bytes=$item.Length; SHA256=$hash.Hash; Note="present" }
    } else {
        [pscustomobject]@{ Path=$RelativePath; Exists=$false; Bytes=0; SHA256=""; Note="MISSING" }
    }
}

$PubCastRoot = [System.IO.Path]::GetFullPath($PubCastRoot)
if (-not (Test-Path -LiteralPath $PubCastRoot)) { throw "PubCastRoot does not exist: $PubCastRoot" }

$VerifyDir = Join-Path $PubCastRoot "_merge_verification"
if (-not (Test-Path $VerifyDir)) { New-Item -ItemType Directory -Force -Path $VerifyDir | Out-Null }

Write-Step "Verifying PubCast tree: $PubCastRoot"

$critical = @(
    "main.py",
    "modules\voxel_asset_manager.py",
    "modules\voxel_llm_adapter.py",
    "modules\voxel_studio_integration.py",
    "modules\studio_control.py",
    "modules\studio_websocket.py",
    "modules\pubworld_router.py",
    "modules\unity_bridge.py",
    "modules\session_resurrector.py",
    "modules\alex_jeremy_bridge.py",
    "modules\feature_flags.py",
    "modules\route_security.py",
    "modules\character_cast.py",
    "modules\bridge_bulletproof.py",
    "modules\irm.py",
    "bin\ws_renderer",
    "bin\ws_renderer.exe",
    "Cargo.toml",
    "pubcast-renderer\Cargo.toml",
    "renderer\Cargo.toml"
)

$reports = foreach ($path in $critical) { Get-FileReport -Root $PubCastRoot -RelativePath $path }
$csvPath = Join-Path $VerifyDir "critical_files.csv"
$reports | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $csvPath
Write-Step "Wrote critical file report: $csvPath"

$required = @(
    "main.py",
    "modules\session_resurrector.py",
    "modules\alex_jeremy_bridge.py",
    "modules\feature_flags.py",
    "modules\route_security.py",
    "modules\character_cast.py"
)
$missingRequired = $reports | Where-Object { -not $_.Exists -and $_.Path -in $required }

$rendererReports = $reports | Where-Object { $_.Path -like "bin\ws_renderer*" -and $_.Exists }
$rendererWarning = $false
if (-not $rendererReports) {
    $rendererWarning = $true
    Write-Warning "No bin/ws_renderer or bin/ws_renderer.exe found. Renderer bridge will fall back or fail."
} else {
    foreach ($r in $rendererReports) {
        if ([int64]$r.Bytes -lt 1000000) {
            $rendererWarning = $true
            Write-Warning "Renderer exists but is suspiciously small: $($r.Path) = $($r.Bytes) bytes"
        }
    }
}

$summaryPath = Join-Path $VerifyDir "verification_summary.txt"
@(
    "PubCast Merge Verification",
    "Timestamp: $(Get-Date -Format o)",
    "Root: $PubCastRoot",
    "",
    "Critical files checked: $($reports.Count)",
    "Missing required files: $($missingRequired.Count)",
    "Renderer warning: $rendererWarning",
    "",
    "Missing required paths:",
    ($missingRequired | ForEach-Object { "- $($_.Path)" })
) | Set-Content -Encoding UTF8 -Path $summaryPath

Push-Location $PubCastRoot
try {
    Write-Step "Running Python syntax compile check"
    $syntaxOut = Join-Path $VerifyDir "syntax_check.txt"
    $compileTargets = @()
    if (Test-Path -LiteralPath "main.py") { $compileTargets += "main.py" }
    if (Test-Path -LiteralPath "modules") { $compileTargets += "modules" }
    if ($compileTargets.Count -gt 0) {
        & $PythonCommand -m compileall -q @compileTargets *> $syntaxOut
        $syntaxExit = $LASTEXITCODE
    } else {
        "No main.py/modules targets found." | Set-Content -Encoding UTF8 -Path $syntaxOut
        $syntaxExit = 2
    }

    Write-Step "Running guarded import check"
    $importScript = @'
import importlib
mods = [
    "modules.session_resurrector",
    "modules.alex_jeremy_bridge",
    "modules.feature_flags",
    "modules.route_security",
    "modules.character_cast",
    "modules.voxel_asset_manager",
    "modules.voxel_llm_adapter",
    "modules.voxel_studio_integration",
    "modules.studio_websocket",
    "modules.pubworld_router",
    "modules.unity_bridge",
]
failures = []
for name in mods:
    try:
        importlib.import_module(name)
        print(f"OK {name}")
    except Exception as exc:
        failures.append((name, repr(exc)))
        print(f"FAIL {name}: {exc!r}")
if failures:
    raise SystemExit(1)
'@
    $importPath = Join-Path $VerifyDir "_import_check.py"
    $importOut = Join-Path $VerifyDir "import_check.txt"
    $importScript | Set-Content -Encoding UTF8 -Path $importPath
    & $PythonCommand $importPath *> $importOut
    $importExit = $LASTEXITCODE

    $pytestExit = $null
    if (-not $SkipPytest) {
        Write-Step "Running pytest if available"
        $pytestOut = Join-Path $VerifyDir "pytest.txt"
        & $PythonCommand -m pytest -q *> $pytestOut
        $pytestExit = $LASTEXITCODE
    }
}
finally { Pop-Location }

$final = [pscustomobject]@{
    Root=$PubCastRoot
    CriticalFilesCsv=$csvPath
    Summary=$summaryPath
    MissingRequiredCount=$missingRequired.Count
    RendererWarning=$rendererWarning
    SyntaxExitCode=$syntaxExit
    ImportExitCode=$importExit
    PytestExitCode=$pytestExit
}

$final | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 -Path (Join-Path $VerifyDir "verification_result.json")
$final | Format-List

if ($missingRequired.Count -gt 0 -or $rendererWarning -or $syntaxExit -ne 0 -or $importExit -ne 0) { exit 1 }
if ($pytestExit -ne $null -and $pytestExit -ne 0) { exit 1 }
exit 0
