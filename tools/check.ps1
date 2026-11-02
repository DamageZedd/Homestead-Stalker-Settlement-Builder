<#
.SYNOPSIS
  Static checks for the Homestead mod (Anomaly 1.5.3 / GAMMA, Lua 5.1 + XML). Not an in-game test.

.DESCRIPTION
  1. Lua syntax + local/upvalue limits   (luac -p, via tools/check_lua.ps1)
  2. luacheck                            (skipped with a message if luacheck is not installed)
  3. XML well-formedness                 (configs + fomod; eng must be ASCII, rus is windows-1251)
  4. Module call resolution              (every stalker_camp_builder.x( / sb.x( has a definition;
                                          also GETGLOBAL of an alias such as `sb` = alias not a local in scope)
  5. Repo hygiene                        (index has LF endings, no luac.out / stray binaries / bytecode)

  Every finding is one stable line "CATEGORY|file|detail". Findings already listed in
  tools/check_baseline.txt are reported as known; anything else is NEW and fails the run.
  Nothing is written into the repo except by -UpdateBaseline. luac output goes to the temp dir only.

  powershell -File tools\check.ps1
  powershell -File tools\check.ps1 -UpdateBaseline     # accept current findings as the baseline
  powershell -File tools\check.ps1 -Skip luacheck,xml

.NOTES
  Exit codes: 0 clean (or only baseline findings), 1 new findings, 2 luac not found.
#>
param(
    [string]$Luac,
    [string]$Luacheck,
    [string[]]$Skip = @(),
    [switch]$UpdateBaseline,
    [switch]$ShowBaseline
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$baselineFile = Join-Path $PSScriptRoot 'check_baseline.txt'
$tmp = Join-Path ([IO.Path]::GetTempPath()) ('homestead_check_' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tmp | Out-Null
$latin1 = [Text.Encoding]::GetEncoding(28591)

$findings = New-Object 'System.Collections.Generic.List[object]'
function Add-Finding($cat, $file, $detail, $extra = '') {
    $findings.Add([pscustomobject]@{ Key = "$cat|$file|$detail"; Extra = $extra })
}
function Rel($p) { $p.Substring($root.Length).TrimStart('\', '/').Replace('\', '/') }
function Section($n) { Write-Host "== $n" }

# ---- tracked files (fall back to a tree walk when not in git) ----------------------------------
Push-Location $root
try {
    $tracked = @(git ls-files) | Where-Object { $_ }
    $haveGit = $LASTEXITCODE -eq 0 -and $tracked.Count -gt 0
} catch { $haveGit = $false }
if (-not $haveGit) {
    $tracked = Get-ChildItem $root -Recurse -File | Where-Object { $_.FullName -notmatch '[\\/]\.git[\\/]' } | ForEach-Object { Rel $_.FullName }
}
$scripts = @($tracked | Where-Object { $_ -like '*.script' })

# ---- locate luac ----------------------------------------------------------------------------------
if (-not $Luac) {
    $cmd = Get-Command luac -ErrorAction SilentlyContinue
    if ($cmd) { $Luac = $cmd.Source }
    elseif (Test-Path 'C:\Program Files (x86)\Lua\5.1\luac.exe') { $Luac = 'C:\Program Files (x86)\Lua\5.1\luac.exe' }
}
if (-not $Luac -or -not (Test-Path $Luac)) {
    Write-Host 'luac (Lua 5.1) not found: pass -Luac <path>.'
    Pop-Location; Remove-Item $tmp -Recurse -Force; exit 2
}

try {
# ---- 1. syntax + limits -------------------------------------------------------------------------------
if ($Skip -notcontains 'luac') {
    Section 'luac syntax and limits'
    $out = & powershell -NoProfile -File (Join-Path $PSScriptRoot 'check_lua.ps1') -Path $root -Luac $Luac 2>&1 | ForEach-Object { "$_" }
    foreach ($l in $out) {
        if ($l -match '^(FAIL|WARN)\s+(\S+)\s+(.*)$') {
            $detail = $Matches[3]
            if ($Matches[1] -eq 'FAIL' -and $detail -notmatch '^syntax:') { $detail = ($detail -replace '\d+', 'N') }
            if ($Matches[1] -eq 'FAIL') { Add-Finding 'LUAC' $Matches[2] $detail }
            else { Write-Host "  note: $l" }
        }
        elseif ($l -match '^Checked ') { Write-Host "  $l" }
    }
}

# ---- 2. luacheck ----------------------------------------------------------------------------------------
if ($Skip -notcontains 'luacheck') {
    Section 'luacheck'
    if (-not $Luacheck) {
        $c = Get-Command luacheck -ErrorAction SilentlyContinue
        if ($c) { $Luacheck = $c.Source }
    }
    if (-not $Luacheck -or -not (Test-Path $Luacheck)) {
        Write-Host '  SKIPPED: luacheck is not installed (luarocks install luacheck, or pass -Luacheck <path>).'
    } else {
        $mods = @($scripts | ForEach-Object { [IO.Path]::GetFileNameWithoutExtension($_) } | Sort-Object -Unique)
        $lcArgs = @('--config', (Join-Path $root '.luacheckrc'), '--formatter', 'plain', '--codes', '--no-color', '--read-globals') + $mods + @('--') + $scripts
        $lc = & $Luacheck @lcArgs 2>&1 | ForEach-Object { "$_" }
        foreach ($l in $lc) {
            # path:line:col: (Wcode) message
            if ($l -match '^(.+?):(\d+):(\d+): \((\w+)\) (.*)$') {
                $f = ($Matches[1] -replace '\\', '/')
                Add-Finding 'LUACHECK' $f "$($Matches[4]) $($Matches[5])" "line $($Matches[2])"
            }
        }
    }
}

# ---- 3. XML -----------------------------------------------------------------------------------------------
if ($Skip -notcontains 'xml') {
    Section 'XML well-formedness'
    $xmls = @($tracked | Where-Object { $_ -like '*.xml' -and ($_ -like '*/configs/*' -or $_ -like 'fomod/*') })
    foreach ($x in $xmls) {
        $path = Join-Path $root $x
        $bytes = [IO.File]::ReadAllBytes($path)
        if ($x -match '/text/eng/' -and ($bytes | Where-Object { $_ -gt 127 } | Select-Object -First 1)) {
            Add-Finding 'XML_ENG_NON_ASCII' $x 'eng XML contains non-ASCII bytes'
        }
        $enc = ''
        if ($latin1.GetString($bytes, 0, [Math]::Min(200, $bytes.Length)) -match 'encoding\s*=\s*"([^"]+)"') { $enc = $Matches[1].ToLower() }
        if ($x -match '/text/rus/' -and $enc -ne 'windows-1251') {
            Add-Finding 'XML_RUS_ENCODING' $x "rus XML declares encoding '$enc', expected windows-1251"
        }
        if ($latin1.GetString($bytes).TrimStart() -match '^#include') { continue }   # X-Ray preprocessor stub, not XML
        try {
            $doc = New-Object Xml.XmlDocument
            $doc.Load($path)          # honours the declared encoding (windows-1251 for rus)
        } catch {
            # X-Ray UI/texture XML often has several top-level elements; accept those wrapped in a dummy root.
            $ok = $false
            if ($_.Exception.Message -match 'multiple root|Root element is missing|There are multiple root') {
                try {
                    $txt = $latin1.GetString($bytes) -replace '^\s*<\?xml[^>]*\?>', ''
                    $d2 = New-Object Xml.XmlDocument
                    $d2.LoadXml("<r>$txt</r>"); $ok = $true
                } catch { $err = $_.Exception.Message }
            } else { $err = $_.Exception.Message }
            if (-not $ok) { Add-Finding 'XML_MALFORMED' $x ($err -replace '\s+', ' ') }
        }
    }
    Write-Host "  Parsed $($xmls.Count) XML file(s)."
}

# ---- 4. module call resolution --------------------------------------------------------------------------
if ($Skip -notcontains 'calls') {
    Section 'module call resolution (stalker_camp_builder.x( / sb.x( ...)'
    $mods = @{}      # module name -> script path
    foreach ($s in $scripts) { $mods[[IO.Path]::GetFileNameWithoutExtension($s)] = $s }
    $defs = @{}      # module -> set of defined names
    $calls = New-Object 'System.Collections.Generic.List[object]'
    $guardedSeen = @{}
    $aliasGlobals = New-Object 'System.Collections.Generic.List[object]'

    foreach ($s in $scripts) {
        $t = $latin1.GetString([IO.File]::ReadAllBytes((Join-Path $root $s)))
        $t = [regex]::Replace($t, '--\[(=*)\[.*?\]\1\]', { param($m) ([regex]::Matches($m.Value, "`n") | ForEach-Object { "`n" }) -join '' }, 'Singleline')
        $lines = $t -split "`r?`n"
        for ($i = 0; $i -lt $lines.Count; $i++) { $lines[$i] = $lines[$i] -replace '--.*$', '' }
        $self = [IO.Path]::GetFileNameWithoutExtension($s)
        # aliases: name -> module (this file only)
        $alias = @{}
        foreach ($l in $lines) {
            if ($l -match '^\s*local\s+([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*)\s*$' -and $mods.ContainsKey($Matches[2]) -and $Matches[1] -ne '_') {
                $alias[$Matches[1]] = $Matches[2]
            }
        }
        # top-level `function name(` / `name = ...` in a script file are members of that module (Anomaly loads scripts as modules)
        foreach ($l in $lines) {
            if ($l -match '^\s*function\s+([A-Za-z_]\w*)\s*\(' -or $l -match '^([A-Za-z_]\w*)\s*=(?!=)') {
                if (-not $defs.ContainsKey($self)) { $defs[$self] = @{} }
                $defs[$self][$Matches[1]] = $true
            }
        }
        $names = @{}; foreach ($m in $mods.Keys) { $names[$m] = $m }; foreach ($a in $alias.Keys) { $names[$a] = $alias[$a] }
        $rx = '\b(' + (($names.Keys | ForEach-Object { [regex]::Escape($_) }) -join '|') + ')\.([A-Za-z_]\w*)\s*(\(|=(?!=))?'
        for ($i = 0; $i -lt $lines.Count; $i++) {
            $l = $lines[$i]
            foreach ($m in [regex]::Matches($l, $rx)) {
                # skip `x.name` preceded by `.` or `:` (field of something else)
                if ($m.Index -gt 0 -and $l[$m.Index - 1] -in '.', ':') { continue }
                $mod = $names[$m.Groups[1].Value]; $n = $m.Groups[2].Value; $tail = $m.Groups[3].Value
                $isDefFn = $l.Substring(0, $m.Index) -match 'function\s+$'
                if ($isDefFn -or $tail -eq '=') {
                    if (-not $defs.ContainsKey($mod)) { $defs[$mod] = @{} }
                    $defs[$mod][$n] = $true
                } elseif ($tail -eq '(') {
                    # `x.f and x.f(...)` is a feature probe; an undefined f there is dead, not a crash
                    $probe = $m.Groups[1].Value + '.' + $n
                    if ($l -match ([regex]::Escape($probe) + '\s+and\s+' + [regex]::Escape($probe) + '\s*\(')) {
                        $guardedSeen["$mod.$n"] = "$s`:$($i + 1)"; continue
                    }
                    $calls.Add([pscustomobject]@{ Mod = $mod; Name = $n; File = $s; Line = $i + 1; Via = $m.Groups[1].Value })
                }
            }
        }
        # file-level: own top-level functions defined as `function name(` are not module members; ignored.
        if ($alias.Count -gt 0) {
            $script:aliasByFile = $null
        }
        $fileAliases = @($alias.Keys | Where-Object { $_ -ne $self })
        foreach ($a in $fileAliases) { $aliasGlobals.Add([pscustomobject]@{ File = $s; Alias = $a }) }
    }
    $seen = @{}
    foreach ($c in $calls) {
        if ($defs.ContainsKey($c.Mod) -and $defs[$c.Mod].ContainsKey($c.Name)) { continue }
        $k = "$($c.Mod)|$($c.File)|$($c.Name)"
        if ($seen.ContainsKey($k)) { continue }; $seen[$k] = $true
        Add-Finding 'UNRESOLVED_CALL' $c.File "$($c.Mod).$($c.Name)" "line $($c.Line), via $($c.Via)"
    }

    # alias used where it is not a local: GETGLOBAL <alias> in luac -l means the alias is global at that point.
    foreach ($g in ($aliasGlobals | Group-Object File)) {
        $aliasNames = @($g.Group.Alias | Sort-Object -Unique)
        $hdr = ''
        $listing = & $Luac -l -p (Join-Path $root $g.Name) 2>&1
        $hit = @{}
        foreach ($line in $listing) {
            $line = "$line"
            if ($line -match '^(main|function) <[^:]*:(\d+),') { $hdr = $Matches[2] }
            elseif ($line -match '^\s*\d+\s+\[(\d+)\]\s+GETGLOBAL\s+\d+\s+-?\d+\s*; (\w+)\s*$' -and $aliasNames -contains $Matches[2]) {
                $k = $Matches[2]
                if (-not $hit.ContainsKey($k)) { $hit[$k] = "line $($Matches[1]), function at line $hdr" }
            }
        }
        foreach ($k in $hit.Keys) { Add-Finding 'ALIAS_NOT_LOCAL' $g.Name "$k used as a global (not a local in that function's scope)" $hit[$k] }
    }
    # the same, for files that use `sb.` but never declare any alias at all
    foreach ($s in $scripts) {
        if ($aliasGlobals | Where-Object { $_.File -eq $s -and $_.Alias -eq 'sb' }) { continue }
        $listing = & $Luac -l -p (Join-Path $root $s) 2>&1
        foreach ($line in $listing) {
            if ("$line" -match '^\s*\d+\s+\[(\d+)\]\s+GETGLOBAL\s+\d+\s+-?\d+\s*; sb\s*$') {
                Add-Finding 'ALIAS_NOT_LOCAL' $s "sb used as a global but no 'local sb = <module>' exists in the file" "line $($Matches[1])"
                break
            }
        }
    }
    foreach ($g in $guardedSeen.Keys) {
        if (-not ($defs.ContainsKey(($g -split '\.')[0]) -and $defs[($g -split '\.')[0]].ContainsKey(($g -split '\.', 2)[1]))) {
            Write-Host "  note: guarded probe of undefined $g (first at $($guardedSeen[$g])) - feature never active"
        }
    }
    Write-Host "  $($calls.Count) module call(s) across $($scripts.Count) script(s)."
}

# ---- 5. hygiene ---------------------------------------------------------------------------------------------
if ($Skip -notcontains 'hygiene') {
    Section 'line endings and stray binaries'
    if ($haveGit) {
        # index side: CRLF in the working tree is just core.autocrlf; CRLF in the index is a real finding.
        foreach ($l in (git ls-files --eol)) {
            if ($l -match '^i/(\S+)\s+w/\S+\s+attr/\S*\s+(.+)$' -and $Matches[1] -in 'crlf', 'mixed') {
                Add-Finding 'EOL_NOT_LF' $Matches[2] "index line endings are $($Matches[1])"
            }
        }
    } else { Write-Host '  not a git checkout: line-ending check skipped.' }
    $binRx = '(^|/)luac\.out$|\.(out|exe|dll|so|dylib|obj|o|luac|pyc|class)$'
    foreach ($f in $tracked) { if ($f -match $binRx) { Add-Finding 'STRAY_BINARY' $f 'tracked file looks like a build artifact' } }
    Get-ChildItem $root -Recurse -File -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ieq 'luac.out' -and $_.FullName -notmatch '[\\/]\.git[\\/]' } |
        ForEach-Object { Add-Finding 'STRAY_BINARY' (Rel $_.FullName) 'luac.out present in the working tree' }
    foreach ($s in $scripts) {
        $fs = [IO.File]::OpenRead((Join-Path $root $s)); $b = New-Object byte[] 4; [void]$fs.Read($b, 0, 4); $fs.Dispose()
        if ($b[0] -eq 0x1B -and $b[1] -eq 0x4C) { Add-Finding 'STRAY_BINARY' $s 'script is compiled Lua bytecode' }
    }
}
} finally {
    Pop-Location
    Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
}

# ---- baseline + report ------------------------------------------------------------------------------------
$keys = @($findings | ForEach-Object { $_.Key } | Sort-Object -Unique)
if ($UpdateBaseline) {
    $hdr = '# Known pre-existing findings from tools/check.ps1. Format: CATEGORY|file|detail. Regenerate: tools\check.ps1 -UpdateBaseline'
    $body = (@($hdr) + $keys) -join "`n"
    [IO.File]::WriteAllText($baselineFile, $body + "`n", (New-Object Text.UTF8Encoding $false))
    Write-Host "Baseline written: $($keys.Count) finding(s) -> tools/check_baseline.txt"
    exit 0
}
$base = @{}
if (Test-Path $baselineFile) {
    foreach ($l in [IO.File]::ReadAllLines($baselineFile)) { if ($l -and -not $l.StartsWith('#')) { $base[$l.TrimEnd()] = $true } }
}
$new = @($findings | Where-Object { -not $base.ContainsKey($_.Key) } | Sort-Object Key -Unique)
$known = @($findings | Where-Object { $base.ContainsKey($_.Key) } | Sort-Object Key -Unique)
$fixed = @($base.Keys | Where-Object { $keys -notcontains $_ })

Write-Host ''
if ($ShowBaseline) { foreach ($k in $known) { Write-Host "known  $($k.Key)  [$($k.Extra)]" } }
foreach ($f in $new) { Write-Host "NEW    $($f.Key)  [$($f.Extra)]" }
foreach ($k in $fixed) { Write-Host "gone   $k  (no longer reported; remove from baseline)" }
Write-Host ("{0} new, {1} known (baseline), {2} resolved since baseline." -f $new.Count, $known.Count, $fixed.Count)
Write-Host 'Static checks only: this does not verify in-game behaviour.'
if ($new.Count -gt 0) { exit 1 }
exit 0
