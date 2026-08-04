param(
    [switch]$Rebuild,
    [switch]$Detached
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $projectRoot '.env.local'

if (-not (Test-Path -LiteralPath $envFile)) {
    throw 'Missing .env.local. Run .\scripts\new-env-local.ps1 first.'
}

$composeArgs = @('compose', '--env-file', '.env.local', 'up')
if ($Rebuild) { $composeArgs += '--build' }
if ($Detached) { $composeArgs += '--detach' }
& docker @composeArgs
