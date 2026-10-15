#requires -Version 7.0
# Native Windows orchestration, shared Python engines; Bash/WSL are never invoked.
Set-StrictMode -Version Latest
$script:engineMap = @{
    frc386='native-network';sys193='native-system';upd501='native-update'
    frc742='disabled';osn521='disabled'
    dns211='osint:dns';ipa212='osint:ip';tls213='osint:tls';hdr214='osint:headers'
    web311='osint:web';api312='osint:api';rat313='osint:rate';jsn314='osint:js'
    rob315='osint:robots';rdp316='osint:rdap'
    tcp401='python:src/offensive/tcp_scan.py'
    xss402='python:src/offensive/xss_lab.py'
    ref403='python:src/offensive/reflection.py'
    sec601='python:src/defensive/secrets_audit.py'
    cor404='audit:cors';met405='audit:methods';coo406='audit:cookies';pth407='audit:paths'
}
$script:activeNetwork = @('tcp401','ref403','cor404','met405','coo406','pth407')
$script:targetRequired = @('dns211','ipa212','tls213','hdr214','web311','api312','rat313','jsn314','rob315','rdp316','tcp401','ref403','cor404','met405','coo406','pth407','sec601')
function Show-MForceBanner {
    Write-Host ''
    Write-Host '  MFORCE / ENHANCED FRAMEWORK' -ForegroundColor Cyan
    Write-Host '  WINDOWS 11 | POWERSHELL 7 | NATIVE TERMINAL' -ForegroundColor Gray
    Write-Host '  Educational & authorized professional use only.' -ForegroundColor DarkGray
    Write-Host ''
}
function Get-MForceCatalog {
    param([Parameter(Mandatory)][string]$Root)
    $registry = Join-Path $Root 'src/data/funcs.json'
    $categoriesPath = Join-Path $Root 'src/data/cats.json'
    if (-not (Test-Path -LiteralPath $registry -PathType Leaf) -or -not (Test-Path -LiteralPath $categoriesPath -PathType Leaf)) {
        throw 'Missing shared MForce registry.'
    }
    $data = Get-Content -LiteralPath $registry -Raw -Encoding utf8 | ConvertFrom-Json
    $categories = Get-Content -LiteralPath $categoriesPath -Raw -Encoding utf8 | ConvertFrom-Json
    if ($null -eq $data.functions -or $null -eq $categories.categories) { throw 'Invalid MForce registry structure.' }
    $known = @{}
    foreach ($category in $categories.categories) {
        if ($category.id -notmatch '^[a-z]+$' -or $known.ContainsKey($category.id)) { throw 'Invalid or duplicate category.' }
        $known[$category.id] = [bool]$category.enabled
    }
    $seen = @{}
    $items = @(
        foreach ($item in $data.functions) {
            $id = [string]$item.id
            if ($id -cnotmatch '^[a-z]{3}[0-9]{3}$' -or $seen.ContainsKey($id) -or -not $script:engineMap.ContainsKey($id)) {
                throw "Unmapped or duplicate module: $id"
            }
            if (-not $known.ContainsKey([string]$item.category)) { throw "Unknown category for $id" }
            if ($item.enabled -isnot [bool]) { throw "Invalid enabled state for $id" }
            $seen[$id] = $true
            $enabled = [bool]$item.enabled -and $known[[string]$item.category]
            [pscustomobject]@{
                Id=$id; Name=[string]$item.name; Category=[string]$item.category
                Status=$(if ($enabled) {'Enabled'} else {'Disabled'})
                Engine=$script:engineMap[$id]
            }
        }
    )
    if ($items.Count -ne $data.functions.Count) { throw 'Registry count mismatch.' }
    return $items
}
function Get-MForcePython {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $python) { return $null }
    try {
        $version = & $python.Source --version 2>&1
        if ($LASTEXITCODE -eq 0 -and "$version" -match 'Python 3\.(1[0-9]|[2-9][0-9])') { return $python.Source }
    } catch {}
    return $null
}
function Test-MForceWindows {
    param([string]$Root, [object[]]$Catalog)
    $python = Get-MForcePython
    $native = $PSVersionTable.PSEdition -eq 'Core' -and $PSVersionTable.PSVersion.Major -ge 7
    $expected = @($Catalog | Where-Object Status -eq 'Enabled')
    $missing = @($expected | Where-Object { -not $script:engineMap.ContainsKey($_.Id) })
    [pscustomobject]@{
        Platform=$(if ($IsWindows) {'Windows'} else {'Other (CI catalog tests only)'})
        PowerShell=$PSVersionTable.PSVersion.ToString()
        Python=$(if ($python) {$python} else {'MISSING (Python 3.10+)'})
        EnabledModules=$expected.Count
        MissingMappings=$missing.Count
        Ready=($IsWindows -and $native -and [bool]$python -and $missing.Count -eq 0)
        Root=$Root
    }
}
function Invoke-MForcePython {
    param([string]$Root, [string]$Script, [string[]]$Arguments)
    $python = Get-MForcePython
    if (-not $python) { throw 'Python 3.10+ required. Install from python.org and reopen PowerShell.' }
    $full = Join-Path $Root $Script
    if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { throw "Missing Python module: $Script" }
    & $python $full @Arguments
    return [int]$LASTEXITCODE
}
function Show-MForceNetwork {
    if (-not $IsWindows) { throw 'Windows network inventory requires Windows 11.' }
    Write-Host '  NETWORK INFORMATION / WINDOWS' -ForegroundColor Cyan
    Get-NetAdapter -ErrorAction Stop | Select-Object Name,Status,LinkSpeed,InterfaceDescription | Format-Table -AutoSize
    Get-NetIPConfiguration -ErrorAction Stop | Select-Object InterfaceAlias,IPv4Address,IPv6Address,IPv4DefaultGateway,DNSServer | Format-List
    return 0
}
function Show-MForceSystem {
    if (-not $IsWindows) { throw 'Windows system inventory requires Windows 11.' }
    $os = Get-CimInstance -ClassName Win32_OperatingSystem
    $cpu = Get-CimInstance -ClassName Win32_Processor | Select-Object -First 1
    [pscustomobject]@{
        Computer=$env:COMPUTERNAME; OS=$os.Caption; Build=$os.BuildNumber
        PowerShell=$PSVersionTable.PSVersion.ToString(); CPU=$cpu.Name
        RAMGiB=[math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
        Uptime=((Get-Date) - $os.LastBootUpTime).ToString()
    } | Format-List
    return 0
}
function Invoke-MForceUpdate {
    param([string]$Root, [string[]]$Arguments)
    $git = Get-Command git -ErrorAction SilentlyContinue
    if (-not $git) { throw 'Git for Windows required to check or install updates.' }
    if (-not (Test-Path -LiteralPath (Join-Path $Root '.git'))) { throw 'Updates require a Git checkout.' }
    if ($Arguments.Count -gt 1 -or ($Arguments.Count -eq 1 -and $Arguments[0] -ne '--apply')) {
        throw 'Update accepts only --apply; without it no changes are made.'
    }
    if ($Arguments.Count -eq 0) { & $git.Source -C $Root status --short --branch }
    else { & $git.Source -C $Root pull --ff-only }
    return [int]$LASTEXITCODE
}
function Invoke-MForceWindowsModule {
    param([string]$Root, [string]$Id, [string]$Target, [switch]$Authorized, [switch]$AllowPublic, [string[]]$ModuleArgs=@())
    if (-not $script:engineMap.ContainsKey($Id)) { throw "Unknown module: $Id" }
    $record = @(Get-MForceCatalog -Root $Root | Where-Object { $_.Id -ceq $Id })
    if ($record.Count -ne 1 -or $record[0].Status -ne 'Enabled') { throw "Module disabled or unavailable: $Id" }
    $engine = [string]$script:engineMap[$Id]
    if ($Id -in $script:activeNetwork -and -not $Authorized) {
        throw "$Id requires -Authorized and explicit permission for the target."
    }
    if ($Id -in $script:targetRequired -and [string]::IsNullOrWhiteSpace($Target)) {
        throw "$Id requires -Target (URL, host, IP or local path)."
    }
    if (@($ModuleArgs | Where-Object { $_ -in @('--authorized','--allow-public') }).Count -gt 0) {
        throw 'Pass -Authorized and -AllowPublic as PowerShell switches, not in -ModuleArgs.'
    }
    $argsList = [System.Collections.Generic.List[string]]::new()
    switch -Wildcard ($engine) {
        'native-network' { return Show-MForceNetwork }
        'native-system' { return Show-MForceSystem }
        'native-update' { return Invoke-MForceUpdate -Root $Root -Arguments $ModuleArgs }
        'osint:*' {
            $argsList.Add($engine.Substring(6)); $argsList.Add($Target)
            foreach ($arg in $ModuleArgs) { $argsList.Add($arg) }
            return Invoke-MForcePython -Root $Root -Script 'src/osint/inspect.py' -Arguments $argsList.ToArray()
        }
        'audit:*' {
            $argsList.Add($engine.Substring(6)); $argsList.Add($Target); $argsList.Add('--authorized')
            if ($AllowPublic) { $argsList.Add('--allow-public') }
            foreach ($arg in $ModuleArgs) { $argsList.Add($arg) }
            return Invoke-MForcePython -Root $Root -Script 'src/offensive/http_audit.py' -Arguments $argsList.ToArray()
        }
        'python:*' {
            if ($Id -in $script:targetRequired) { $argsList.Add($Target) }
            if ($Id -in $script:activeNetwork) {
                $argsList.Add('--authorized')
                if ($AllowPublic) { $argsList.Add('--allow-public') }
            }
            foreach ($arg in $ModuleArgs) { $argsList.Add($arg) }
            return Invoke-MForcePython -Root $Root -Script $engine.Substring(7) -Arguments $argsList.ToArray()
        }
        default { throw "No native mapping for $Id" }
    }
}
function Start-MForceWindowsMenu {
    param([string]$Root, [object[]]$Catalog)
    if ([Console]::IsInputRedirected) { throw 'Interactive menu needs a terminal. Use -List or -Module in scripts.' }
    $groups = @($Catalog | Where-Object Status -eq 'Enabled' | Group-Object Category | Sort-Object Name)
    while ($true) {
        Write-Host ''; Write-Host '  MODULE CATEGORIES' -ForegroundColor Cyan
        for ($i=0; $i -lt $groups.Count; $i++) {
            Write-Host ('  [{0}] {1,-20} ({2})' -f ($i+1),$groups[$i].Name,$groups[$i].Count)
        }
        Write-Host '  [Q] Quit'
        $choice = (Read-Host '  Select category').Trim()
        if ($choice -match '^(?i:q|quit|exit)$') { return }
        $number = 0
        if (-not [int]::TryParse($choice,[ref]$number) -or $number -lt 1 -or $number -gt $groups.Count) {
            Write-Warning 'Invalid category.'; continue
        }
        $selected = @($groups[$number-1].Group)
        while ($true) {
            Write-Host ''; Write-Host ('  {0} / MODULES' -f $groups[$number-1].Name.ToUpperInvariant()) -ForegroundColor Cyan
            for ($i=0; $i -lt $selected.Count; $i++) {
                Write-Host ('  [{0}] {1,-8} {2}' -f ($i+1),$selected[$i].Id,$selected[$i].Name)
            }
            Write-Host '  [B] Back  [Q] Quit'
            $selection = (Read-Host '  Select module').Trim()
            if ($selection -match '^(?i:q|quit|exit)$') { return }
            if ($selection -match '^(?i:b|back)$') { break }
            $index = 0
            if (-not [int]::TryParse($selection,[ref]$index) -or $index -lt 1 -or $index -gt $selected.Count) {
                Write-Warning 'Invalid module.'; continue
            }
            $id = [string]$selected[$index-1].Id
            $target = ''
            if ($id -in $script:targetRequired) {
                $target = (Read-Host '  Target (URL / host / local path)').Trim()
                if ([string]::IsNullOrWhiteSpace($target)) { Write-Warning 'Target required.'; continue }
            }
            $authorized = $false; $allowPublic = $false
            if ($id -in $script:activeNetwork) {
                if ((Read-Host '  Explicit authorization? Type YES').Trim() -cne 'YES') {
                    Write-Warning 'Authorization required.'; continue
                }
                $authorized = $true
                $allowPublic = (Read-Host '  Authorized PUBLIC target? Type YES to allow').Trim() -ceq 'YES'
            }
            try {
                $code = Invoke-MForceWindowsModule -Root $Root -Id $id -Target $target -Authorized:$authorized -AllowPublic:$allowPublic
                Write-Host "  Exit code: $code" -ForegroundColor Gray
            } catch { Write-Warning $_.Exception.Message }
            [void](Read-Host '  Press Enter to return')
        }
    }
}
Export-ModuleMember -Function Show-MForceBanner,Get-MForceCatalog,Get-MForcePython,Test-MForceWindows,Invoke-MForceWindowsModule,Start-MForceWindowsMenu
