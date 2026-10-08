# Creates a Start Menu shortcut for the hiragana drill.
# Kept as a separate .ps1 (rather than inline in the .bat) because PowerShell
# escaped through batch carets breaks on parentheses and quotes.
# ASCII only, so it survives any console code page.

$ErrorActionPreference = 'Stop'

try {
    $here = Split-Path -Parent $MyInvocation.MyCommand.Path
    $bat  = Join-Path $here 'hiragana.bat'
    $ico  = Join-Path $here 'hiragana.ico'

    if (-not (Test-Path $bat)) {
        throw "hiragana.bat not found in $here"
    }

    $programs = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs'
    if (-not (Test-Path $programs)) { New-Item -ItemType Directory -Path $programs | Out-Null }

    $link = Join-Path $programs 'Hiragana Drill.lnk'

    # The target is cmd.exe, not hiragana.bat, because Windows refuses to pin
    # anything whose target is a .bat or .cmd - the "Pin to taskbar" item is
    # simply absent. With cmd.exe as the target it is an ordinary executable
    # and pins to both Start and the taskbar.
    #
    # Arguments stay relative ('/c hiragana.bat') and WorkingDirectory carries
    # the folder. Passing the full path instead would need doubled quotes,
    # because cmd /c strips the outer pair and then breaks on spaces.
    $cmd = Join-Path $env:SystemRoot 'System32\cmd.exe'

    $shell    = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($link)
    $shortcut.TargetPath       = $cmd
    $shortcut.Arguments        = '/c hiragana.bat'
    $shortcut.WorkingDirectory = $here
    $shortcut.Description      = 'Hiragana practice'
    $shortcut.WindowStyle      = 7          # start minimised
    if (Test-Path $ico) { $shortcut.IconLocation = "$ico,0" }
    $shortcut.Save()

    Write-Host ''
    Write-Host '  Shortcut created:' -ForegroundColor Green
    Write-Host "    $link"
    Write-Host ''
    Write-Host '  To pin it:'
    Write-Host '    1. Open Start and type:  hiragana'
    Write-Host '    2. Right-click the result'
    Write-Host '    3. Choose "Pin to Start"   (RU: Zakrepit na nachalnom ekrane)'
    Write-Host '       or "Pin to taskbar"     (RU: Zakrepit na paneli zadach)'
    Write-Host ''
    Write-Host '  On Windows 11 the taskbar option may sit under "More" / "Dopolnitelno".'
    Write-Host '  You can also drag the .lnk above straight onto the taskbar.'
    Write-Host ''
    Write-Host '  Windows does not allow pinning from a script, so that last'
    Write-Host '  step has to be done by hand - once.'
    Write-Host ''
    Write-Host '  If you move this folder later, run this installer again.'
    Write-Host ''
}
catch {
    Write-Host ''
    Write-Host '  Could not create the shortcut:' -ForegroundColor Red
    Write-Host "    $($_.Exception.Message)"
    Write-Host ''
    exit 1
}
