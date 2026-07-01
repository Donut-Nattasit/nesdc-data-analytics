param(
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$required = @(
    "AGENTS.md",
    "CLAUDE.md",
    ".claude\agents",
    ".claude\commands",
    ".claude\skills",
    ".codex\README.md",
    ".codex\CLAUDE_COMPATIBILITY.md",
    ".codex\instructions.md",
    ".codex\agents\README.md",
    ".codex\commands\README.md",
    ".codex\skills\README.md"
)

$missing = @()
foreach ($path in $required) {
    $fullPath = Join-Path $root $path
    if (-not (Test-Path $fullPath)) {
        $missing += $path
    }
}

$errors = @()
foreach ($path in $missing) {
    $errors += "Missing required path: $path"
}

if ($missing.Count -eq 0) {
    $agentIndex = Get-Content -Raw (Join-Path $root ".codex\agents\README.md")
    $commandIndex = Get-Content -Raw (Join-Path $root ".codex\commands\README.md")
    $skillIndex = Get-Content -Raw (Join-Path $root ".codex\skills\README.md")

    foreach ($file in Get-ChildItem (Join-Path $root ".claude\agents") -Filter "*.md") {
        $rel = ".claude/agents/$($file.Name)"
        if ($agentIndex -notlike "*$rel*") {
            $errors += "Missing agent index entry: $rel"
        }
    }

    foreach ($file in Get-ChildItem (Join-Path $root ".claude\commands") -Filter "*.md") {
        $rel = ".claude/commands/$($file.Name)"
        if ($commandIndex -notlike "*$rel*") {
            $errors += "Missing command index entry: $rel"
        }
    }

    foreach ($dir in Get-ChildItem (Join-Path $root ".claude\skills") -Directory) {
        $skillFile = Join-Path $dir.FullName "SKILL.md"
        $rel = ".claude/skills/$($dir.Name)/SKILL.md"
        if (-not (Test-Path $skillFile)) {
            $errors += "Missing skill file: $rel"
        } elseif ($skillIndex -notlike "*$rel*") {
            $errors += "Missing skill index entry: $rel"
        }
    }

    if ($commandIndex -notlike "*.claude/skills/deflator_prediction/SKILL.md*") {
        $errors += "Missing /deflator_prediction skill fallback in command index."
    }
}

if ($errors.Count -gt 0) {
    if (-not $Quiet) {
        Write-Host "Codex Claude compatibility check failed. Missing:"
        foreach ($item in $errors) {
            Write-Host " - $item"
        }
    }
    exit 1
}

if (-not $Quiet) {
    Write-Host "Codex Claude compatibility check passed."
    Write-Host "Canonical instructions: CLAUDE.md and .claude/"
    Write-Host "Codex entry point: AGENTS.md"
}
