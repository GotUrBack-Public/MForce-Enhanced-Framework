#requires -Version 7.0
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$entry = Join-Path $root 'windows/MForce.ps1'
Import-Module (Join-Path $root 'windows/MForce.Windows.psm1') -Force
function Assert-True {
    param([bool]$Condition,[string]$Message)
    if (-not $Condition) { throw "ASSERTION FAILED: $Message" }
}
function Invoke-Launcher {
    param([string[]]$Arguments)
    $result = & pwsh -NoProfile -File $entry -NoBanner @Arguments 2>&1
    return [pscustomobject]@{ ExitCode=$LASTEXITCODE; Output=($result -join [Environment]::NewLine) }
}
$catalog = @(Get-MForceCatalog -Root $root)
$enabled = @($catalog | Where-Object Status -eq 'Enabled')
Assert-True ($catalog.Count -eq 23) 'Shared registry must expose 23 entries'
Assert-True ($enabled.Count -eq 21) 'Windows must expose all 21 enabled modules'
Assert-True ((@($catalog | Where-Object Status -eq 'Disabled')).Count -eq 2) 'Disabled modules stay disabled'
Assert-True ((@($catalog | Where-Object { $_.Engine -eq 'disabled' })).Count -eq 2) 'Disabled modules are never executable'
$list = Invoke-Launcher -Arguments @('-List')
Assert-True ($list.ExitCode -eq 0) 'List command failed'
Assert-True ($list.Output.Contains('dns211') -and $list.Output.Contains('pth407')) 'List is missing modules'
$doctor = Invoke-Launcher -Arguments @('-Doctor')
Assert-True ($doctor.ExitCode -eq 0) "Doctor failed: $($doctor.Output)"
$xss = Invoke-Launcher -Arguments @('-Module','xss402','-ModuleArgs','--list-categories')
Assert-True ($xss.ExitCode -eq 0) "Offline XSS library failed: $($xss.Output)"
Assert-True ($xss.Output.Contains('javascript')) 'Offline lab categories unavailable'
$disabled = Invoke-Launcher -Arguments @('-Module','frc742')
Assert-True ($disabled.ExitCode -eq 2) 'Disabled module executed'
$unauthorized = Invoke-Launcher -Arguments @('-Module','tcp401','-Target','127.0.0.1')
Assert-True ($unauthorized.ExitCode -eq 2) 'Active scan executed without authorization'
$bypass = Invoke-Launcher -Arguments @('-Module','tcp401','-Target','127.0.0.1','-Authorized','-ModuleArgs','--allow-public')
Assert-True ($bypass.ExitCode -eq 2) 'Authorization switch bypass accepted'
$noTarget = Invoke-Launcher -Arguments @('-Module','dns211')
Assert-True ($noTarget.ExitCode -eq 2) 'Targetless module executed'
$temp = Join-Path ([IO.Path]::GetTempPath()) ('mforce-windows-smoke-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $temp | Out-Null
try {
    Set-Content -LiteralPath (Join-Path $temp 'safe.txt') -Value 'harmless fixture' -Encoding utf8
    $secret = Invoke-Launcher -Arguments @('-Module','sec601','-Target',$temp,'-ModuleArgs','--json')
    Assert-True ($secret.ExitCode -eq 0) "Offline secret audit failed: $($secret.Output)"
    Assert-True ($secret.Output.Contains('checked_files')) 'Secret audit result missing'
} finally { Remove-Item -LiteralPath $temp -Recurse -Force }
Write-Host 'Windows 11 PowerShell port smoke tests: PASS' -ForegroundColor Green
