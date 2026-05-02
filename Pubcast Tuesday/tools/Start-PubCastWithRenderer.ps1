<#
Start PubCast with renderer first.
Run from the merged PubCast folder, or pass -PubCastRoot.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)] [string]$PubCastRoot = $PWD,
    [Parameter(Mandatory=$false)] [int]$RendererPort = 9001,
    [Parameter(Mandatory=$false)] [int]$PubCastPort = 8000,
    [Parameter(Mandatory=$false)] [string]$PythonCommand = "python",
    [Parameter(Mandatory=$false)] [switch]$NoRenderer
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-PortOpen {
    param([string]$HostName, [int]$Port)
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $iar = $client.BeginConnect($HostName, $Port, $null, $null)
        $success = $iar.AsyncWaitHandle.WaitOne(500, $false)
        if ($success -and $client.Connected) {
            $client.EndConnect($iar)
            $client.Close()
            return $true
        }
        $client.Close()
        return $false
    } catch { return $false }
}

function Wait-Port {
    param([string]$HostName, [int]$Port, [int]$Seconds)
    $deadline = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-PortOpen -HostName $HostName -Port $Port) { return $true }
        Start-Sleep -Milliseconds 500
    }
    return $false
}

$PubCastRoot = [System.IO.Path]::GetFullPath($PubCastRoot)
if (-not (Test-Path -LiteralPath (Join-Path $PubCastRoot "main.py"))) {
    throw "main.py not found under PubCastRoot: $PubCastRoot"
}

$LogDir = Join-Path $PubCastRoot "_runtime_logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Force -Path $LogDir | Out-Null }
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"

Push-Location $PubCastRoot
try {
    if (-not $NoRenderer) {
        $rendererCandidates = @(
            (Join-Path $PubCastRoot "bin\ws_renderer.exe"),
            (Join-Path $PubCastRoot "bin\ws_renderer")
        )
        $renderer = $rendererCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
        if ($renderer) {
            $rendererSize = (Get-Item -LiteralPath $renderer).Length
            if ($rendererSize -lt 1000000) {
                Write-Warning "Renderer file exists but is suspiciously small: $rendererSize bytes"
            }
            if (Test-PortOpen -HostName "127.0.0.1" -Port $RendererPort) {
                Write-Host "Renderer port $RendererPort already open; not starting another renderer."
            } else {
                $rendererLog = Join-Path $LogDir "renderer_$Stamp.log"
                Write-Host "Starting renderer: $renderer"
                Start-Process -FilePath $renderer -WorkingDirectory $PubCastRoot -RedirectStandardOutput $rendererLog -RedirectStandardError $rendererLog
                if (Wait-Port -HostName "127.0.0.1" -Port $RendererPort -Seconds 10) {
                    Write-Host "Renderer is listening on port $RendererPort."
                } else {
                    Write-Warning "Renderer did not open port $RendererPort within 10 seconds. PubCast may fall back to emergency bridge mode. Log: $rendererLog"
                }
            }
        } else {
            Write-Warning "No renderer binary found in bin\. PubCast will start without renderer."
        }
    }

    $serverLog = Join-Path $LogDir "pubcast_$Stamp.log"
    Write-Host "Starting PubCast server on port $PubCastPort..."

    & $PythonCommand -c "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('uvicorn') else 1)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Start-Process -FilePath $PythonCommand -ArgumentList @("-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "$PubCastPort") -WorkingDirectory $PubCastRoot -RedirectStandardOutput $serverLog -RedirectStandardError $serverLog
    } else {
        Start-Process -FilePath $PythonCommand -ArgumentList @("main.py") -WorkingDirectory $PubCastRoot -RedirectStandardOutput $serverLog -RedirectStandardError $serverLog
    }

    Start-Sleep -Seconds 3
    $healthUrl = "http://127.0.0.1:$PubCastPort/health"
    try {
        $health = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 5
        $healthPath = Join-Path $LogDir "health_$Stamp.json"
        $health.Content | Set-Content -LiteralPath $healthPath -Encoding UTF8
        Write-Host "Health check saved: $healthPath"
        Write-Host $health.Content
    } catch {
        Write-Warning "Could not fetch /health yet. Server log: $serverLog"
    }

    Write-Host "Runtime logs: $LogDir"
} finally { Pop-Location }
