# =============================================================================
# DRY RUN REPORT - Typography System Migration Analysis
# =============================================================================
# 
# Automatische Analyse der Translation Quality GUI für Typography-Migration
# Erstellt einen umfassenden Report ohne Änderungen zu machen

param(
    [Parameter(Mandatory=$true)]
    [string]$Directory
)

# =============================================================================
# ANALYSIS CONFIGURATION
# =============================================================================

$TypographyMapping = @{
    'button_lg' = 'body_bold'
    'button_md' = 'body_bold'
    'button' = 'body_bold'
    'heading_lg' = 'heading'
    'heading_md' = 'subheading'
    'heading_sm' = 'subheading'
    'body_sm' = 'body'
    'body_lg' = 'body_bold'
    'label_bold' = 'body_bold'
    'label' = 'body'
    'small' = 'caption'
    'menu' = 'caption'
    'status' = 'caption'
}

$SearchPatterns = @(
    "get_typography\('([^']+)'\)",
    'get_typography\("([^"]+)"\)',
    "\.ty-([a-zA-Z_-]+)",
    "fontSize:\s*[''\""]([^''\""]+)[''\""]",
    "typography=[''\""]([^''\""]+)[''\""]"
)

# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

function Find-TypographyUsage {
    param([string]$Path)

    $findings = @()
    $files = Get-ChildItem -Path $Path -Recurse -File -Include *.py, *.js, *.jsx, *.ts, *.tsx, *.css, *.html \
        | Where-Object { $_.Name -notmatch 'backup|\.bak$|\.old$|\.orig$' }
    # ⏭️  Backup/temporäre Dateien werden ignoriert, damit Legacy-Tokens in historischen Snapshots den CI nicht blockieren.

    foreach ($file in $files) {
        $content = Get-Content -Path $file.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }

        foreach ($pattern in $SearchPatterns) {
            $matches = [regex]::Matches($content, $pattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)

            foreach ($match in $matches) {
                $typographyName = $match.Groups[1].Value
                $hasMapping = $TypographyMapping.ContainsKey($typographyName)
                $mapped = if ($hasMapping) { $TypographyMapping[$typographyName] } else { $typographyName }

                $findings += @{
                    File         = $file.FullName
                    FileName     = $file.Name
                    Extension    = $file.Extension
                    LineNumber   = ($content.Substring(0, $match.Index) -split "`n").Count
                    OldTypography= $typographyName
                    NewTypography= $mapped
                    NeedsChange  = [bool]$hasMapping
                    FullMatch    = $match.Value
                    Pattern      = $pattern
                    Context      = $content.Substring([Math]::Max(0, $match.Index - 50), [Math]::Min(100, $content.Length - [Math]::Max(0, $match.Index - 50)))
                }
            }
        }
    }

    return $findings
}

function Generate-MigrationReport {
    param([array]$Findings)
    
    Write-Host "🎯 Typography Migration Analysis Report" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host ""
    
    # Summary Statistics
    $totalFindings = $Findings.Count
    $changesNeeded = ($Findings | Where-Object { $_.NeedsChange }).Count
    $filesAffected = ($Findings | Select-Object File -Unique).Count
    $filesByExt = $Findings | Group-Object Extension
    
    Write-Host "📊 Summary Statistics:" -ForegroundColor Yellow
    Write-Host "  Total Typography Usages Found: $totalFindings" -ForegroundColor White
    Write-Host "  Changes Needed: $changesNeeded" -ForegroundColor White
    Write-Host "  Files Affected: $filesAffected" -ForegroundColor White
    Write-Host "  Directory: $Directory" -ForegroundColor White
    Write-Host "  Analysis Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
    Write-Host ""
    
    # Files by Extension
    Write-Host "📄 Files by Extension:" -ForegroundColor Yellow
    foreach ($group in $filesByExt) {
        $changesInExt = ($group.Group | Where-Object { $_.NeedsChange }).Count
        Write-Host "  $($group.Name): $($group.Count) usages ($changesInExt changes needed)" -ForegroundColor White
    }
    Write-Host ""
    
    # Typography Mapping Overview
    Write-Host "📝 Typography Mapping Overview:" -ForegroundColor Yellow
    $changeCounts = @{}
    foreach ($finding in $Findings | Where-Object { $_.NeedsChange }) {
        $key = "$($finding.OldTypography) → $($finding.NewTypography)"
        if (-not $changeCounts.ContainsKey($key)) { $changeCounts[$key] = 0 }
        $changeCounts[$key] = $changeCounts[$key] + 1
    }
    
    foreach ($change in $changeCounts.GetEnumerator() | Sort-Object Value -Descending) {
        Write-Host "  $($change.Key): $($change.Value) occurrences" -ForegroundColor Green
    }
    Write-Host ""
    
    # Files Requiring Changes
    $filesNeedingChanges = $Findings | Where-Object { $_.NeedsChange } | Group-Object File
    if ($filesNeedingChanges.Count -gt 0) {
        Write-Host "📁 Files Requiring Changes:" -ForegroundColor Yellow
        foreach ($fileGroup in $filesNeedingChanges) {
            $fileName = Split-Path $fileGroup.Name -Leaf
            Write-Host "  ✏️  $fileName ($($fileGroup.Count) changes)" -ForegroundColor Red
            
            # Show specific changes for this file
            foreach ($change in $fileGroup.Group) {
                Write-Host "    Line $($change.LineNumber): $($change.OldTypography) → $($change.NewTypography)" -ForegroundColor Magenta
            }
        }
        Write-Host ""
    }
    
    # Files Already Up-to-Date
    $upToDateUsages = $Findings | Where-Object { -not $_.NeedsChange } | Group-Object File
    if ($upToDateUsages.Count -gt 0) {
        Write-Host "✅ Files Already Using Current Typography:" -ForegroundColor Green
        foreach ($fileGroup in $upToDateUsages) {
            $fileName = Split-Path $fileGroup.Name -Leaf
            $uniqueTypos = $fileGroup.Group | Select-Object OldTypography -Unique
            Write-Host "  ✅ $fileName ($($uniqueTypos.Count) typography types)" -ForegroundColor Green
        }
        Write-Host ""
    }
    
    # Migration Priority
    Write-Host "🎯 Migration Priority:" -ForegroundColor Yellow
    $priorityOrder = @('button_lg', 'button_md', 'heading_lg', 'body_lg', 'label_bold')
    foreach ($priority in $priorityOrder) {
        $count = ($Findings | Where-Object { $_.OldTypography -eq $priority -and $_.NeedsChange }).Count
        if ($count -gt 0) {
            $newName = $TypographyMapping[$priority]
            Write-Host "  🔥 HIGH: $priority → $newName ($count occurrences)" -ForegroundColor Red
        }
    }
    Write-Host ""
    
    # Command Suggestions
    Write-Host "🚀 Recommended Commands:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Node.js Codemod (Recommended):" -ForegroundColor Cyan
    Write-Host "  node typography-codemod.js `"$Directory`" --dry-run" -ForegroundColor White
    Write-Host "  node typography-codemod.js `"$Directory`" --verbose" -ForegroundColor White
    Write-Host ""
    Write-Host "PowerShell Alternative:" -ForegroundColor Cyan
    Write-Host "  .\typography-refactor.ps1 -Directory `"$Directory`" -DryRun" -ForegroundColor White
    Write-Host "  .\typography-refactor.ps1 -Directory `"$Directory`" -Verbose" -ForegroundColor White
    Write-Host ""
    
    # Detailed Findings Export
    $reportPath = "typography-analysis-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $reportData = @{
        summary = @{
            totalFindings = $totalFindings
            changesNeeded = $changesNeeded
            filesAffected = $filesAffected
            directory = $Directory
            timestamp = Get-Date -Format 'yyyy-MM-ddTHH:mm:ss'
        }
        mapping = $TypographyMapping
        findings = $Findings
        filesByExtension = $filesByExt | ForEach-Object { @{ extension = $_.Name; count = $_.Count } }
        changesRequired = $changeCounts
        legacy = $global:LegacyTypographySummary
    }
    
    $reportData | ConvertTo-Json -Depth 4 | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Host "📋 Detailed analysis saved: $reportPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Cyan
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if (-not (Test-Path $Directory)) {
    Write-Host "❌ Directory does not exist: $Directory" -ForegroundColor Red
    exit 1
}

Write-Host "🔍 Analyzing Typography Usage in: $Directory" -ForegroundColor Cyan
Write-Host "⏳ Scanning files..." -ForegroundColor Yellow

$findings = Find-TypographyUsage -Path $Directory
<#
  Legacy-Erkennung: Verbannte / alte Tokens, die vollständig entfernt werden sollen.
  Enthält: frühere Variants (micro_bold, caption_bold, metric_value, input) + redundante heading_* Größen.
#>
$legacyTokens = @('micro_bold','caption_bold','metric_value','input','heading_lg','heading_xl','title_lg','title_xl')
$legacyFindings = $findings | Where-Object { $legacyTokens -contains $_.OldTypography }
$legacyCount = $legacyFindings.Count

$global:LegacyTypographySummary = @{
    legacyTokens = $legacyTokens
    legacyCount  = $legacyCount
    legacyFiles  = ($legacyFindings | Select-Object -Expand File -Unique)
}

if ($legacyCount -gt 0) {
    Write-Host "❌ Legacy Typography Usages Detected: $legacyCount" -ForegroundColor Red
    foreach ($g in ($legacyFindings | Group-Object File)) {
        $short = Split-Path $g.Name -Leaf
        $types = ($g.Group | Select-Object -Expand OldTypography -Unique) -join ', '
        Write-Host "  • $short → $types" -ForegroundColor DarkYellow
    }
    Write-Host "⚠️  CI will fail (exit 2) until legacy tokens entfernt sind." -ForegroundColor Yellow
}

Generate-MigrationReport -Findings $findings

if ($legacyCount -gt 0) {
    Write-Host "⛔ Exiting with code 2 due to legacy typography" -ForegroundColor Red
    exit 2
}

Write-Host "✅ Analysis complete (no legacy tokens)." -ForegroundColor Green
