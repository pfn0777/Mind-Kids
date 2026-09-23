# Deploys the Mind Kids Telegram bot to Hetzner over SSH.
#
# Windows PowerShell 5.1 compatible: no `&&`, no ternary, no 3-arg Join-Path
# (that overload does not exist in 5.1). Copies bot/ and deploy/ to a staging
# directory first (excluding local junk), scp's that staging dir to the
# server, then runs deploy/install.sh there.
#
# install.sh derives its source root from its own location's parent, so the
# staging layout on the server must mirror the repo: <root>/bot and
# <root>/deploy.
#
#   powershell -File deploy/deploy.ps1
#   powershell -File deploy/deploy.ps1 -Server root@1.2.3.4
#   powershell -File deploy/deploy.ps1 -StageOnly   # build+print the staging tree, no ssh/scp

param(
    [string]$Server = "root@178.104.103.113",
    [switch]$StageOnly
)

$RepoRoot = Split-Path -Parent $PSScriptRoot
$RemoteStaging = "/tmp/mindkids-bot-src"

function Assert-ExitCode {
    param([string]$Description)
    if ($LASTEXITCODE -ne 0) {
        throw "$Description failed with exit code $LASTEXITCODE"
    }
}

# ---- 1. Build a clean local staging dir (exclude venv/cache/secrets/data) ----
$Staging = Join-Path $env:TEMP ("mindkids-bot-deploy-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $Staging -Force | Out-Null
$StagingBot = Join-Path $Staging "bot"
$StagingDeploy = Join-Path $Staging "deploy"
New-Item -ItemType Directory -Path $StagingBot -Force | Out-Null
New-Item -ItemType Directory -Path $StagingDeploy -Force | Out-Null

$ExcludeDirs = @(".venv", "__pycache__", ".pytest_cache", "data")
$ExcludeFiles = @(".env")

try {
    Write-Host "==> Staging bot/ -> $StagingBot"
    Get-ChildItem -Path (Join-Path $RepoRoot "bot") -Force | ForEach-Object {
        if ($_.PSIsContainer) {
            if ($ExcludeDirs -notcontains $_.Name) {
                Copy-Item -Path $_.FullName -Destination (Join-Path $StagingBot $_.Name) -Recurse -Force
            }
        }
        else {
            if (($ExcludeFiles -notcontains $_.Name) -and ($_.Extension -ne ".db")) {
                Copy-Item -Path $_.FullName -Destination (Join-Path $StagingBot $_.Name) -Force
            }
        }
    }

    Write-Host "==> Staging deploy/ -> $StagingDeploy"
    $DeploySource = Join-Path (Join-Path $RepoRoot "deploy") "*"
    Copy-Item -Path $DeploySource -Destination $StagingDeploy -Recurse -Force

    if ($StageOnly) {
        Write-Host "==> Staged tree ($Staging):"
        Get-ChildItem -Path $Staging -Recurse -Name
        return
    }

    # ---- 2. Ship the staging dir to the server ----
    # Native ssh/scp/apt-get/pip write normal progress to stderr; under PS 5.1
    # that becomes a NativeCommandError under "Stop" and aborts the script
    # even on a successful (exit 0) run. Rely on $LASTEXITCODE instead.
    $ErrorActionPreference = "Continue"

    Write-Host "==> Resetting remote staging dir"
    ssh $Server "rm -rf $RemoteStaging && mkdir -p $RemoteStaging"
    Assert-ExitCode "ssh (reset remote staging dir)"

    Write-Host "==> Copying files to $Server`:$RemoteStaging"
    scp -r "$Staging/bot" "$Staging/deploy" "${Server}:${RemoteStaging}/"
    Assert-ExitCode "scp"

    # ---- 3. Install/update on the server ----
    Write-Host "==> Running install.sh on the server"
    ssh $Server "sudo bash $RemoteStaging/deploy/install.sh"
    Assert-ExitCode "ssh (install.sh)"

    # ---- 4. Report status ----
    Write-Host "==> Service status"
    ssh $Server "systemctl is-active mindkids-bot; journalctl -u mindkids-bot -n 20 --no-pager"
    Assert-ExitCode "ssh (status check)"
}
finally {
    # Always cleaned up, including when scp/ssh throws above.
    Remove-Item -Path $Staging -Recurse -Force -ErrorAction SilentlyContinue
}
