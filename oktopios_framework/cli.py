"""
oktopios-framework — CLI / scaffolding (façon django-admin / symfony).

Expose la commande `oktopios` :

    oktopios new <projet>              crée un projet complet prêt à lancer
    oktopios make:model <Nom>          génère un modèle décoré
    oktopios make:controller <Nom>     génère un contrôleur
    oktopios serve [--port N]          lance l'application (okp main.okp)
    oktopios migrate                   exécute les migrations (bin/migrate.okp)
    oktopios version                   affiche la version du framework
"""
import argparse
import os
import subprocess
import sys

from . import __version__


# --------------------------------------------------------------------------
# Gabarits (templates) de fichiers générés
# --------------------------------------------------------------------------

ENV_LOCAL = """# Environnement de developpement
APP_ENV=local
APP_DEBUG=true
DB_PATH=var/app.db
"""

ENV_PROD = """# Environnement de production (ne versionnez jamais de vrais secrets)
APP_ENV=prod
APP_DEBUG=false
DB_PATH=var/app.db
"""

MAIN_OKP = '''// Point d'entree de l'application {name}.
// Lancer :  oktopios serve   (ou  okp main.okp)
use "oktopios_framework/routing.okp"
use "oktopios_framework/config.okp"
use "oktopios_framework/view.okp"
use "controllers/home.okp"

var cfg = new Config()
cfg.load("local")

var router = new Router()
router.use(logRequest)
router.get("/", homeIndex)

print("{name} demarre sur http://localhost:8000")
router.run(8000)
'''

HOME_CONTROLLER = '''// Controleur Home — genere par `oktopios new`.
inject Type

var vue = new View("templates")

fun homeIndex(req: any): any {{
    return vue.render("home.html", {{ "titre": "{name}" }})
}}
'''

HOME_TEMPLATE = """<!doctype html>
<html lang="fr">
<head><meta charset="utf-8"><title>{{titre}}</title></head>
<body>
  <h1>Bienvenue sur {{titre}} 🐙</h1>
  <p>Votre application oktopios-framework est operationnelle.</p>
</body>
</html>
"""

MIGRATE_OKP = '''// Migrations — declarez ici vos modeles puis Schema.migrate(...).
use "oktopios_orm/orm.okp"
use "models/example.okp"

var schema = new Schema()
// schema.migrate(new Example())
print("Migrations terminees.")
'''

MODEL_TEMPLATE = '''@Entity("{table}")
class {Name} {{
    @Id
    var id: any

    @NotNull
    @Column("nom")
    var nom: any
}}
'''

CONTROLLER_TEMPLATE = '''// Controleur {Name} — genere par `oktopios make:controller`.
inject Type

var vue = new View("templates")

fun {fn}Index(req: any): any {{
    return "<h1>{Name}</h1>"
}}
'''

GITIGNORE = """var/
*.db
__pycache__/
"""


# --------------------------------------------------------------------------
# Utilitaires
# --------------------------------------------------------------------------

def _write(path, content):
    """Écrit un fichier (sans écraser un fichier existant)."""
    if os.path.exists(path):
        print(f"  ignore (existe deja) : {path}")
        return False
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  cree : {path}")
    return True


def _okp_binary():
    """Trouve l'exécutable `okp` (ou se rabat sur `python -m vm.main`)."""
    from shutil import which
    okp = which("okp")
    if okp:
        return [okp]
    return [sys.executable, "-m", "vm.main"]


# --------------------------------------------------------------------------
# Commandes
# --------------------------------------------------------------------------

def cmd_new(args):
    name = args.name
    root = os.path.abspath(name)
    if os.path.exists(root) and os.listdir(root):
        print(f"[erreur] le dossier '{name}' existe deja et n'est pas vide.")
        return 1
    print(f"Creation du projet '{name}' ...")
    _write(os.path.join(root, ".env.local"), ENV_LOCAL)
    _write(os.path.join(root, ".env.prod"), ENV_PROD)
    _write(os.path.join(root, ".gitignore"), GITIGNORE)
    _write(os.path.join(root, "main.okp"), MAIN_OKP.format(name=name))
    _write(os.path.join(root, "controllers", "home.okp"),
           HOME_CONTROLLER.format(name=name))
    _write(os.path.join(root, "templates", "home.html"), HOME_TEMPLATE)
    _write(os.path.join(root, "models", ".gitkeep"), "")
    _write(os.path.join(root, "bin", "migrate.okp"), MIGRATE_OKP)
    print("")
    print(f"Projet '{name}' pret. Pour demarrer :")
    print(f"  cd {name}")
    print("  oktopios serve")
    return 0


def cmd_make_model(args):
    name = args.name
    table = args.table or (name.lower() + "s")
    fn = name.lower() + ".okp"
    path = os.path.join("models", fn)
    content = MODEL_TEMPLATE.format(Name=name, table=table)
    return 0 if _write(path, content) else 1


def cmd_make_controller(args):
    name = args.name
    fn = name.lower()
    path = os.path.join("controllers", fn + ".okp")
    content = CONTROLLER_TEMPLATE.format(Name=name, fn=fn)
    return 0 if _write(path, content) else 1


def cmd_serve(args):
    entry = args.entry or "main.okp"
    if not os.path.exists(entry):
        print(f"[erreur] point d'entree introuvable : {entry}")
        return 1
    cmd = _okp_binary() + [entry]
    print(f"Lancement : {' '.join(cmd)}")
    return subprocess.call(cmd)


def cmd_migrate(args):
    entry = os.path.join("bin", "migrate.okp")
    if not os.path.exists(entry):
        print(f"[erreur] fichier de migration introuvable : {entry}")
        return 1
    cmd = _okp_binary() + [entry]
    print(f"Migrations : {' '.join(cmd)}")
    return subprocess.call(cmd)


def cmd_version(args):
    print(f"oktopios-framework {__version__}")
    return 0


# --------------------------------------------------------------------------
# Entrée principale
# --------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(
        prog="oktopios",
        description="Outil CLI du framework web Oktopios (facon django-admin / symfony).",
    )
    sub = p.add_subparsers(dest="command")

    sp = sub.add_parser("new", help="cree un nouveau projet")
    sp.add_argument("name", help="nom du projet (dossier a creer)")
    sp.set_defaults(func=cmd_new)

    sp = sub.add_parser("make:model", help="genere un modele decore")
    sp.add_argument("name", help="nom de la classe modele (ex. User)")
    sp.add_argument("--table", help="nom de la table (defaut: nom en minuscules + 's')")
    sp.set_defaults(func=cmd_make_model)

    sp = sub.add_parser("make:controller", help="genere un controleur")
    sp.add_argument("name", help="nom du controleur (ex. Home)")
    sp.set_defaults(func=cmd_make_controller)

    sp = sub.add_parser("serve", help="lance l'application (okp main.okp)")
    sp.add_argument("entry", nargs="?", help="point d'entree (defaut: main.okp)")
    sp.add_argument("--port", type=int, help="(informatif) port, defini dans main.okp")
    sp.set_defaults(func=cmd_serve)

    sp = sub.add_parser("migrate", help="execute bin/migrate.okp")
    sp.set_defaults(func=cmd_migrate)

    sp = sub.add_parser("version", help="affiche la version du framework")
    sp.set_defaults(func=cmd_version)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
