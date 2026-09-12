# oktopios-framework 🐙🌐

Framework web **MVC** pour le langage **[Oktopios](https://pypi.org/project/oktopios/)**,
dans l'esprit de **Django** et **Symfony** — on reprend leurs points forts, on
vise à transformer leurs points faibles en points forts.

Troisième couche de l'écosystème, façon Django/Symfony :

| Couche | Rôle | Équivalent |
|---|---|---|
| `oktopios` | langage + interpréteur | Python / PHP |
| `oktopios-orm` | ORM (modèles, migrations, requêtes) | Django ORM / Doctrine |
| **`oktopios-framework`** | framework applicatif (config, MVC…) | **Django / Symfony** |

## Installation

```bash
pip install oktopios-framework
```

Installe automatiquement `oktopios-orm` et `oktopios` (dépendances) — comme
Django tire Python et Symfony tire PHP.

## Statut (construction pilier par pilier)

- ✅ **ORM** (via `oktopios-orm`) — modèles décorés, migrations, query-builder
- ✅ **Configuration** par environnement (`.env.local`, `.env.prod`)
- ⏳ Routing + contrôleurs (serveur HTTP)
- ⏳ Moteur de templates (vues)
- ⏳ Formulaires / validation, Auth, CLI / scaffolding

## Structure

```
oktopios-framework/
├── oktopios_framework/
│   ├── config.okp        # Config : chargement .env.<env>
│   └── (routing.okp, view.okp … à venir)
└── examples/
    ├── blog.okp          # démo ORM + config
    ├── .env.local        # config développement
    └── .env.prod         # config production
```

## Démarrage

```bash
pip install oktopios-framework
okp examples/blog.okp        # depuis la racine du projet
```

```okp
use "oktopios_orm/orm.okp"
use "oktopios_framework/config.okp"

var cfg = new Config()
cfg.load("local")            // lit .env.local  ("prod" -> .env.prod)
print(cfg.get("DB_PATH"))

@Entity("articles")
class Article {
    @Id
    var id: int
    @Column("titre")
    var title: string
}
// ... Schema.migrate / Repo / Query fournis par oktopios-orm
```

## Configuration `.env` (façon Symfony)

`.env.local` (développement) et `.env.prod` (production) contiennent des paires
`CLE=VALEUR`. `Config.load("local")` / `Config.load("prod")` chargent le fichier
correspondant. Ne mettez jamais de secrets réels dans un `.env.prod` versionné.

## Licence

MIT © Mouanwiya Ali Soule
