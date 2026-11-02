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
- ✅ **Routing + contrôleurs** (serveur HTTP via le namespace natif `Server`)
- ✅ **Moteur de templates** (vues HTML, layout)
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

## Routing / Contrôleurs 🌐

```okp
use "oktopios_framework/routing.okp"

var res = new Response()

fun home(req: any): any {
    return "<h1>Oktopios</h1>"
}
fun apiUser(req: any): any {
    var p = req["params"]
    var data = { "id": p["id"], "nom": "Awa" }
    return res.json(data)          // -> application/json
}

var router = new Router()
router.get("/", home)
router.get("/api/users/:id", apiUser)
router.run(8000)                   // serveur bloquant
```

Un **contrôleur** est une fonction `(req) -> réponse`. `req` est un map
`{ method, path, query, params, body }`. Il peut renvoyer :
- une **chaîne** → `200 text/html`
- `res.json(x)` → `200 application/json`
- `res.html(s)`, `res.text(s)`, `res.status(code, body)`, `res.redirect(url)`

`Router` : `get` / `post` / `put` / `delete` (chaînables) + `run(port)`.
Démo complète : `examples/web.okp`.

## Vue — templates HTML 🖼️

```okp
use "oktopios_framework/view.okp"

var vue = new View("templates")     // dossier des templates
vue.setLayout("layout.html")        // layout commun contenant {{content}}

var html = vue.render("home.html", { "title": "Accueil", "nom": "Awa" })
```

Les templates utilisent `{{variable}}` et `{{variable|defaut}}`. Avec un layout,
le rendu de la page est inséré dans `{{content}}` du layout (les autres variables
y restent disponibles). Un contrôleur renvoie directement la chaîne HTML :

```okp
fun home(req: any): any {
    return vue.render("home.html", { "title": "Accueil", "nom": "Awa" })
}
```

Démo complète : `examples/web_views.okp` (+ `examples/templates/`).

## Configuration `.env` (façon Symfony)

`.env.local` (développement) et `.env.prod` (production) contiennent des paires
`CLE=VALEUR`. `Config.load("local")` / `Config.load("prod")` chargent le fichier
correspondant. Ne mettez jamais de secrets réels dans un `.env.prod` versionné.

## Licence

MIT © Mouanwiya Ali Soule
