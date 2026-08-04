param(
    [switch]$Force
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$templatePath = Join-Path $projectRoot '.env.local.example'
$localPath = Join-Path $projectRoot '.env.local'

if ((Test-Path -LiteralPath $localPath) -and -not $Force) {
    Write-Host '.env.local already exists; no changes made.'
    exit 0
}

Copy-Item -LiteralPath $templatePath -Destination $localPath -Force:$Force
Write-Host 'Created .env.local. Update its database and API-key values before starting Django.'
