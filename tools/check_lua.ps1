<#
.SYNOPSIS
  Lua 5.1 syntax + limit check for every .script/.lua file in the repo.

.DESCRIPTION
  Anomaly runs Lua 5.1, which has hard limits that a plain syntax check does not catch:
    - 200 local variables per function (a script that crosses it fails to load)
    - 60 upvalues per function
  This runs `luac -p` on each file, then reads `luac -l -l` and reports the highest
  locals/upvalues of any function. Exit code 1 on a syntax error or a FAIL threshold.

.PARAMETER Path
  Folder or file to check (default: the repo root, one level above this script).
.PARAMETER Luac
  Path to a Lua 5.1 luac. Default: luac on PATH, then C:\Program Files (x86)\Lua\5.1\luac.exe.

  powershell -File tools\check_lua.ps1
  powershell -File tools\check_lua.ps1 -Path 00_Core\gamedata\scripts
#>
param(
    [string]$Path = (Join-Path $PSScriptRoot '..'),
    [string]$Luac,
    [int]$LocalsWarn = 150, [int]$LocalsFail = 180,
    [int]$UpvalsWarn = 50,  [int]$UpvalsFail = 56
)

if (-not $Luac) {
    $cmd = Get-Command luac -ErrorAction SilentlyContinue
    if ($cmd) { $Luac = $cmd.Source }
    elseif (Test-Path 'C:\Program Files (x86)\Lua\5.1\luac.exe') { $Luac = 'C:\Program Files (x86)\Lua\5.1\luac.exe' }
}
if (-not $Luac -or -not (Test-Path $Luac)) {
    Write-Host 'luac (Lua 5.1) not found: syntax and limit checks could not run. Pass -Luac <path>.'
    exit 2
}
$ver = (& $Luac -v 2>&1 | Out-String).Trim()
if ($ver -notmatch 'Lua 5\.1') { Write-Host "WARNING: $ver is not Lua 5.1; results may not match Anomaly." }

$root = (Resolve-Path $Path).Path
$files = if ((Get-Item $root).PSIsContainer) {
    Get-ChildItem $root -Recurse -File | Where-Object { $_.Extension -in '.script', '.lua' }
} else { Get-Item $root }

$bad = 0; $warn = 0; $n = 0
foreach ($f in $files) {
    $n++
    $rel = $f.FullName.Substring($root.Length).TrimStart('\', '/')
    $err = & $Luac -p $f.FullName 2>&1
    if ($LASTEXITCODE -ne 0) { Write-Host "FAIL  $rel  syntax: $err"; $bad++; continue }

    $maxL = 0; $maxU = 0; $locHdr = ''; $upHdr = ''; $hdr = ''
    foreach ($line in (& $Luac -l -l -o NUL $f.FullName)) {
        if ($line -match '^(main|function) <.*:(\d+),\d+>') { $hdr = if ($line -match '^main') { 'main chunk' } else { "line $($Matches[2])" } }
        elseif ($line -match '(\d+) upvalues?, (\d+) locals?') {
            $u = [int]$Matches[1]; $l = [int]$Matches[2]
            if ($l -gt $maxL) { $maxL = $l; $locHdr = $hdr }
            if ($u -gt $maxU) { $maxU = $u; $upHdr = $hdr }
        }
    }
    $status = 'ok  '
    if ($maxL -ge $LocalsFail -or $maxU -ge $UpvalsFail) { $status = 'FAIL'; $bad++ }
    elseif ($maxL -ge $LocalsWarn -or $maxU -ge $UpvalsWarn) { $status = 'WARN'; $warn++ }
    if ($status -ne 'ok  ') {
        Write-Host ("{0}  {1}  locals {2} ({3}, limit 200)  upvalues {4} ({5}, limit 60)" -f $status, $rel, $maxL, $locHdr, $maxU, $upHdr)
    }
}
Write-Host "Checked $n file(s) with $ver : $bad failure(s), $warn warning(s)."
if ($bad -gt 0) { exit 1 }
