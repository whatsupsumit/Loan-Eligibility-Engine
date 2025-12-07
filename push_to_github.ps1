# GitHub Push Helper Script
# Run this after creating your GitHub repository

Write-Host "🚀 GitHub Repository Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Get GitHub username and repo name
$username = Read-Host "Enter your GitHub username"
$repoName = Read-Host "Enter repository name (default: loan-eligibility-engine)"

if ([string]::IsNullOrWhiteSpace($repoName)) {
    $repoName = "loan-eligibility-engine"
}

$repoUrl = "https://github.com/$username/$repoName.git"

Write-Host ""
Write-Host "Repository URL: $repoUrl" -ForegroundColor Yellow
Write-Host ""

# Confirm
$confirm = Read-Host "Is this correct? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Aborted. Please run the script again." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "📦 Initializing Git repository..." -ForegroundColor Yellow

# Initialize git if not already initialized
if (-not (Test-Path ".git")) {
    git init
    Write-Host "✅ Git initialized" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Git already initialized" -ForegroundColor Blue
}

Write-Host ""
Write-Host "📝 Adding files..." -ForegroundColor Yellow
git add .

Write-Host ""
Write-Host "💾 Creating commit..." -ForegroundColor Yellow
git commit -m "Initial commit: Loan Eligibility Engine for ClickPe SDE Internship"

Write-Host ""
Write-Host "🔗 Adding remote repository..." -ForegroundColor Yellow

# Remove existing remote if any
$existingRemote = git remote get-url origin 2>$null
if ($existingRemote) {
    git remote remove origin
    Write-Host "ℹ️  Removed existing remote" -ForegroundColor Blue
}

git remote add origin $repoUrl

Write-Host ""
Write-Host "⬆️  Pushing to GitHub..." -ForegroundColor Yellow
git branch -M main
git push -u origin main

Write-Host ""
Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Go to: https://github.com/$username/$repoName" -ForegroundColor White
Write-Host "2. Click 'Settings' → 'Collaborators'" -ForegroundColor White
Write-Host "3. Invite:" -ForegroundColor White
Write-Host "   - saurabh@clickpe.ai" -ForegroundColor Yellow
Write-Host "   - harsh.srivastav@clickpe.ai" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 Your GitHub Link for submission:" -ForegroundColor Cyan
Write-Host "https://github.com/$username/$repoName" -ForegroundColor Green
Write-Host ""
