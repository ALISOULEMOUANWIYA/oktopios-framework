"""Permet d'invoquer la CLI via `python -m oktopios_framework ...`.

Utile quand le lanceur de script `oktopios.exe` n'est pas sur le PATH ou est
cassé (souci fréquent sous Windows). Équivalent à la commande `oktopios`.
"""
import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
