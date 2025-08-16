# =============================================================================
# TYPOGRAPHY REGEX FALLBACK - PowerShell Implementation
# =============================================================================
# 
# Alternative zu Node.js Codemod für Windows-Systeme ohne Node.js
# Basiert auf ripgrep/sed Äquivalenten in PowerShell

param(
    [Parameter(Mandatory=$true)]
    [string]$Directory,
    
    [switch]$DryRun,
    [switch]$Verbose,
    [string[]]$Extensions = @('.py', '.js', '.jsx', '.ts', '.tsx', '.css', '.html')
)

# =============================================================================
# TYPOGRAPHY MAPPING CONFIGURATION
# =============================================================================

$TypographyMapping = @{
    # Button Typography -> body_bold
    'button_lg' = 'body_bold'
    'button_md' = 'body_bold'
    'button' = 'body_bold'
    'button_sm' = 'body_bold'
    
    # Heading Hierarchy Simplification
    'heading_lg' = 'heading'
    'heading_md' = 'subheading'
    'heading_sm' = 'subheading'
    
    # Body Text Consolidation
    'body_sm' = 'body'
    'body_lg' = 'body_bold'
    'body_md' = 'body'
    
    # Label Consolidation
    'label_bold' = 'body_bold'
    'label' = 'body'
    'label_sm' = 'caption'
    'label_lg' = 'body_bold'
    
    # Caption Variants
    'caption_sm' = 'caption'
    'caption_lg' = 'caption'
    'small' = 'caption'
    'small_normal' = 'caption'
    
    # Title Variants
    'title_lg' = 'title'
    'title_md' = 'title'
    'display' = 'title'
    'display_lg' = 'title'
    
    # Misc Variants
    'menu' = 'caption'
    'status' = 'caption'
    'metric_value' = 'heading'
    'code' = 'body'
}

# =============================================================================
# REPLACEMENT PATTERNS
# =============================================================================

$Patterns = @{
    # Python get_typography() Calls
    PythonGetTypography = "get_typography\('([^']+)'\)"
    PythonGetTypographyDouble = 'get_typography\("([^"]+)"\)'
    
    # CSS Classes
    CssClasses = '\.ty-([a-zA-Z_-]+)'
    
    # HTML Classes
    HtmlClasses = 'class(?:Name)?=[''"]([^''"]*\bty-[a-zA-Z_-]+[^''"]*)[''""]'
    
    # JavaScript fontSize
    JsFontSize = "fontSize:\s*[''\""]([^''\""]+)[''\""]"
    
    # React Props
    ReactProps = "typography=[''\""]([^''\""]+)[''\""]"
}

# =============================================================================
# FUNCTIONS
# =============================================================================

function Write-Status {
    param([string]$Message, [string]$Type = "Info")
    
    $color = switch ($Type) {
        "Success" { "Green" }
        "Warning" { "Yellow" }
        "Error" { "Red" }
        default { "Cyan" }
    }
    
    Write-Host $Message -ForegroundColor $color
}

function Get-AllFiles {
    param([string]$Path, [string[]]$Extensions)
    
    $excludeDirs = @('node_modules', '.git', '.vscode', '__pycache__', 'dist', 'build')
    
    Get-ChildItem -Path $Path -Recurse -File | 
        Where-Object { 
            $_.Extension -in $Extensions -and 
            -not ($_.Directory.Name -in $excludeDirs)
        }
}

function Replace-Typography {
    param(
        [string]$Content,
        [string]$Pattern,
        [hashtable]$Mapping,
        [string]$FilePath,
        [ref]$ChangesFound
    )
    
    $newContent = $Content
    $regex = [regex]::new($Pattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    
    $newContent = $regex.Replace($Content, {
        param($match)
        
        $oldTypography = $match.Groups[1].Value
        $newTypography = $Mapping[$oldTypography]
        
        if ($newTypography -and $newTypography -ne $oldTypography) {
            $ChangesFound.Value++
            
            if ($Verbose) {
                Write-Status "  $oldTypography → $newTypography" "Success"
            }
            
            # Replace based on pattern type
            if ($Pattern -match "get_typography") {
                return "get_typography('$newTypography')"
            }
            elseif ($Pattern -match "fontSize") {
                return "fontSize: '$newTypography'"
            }
            elseif ($Pattern -match "typography=") {
                return "typography=`"$newTypography`""
            }
            elseif ($Pattern -match "\.ty-") {
                return ".ty-$newTypography"
            }
            else {
                return $match.Value.Replace($oldTypography, $newTypography)
            }
        }
        
        return $match.Value
    })
    
    return $newContent
}

function Process-File {
    param(
        [System.IO.FileInfo]$File,
        [hashtable]$Mapping,
        [hashtable]$Patterns,
        [bool]$DryRun,
        [bool]$Verbose
    )
    
    try {
        $content = Get-Content -Path $File.FullName -Raw -ErrorAction Stop
        $originalContent = $content
        $fileChanges = 0
        
        # Apply all relevant patterns based on file extension
        switch ($File.Extension) {
            '.py' {
                $content = Replace-Typography $content $Patterns.PythonGetTypography $Mapping $File.FullName ([ref]$fileChanges)
                $content = Replace-Typography $content $Patterns.PythonGetTypographyDouble $Mapping $File.FullName ([ref]$fileChanges)
            }
            {$_ -in @('.js', '.jsx', '.ts', '.tsx')} {
                $content = Replace-Typography $content $Patterns.JsFontSize $Mapping $File.FullName ([ref]$fileChanges)
                $content = Replace-Typography $content $Patterns.ReactProps $Mapping $File.FullName ([ref]$fileChanges)
            }
            '.css' {
                $content = Replace-Typography $content $Patterns.CssClasses $Mapping $File.FullName ([ref]$fileChanges)
            }
            '.html' {
                $content = Replace-Typography $content $Patterns.HtmlClasses $Mapping $File.FullName ([ref]$fileChanges)
            }
        }
        
        # Write changes if content changed
        if ($content -ne $originalContent) {
            if (-not $DryRun) {
                Set-Content -Path $File.FullName -Value $content -NoNewline
            }
            
            if ($Verbose) {
                Write-Status "✅ Modified: $($File.Name)" "Success"
            }
            
            return @{
                Modified = $true
                Changes = $fileChanges
                File = $File.FullName
            }
        }
        
        return @{
            Modified = $false
            Changes = 0
            File = $File.FullName
        }
        
    } catch {
        Write-Status "❌ Error processing $($File.Name): $($_.Exception.Message)" "Error"
        return @{
            Modified = $false
            Changes = 0
            File = $File.FullName
            Error = $_.Exception.Message
        }
    }
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

function Main {
    Write-Status "🚀 Typography Regex Fallback - PowerShell Implementation" "Info"
    Write-Status "📁 Directory: $Directory" "Info"
    Write-Status "🎯 Mode: $(if ($DryRun) { 'DRY RUN' } else { 'LIVE RUN' })" "Info"
    Write-Status "📝 Extensions: $($Extensions -join ', ')" "Info"
    Write-Status ""
    
    # Validate directory
    if (-not (Test-Path $Directory)) {
        Write-Status "❌ Directory does not exist: $Directory" "Error"
        exit 1
    }
    
    # Get all files
    $files = Get-AllFiles -Path $Directory -Extensions $Extensions
    Write-Status "📄 Found $($files.Count) files to process" "Info"
    Write-Status ""
    
    # Process files
    $results = @()
    $totalChanges = 0
    $modifiedFiles = 0
    
    foreach ($file in $files) {
        if ($Verbose) {
            Write-Status "Processing: $($file.Name)" "Info"
        }
        
        $result = Process-File -File $file -Mapping $TypographyMapping -Patterns $Patterns -DryRun $DryRun -Verbose $Verbose
        $results += $result
        
        if ($result.Modified) {
            $modifiedFiles++
            $totalChanges += $result.Changes
        }
    }
    
    # Generate report
    Write-Status ""
    Write-Status "🎯 Typography Refactoring Report" "Info"
    Write-Status "=" * 50 "Info"
    Write-Status ""
    Write-Status "📊 Summary:" "Info"
    Write-Status "  Mode: $(if ($DryRun) { 'DRY RUN' } else { 'LIVE RUN' })" "Info"
    Write-Status "  Files Processed: $($files.Count)" "Info"
    Write-Status "  Files Modified: $modifiedFiles" "Info"
    Write-Status "  Total Changes: $totalChanges" "Info"
    Write-Status "  Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "Info"
    Write-Status ""
    
    # Show mapping
    Write-Status "📝 Typography Mappings Applied:" "Info"
    foreach ($mapping in $TypographyMapping.GetEnumerator()) {
        Write-Status "  $($mapping.Key) → $($mapping.Value)" "Success"
    }
    Write-Status ""
    
    # Show modified files
    $modifiedResults = $results | Where-Object { $_.Modified }
    if ($modifiedResults.Count -gt 0) {
        Write-Status "📄 Modified Files:" "Info"
        foreach ($result in $modifiedResults) {
            $fileName = Split-Path $result.File -Leaf
            Write-Status "  ✅ $fileName ($($result.Changes) changes)" "Success"
        }
    } else {
        Write-Status "✅ No changes needed - all typography is already up to date!" "Success"
    }
    
    # Show errors if any
    $errorResults = $results | Where-Object { $_.Error }
    if ($errorResults.Count -gt 0) {
        Write-Status ""
        Write-Status "❌ Errors:" "Error"
        foreach ($result in $errorResults) {
            $fileName = Split-Path $result.File -Leaf
            Write-Status "  ❌ $fileName`: $($result.Error)" "Error"
        }
    }
    
    Write-Status ""
    Write-Status "=" * 50 "Info"
    
    # Save detailed report
    $reportPath = "typography-refactor-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $reportData = @{
        summary = @{
            mode = if ($DryRun) { 'DRY RUN' } else { 'LIVE RUN' }
            filesProcessed = $files.Count
            filesModified = $modifiedFiles
            totalChanges = $totalChanges
            timestamp = Get-Date -Format 'yyyy-MM-ddTHH:mm:ss'
        }
        mapping = $TypographyMapping
        results = $results
    }
    
    $reportData | ConvertTo-Json -Depth 3 | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Status "📋 Detailed report saved: $reportPath" "Info"
}

# =============================================================================
# USAGE INFORMATION
# =============================================================================

function Show-Usage {
    Write-Host @"
📝 Typography Regex Fallback - PowerShell Implementation

Usage:
  .\typography-refactor.ps1 -Directory <path> [options]

Parameters:
  -Directory <path>     Target directory to process (required)
  -DryRun              Run without making changes (default: false)
  -Verbose             Show detailed output (default: false)
  -Extensions <array>   File extensions to process (default: .py,.js,.jsx,.ts,.tsx,.css,.html)

Examples:
  .\typography-refactor.ps1 -Directory .\src -DryRun
  .\typography-refactor.ps1 -Directory .\src -Verbose
  .\typography-refactor.ps1 -Directory .\src -Extensions @('.py', '.js')

Typography Mappings:
"@

    foreach ($mapping in $TypographyMapping.GetEnumerator()) {
        Write-Host "  $($mapping.Key) → $($mapping.Value)" -ForegroundColor Green
    }
}

# Execute main function
if ($args -contains '-help' -or $args -contains '--help' -or $args -contains '-h') {
    Show-Usage
} else {
    Main
}
