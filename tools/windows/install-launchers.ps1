# =====================================================================
#  Installe des lanceurs natifs `okp` et `oktopios` sous Windows, quand
#  les lanceurs .exe generes par pip sont casses
#  (« Fatal error in launcher: Unable to find an appended archive »).
#
#  Ce que fait le script :
#    1. localise le dossier Scripts de l'interpreteur Python courant ;
#    2. met de cote les okp.exe / oktopios.exe casses (renommes .broken) ;
#    3. depose okp.cmd / oktopios.cmd (qui appellent `python -m ...`).
#
#  Apres coup, `okp monfichier.okp` et `oktopios serve` fonctionnent
#  nativement, sans dependre des .exe.
#
#  Usage :  powershell -ExecutionPolicy Bypass -File install-launchers.ps1
# =====================================================================

$ErrorActionPreference = "Stop"

# 1. Dossier Scripts de CE Python
$py = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $py) { Write-Error "python introuvable sur le PATH."; exit 1 }
$pyDir = Split-Path $py
$scripts = Join-Path $pyDir "Scripts"
if (-not (Test-Path $scripts)) { New-Item -ItemType Directory -Path $scripts | Out-Null }
Write-Host "Dossier cible : $scripts"

# 2. Mettre de cote les .exe casses (sinon ils ont priorite sur les .cmd)
foreach ($name in @("okp.exe", "oktopios.exe")) {
    $exe = Join-Path $scripts $name
    if (Test-Path $exe) {
        $bak = "$exe.broken"
        if (Test-Path $bak) { Remove-Item $bak -Force -ErrorAction SilentlyContinue }
        try {
            Rename-Item $exe $bak -Force
            Write-Host "  mis de cote : $name -> $name.broken"
        } catch {
            Write-Warning "  impossible de renommer $name (verrouille ?). Ferme les serveurs en cours et relance."
        }
    }
}

# 3. Deposer les lanceurs .cmd
$okp = "@echo off`r`npython -m vm.main %*`r`n"
$okt = "@echo off`r`npython -m oktopios_framework %*`r`n"
Set-Content -Path (Join-Path $scripts "okp.cmd")      -Value $okp -Encoding ascii
Set-Content -Path (Join-Path $scripts "oktopios.cmd") -Value $okt -Encoding ascii
Write-Host "  cree : okp.cmd, oktopios.cmd"

Write-Host ""
Write-Host "Termine. Ouvre un NOUVEAU terminal puis teste :"
Write-Host "  okp --version"
Write-Host "  oktopios version"
