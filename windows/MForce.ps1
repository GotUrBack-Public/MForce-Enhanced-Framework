#requires -Version 7.0
<#
.SYNOPSIS
  MForce Enhanced Framework for Windows 11 / PowerShell 7.
.EXAMPLE
  pwsh -NoProfile -File .\windows\MForce.ps1 -List
.EXAMPLE
  pwsh -NoProfile -File .\windows\MForce.ps1 -Module dns211 -Target example.org
.EXAMPLE
  pwsh -NoProfile -File .\windows\MForce.ps1 -Module tcp401 -Target 127.0.0.1 -Authorized
#>
[CmdletBinding(DefaultParameterSetName = 'Menu')]
param(
    [Parameter(ParameterSetName = 'List', Mandatory)][switch]$List,
    [Parameter(ParameterSetName = 'Doctor', Mandatory)][switch]$Doctor,
    [Parameter(ParameterSetName = 'Module', Mandatory)][ValidatePattern('^[a-z]{3}[0-9]{3}$')][string]$Module,
    [Parameter(ParameterSetName = 'Module')][string]$Target,
    [Parameter(ParameterSetName = 'Module')][switch]$Authorized,
    [Parameter(ParameterSetName = 'Module')][switch]$AllowPublic,
    [Parameter(ParameterSetName = 'Module')][string[]]$ModuleArgs = @(),
    [switch]$NoBanner
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
Import-Module (Join-Path $PSScriptRoot 'MForce.Windows.psm1') -Force -ErrorAction Stop
try {
    $catalog = @(Get-MForceCatalog -Root $root)
    if (-not $NoBanner) { Show-MForceBanner }
    switch ($PSCmdlet.ParameterSetName) {
        'List' { $catalog | Format-Table -AutoSize Id, Category, Name, Status, Engine; exit 0 }
        'Doctor' {
            $result = Test-MForceWindows -Root $root -Catalog $catalog
            $result | Format-List
            if (-not $result.Ready) { exit 1 }
            exit 0
        }
        'Module' {
            $selected = $catalog | Where-Object { $_.Id -ceq $Module } | Select-Object -First 1
            if ($null -eq $selected) { throw "Unknown module ID: $Module" }
            if ($selected.Status -ne 'Enabled') { throw "Module is disabled: $Module" }
            $code = Invoke-MForceWindowsModule -Root $root -Id $Module -Target $Target -Authorized:$Authorized -AllowPublic:$AllowPublic -ModuleArgs $ModuleArgs
            exit [int]$code
        }
        default { Start-MForceWindowsMenu -Root $root -Catalog $catalog; exit 0 }
    }
} catch {
    [Console]::Error.WriteLine("MForce Windows: " + $_.Exception.Message)
    exit 2
}
