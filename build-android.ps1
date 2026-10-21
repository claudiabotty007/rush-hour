<#
.SYNOPSIS
  Builds a signed, sideloadable Rush Hour APK into dist\.

.DESCRIPTION
  1. Regenerates the page (8x8 puzzles, fonts embedded) into the app's assets and checks every puzzle.
  2. Creates a release signing key on first run (outside the repo, in ~\.rushhour-signing).
  3. Runs Gradle to build and sign the APK, then verifies the signature.

  Run it with:  powershell -NoProfile -ExecutionPolicy Bypass -File .\build-android.ps1

  Tool locations (override with JAVA_HOME / ANDROID_HOME if yours differ):
    JDK 17   %LOCALAPPDATA%\Android\jdk-17
    SDK      %LOCALAPPDATA%\Android\Sdk
#>
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$android = Join-Path $root 'android'

function Fail($msg) { Write-Host "ERROR: $msg" -ForegroundColor Red; exit 1 }

# ---- tools -----------------------------------------------------------------
if (-not $env:JAVA_HOME -or -not (Test-Path (Join-Path $env:JAVA_HOME 'bin\java.exe'))) {
    $env:JAVA_HOME = Join-Path $env:LOCALAPPDATA 'Android\jdk-17'
}
if (-not (Test-Path (Join-Path $env:JAVA_HOME 'bin\java.exe'))) { Fail "No JDK 17 found at $env:JAVA_HOME. Set JAVA_HOME." }
if (-not $env:ANDROID_HOME -or -not (Test-Path $env:ANDROID_HOME)) {
    $env:ANDROID_HOME = Join-Path $env:LOCALAPPDATA 'Android\Sdk'
}
if (-not (Test-Path $env:ANDROID_HOME)) { Fail "No Android SDK found at $env:ANDROID_HOME. Set ANDROID_HOME." }
$env:ANDROID_SDK_ROOT = $env:ANDROID_HOME
$env:Path = (Join-Path $env:JAVA_HOME 'bin') + ';' + $env:Path

$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) { Fail 'python not found on PATH.' }
$node = (Get-Command node -ErrorAction SilentlyContinue).Source
if (-not $node) { Fail 'node not found on PATH (used to check the puzzles).' }

# ---- page ------------------------------------------------------------------
$page = Join-Path $android 'app\src\main\assets\index.html'
& $python (Join-Path $root 'build.py') 8 (Join-Path $root 'puzzles-8x8.json') $page
if ($LASTEXITCODE -ne 0) { Fail 'build.py failed.' }
& $node (Join-Path $root 'check.js') $page
if ($LASTEXITCODE -ne 0) { Fail 'puzzle check failed.' }

# ---- signing key -----------------------------------------------------------
$propsFile = Join-Path $android 'keystore.properties'
if (-not (Test-Path $propsFile)) {
    $dir = Join-Path $env:USERPROFILE '.rushhour-signing'
    $jks = Join-Path $dir 'rushhour-release.jks'
    if (Test-Path $jks) { Fail "$jks exists but $propsFile is missing. Restore keystore.properties or move the key aside." }
    New-Item -ItemType Directory -Force $dir | Out-Null
    $bytes = New-Object byte[] 24
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $pw = [Convert]::ToBase64String($bytes).Replace('+', 'A').Replace('/', 'b').Replace('=', 'c')
    & keytool -genkeypair -keystore $jks -storetype PKCS12 -alias rushhour -keyalg RSA -keysize 2048 `
        -validity 10000 -dname 'CN=Rush Hour' -storepass $pw -keypass $pw
    if ($LASTEXITCODE -ne 0) { Fail 'keytool failed.' }
    $jksForGradle = $jks.Replace('\', '/')
    @(
        "storeFile=$jksForGradle",
        "storePassword=$pw",
        'keyAlias=rushhour',
        "keyPassword=$pw"
    ) | Set-Content -Path $propsFile -Encoding ascii
    Write-Host "Created release key: $jks" -ForegroundColor Yellow
    Write-Host 'Back it up. Updates only install over this version if they are signed with the same key.' -ForegroundColor Yellow
}

# ---- build -----------------------------------------------------------------
Push-Location $android
try {
    & .\gradlew.bat --no-daemon assembleRelease
    if ($LASTEXITCODE -ne 0) { Fail 'Gradle build failed.' }
} finally { Pop-Location }

$gradle = Get-Content (Join-Path $android 'app\build.gradle') -Raw
$version = [regex]::Match($gradle, "versionName\s+'([^']+)'").Groups[1].Value
$built = Join-Path $android 'app\build\outputs\apk\release\app-release.apk'
if (-not (Test-Path $built)) { Fail "Expected APK not found: $built" }

$dist = Join-Path $root 'dist'
New-Item -ItemType Directory -Force $dist | Out-Null
$apk = Join-Path $dist "rush-hour-$version.apk"
Copy-Item $built $apk -Force

# ---- verify ----------------------------------------------------------------
$buildTools = Get-ChildItem (Join-Path $env:ANDROID_HOME 'build-tools') | Sort-Object Name -Descending | Select-Object -First 1
$apksigner = Join-Path $buildTools.FullName 'apksigner.bat'
& $apksigner verify --print-certs $apk
if ($LASTEXITCODE -ne 0) { Fail 'apksigner verification failed.' }

$hash = (Get-FileHash $apk -Algorithm SHA256).Hash
Write-Host ''
Write-Host "APK:    $apk" -ForegroundColor Green
Write-Host ("Size:   {0:N0} KB" -f ((Get-Item $apk).Length / 1KB))
Write-Host "SHA256: $hash"
