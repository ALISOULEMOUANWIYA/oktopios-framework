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

> 📖 **Nouveau ?** Commence par le **[guide de prise en main](GETTING_STARTED.md)** —
> de l'installation à une application complète qui tourne, en passant par chaque couche.
> Pour la mise en ligne : **[guide de déploiement](DEPLOYMENT.md)** (Docker, nginx, TLS).

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
- ✅ **Middleware** (pipeline avant/après : logger, CORS, gardes)
- ✅ **Formulaires & validation** (binding `req.body` → modèle + décorateurs de validation)
- ✅ **CLI & scaffolding** (`oktopios new`, générateurs, `serve`, `migrate`)
- ✅ **Auth & sessions** (hash salé, sessions, cookie/Bearer, garde `requireAuth`)
- ✅ **Pagination & messages flash** (`Paginator`, `FlashBag`)
- ✅ **Autorisation par rôle** (`requireRole`) et **API REST auto** (`Rest`)
- ✅ **App de référence `blog_complet` + tests e2e** (toutes les couches, vérifiées via `pytest`)

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

Les templates utilisent `{{variable}}`, `{{variable|defaut}}` et des **boucles**
`{{#each liste}} … {{/each}}` (imbriquables) — à l'intérieur, `{{champ}}` désigne
l'élément courant et `{{this}}` un scalaire :

```okp
// contrôleur : passe une liste de maps à la vue
var vues = []
for (a in articles) { vues = vues + [ { "titre": a.titre, "auteur": a.auteur.nom } ] }
return vue.render("list.html", { "articles": vues })
```
```html
<!-- list.html -->
<ul>{{#each articles}}<li>{{titre}} — {{auteur}}</li>{{/each}}</ul>
```

Avec un layout, le rendu de la page est inséré dans `{{content}}` du layout (les
autres variables y restent disponibles). Un contrôleur renvoie directement la
chaîne HTML :

```okp
fun home(req: any): any {
    return vue.render("home.html", { "title": "Accueil", "nom": "Awa" })
}
```

Démo complète : `examples/web_views.okp` (+ `examples/templates/`).

## Middleware 🧱

Pipeline **avant** (`use`, peut court-circuiter) et **après** (`after`, transforme
la réponse) :

```okp
use "oktopios_framework/routing.okp"

var res = new Response()
fun guard(req: any): any {
    if (req["path"] == "/admin") { return res.status(401, "Non autorise") }
    return null                    // null = continuer
}

var router = new Router()
router.use(logRequest)             // middleware fourni : journalise la requête
router.use(guard)                  // garde : court-circuite si réponse != null
router.after(corsAllowAll)         // middleware fourni : ajoute l'en-tête CORS
router.get("/", home)
router.run(8000)
```

- **avant** : `fun(req) -> réponse | null` (null = passer au suivant / au contrôleur)
- **après** : `fun(req, resp) -> resp` (reçoit et renvoie la réponse, éventuellement modifiée)
- fournis : `logRequest` (avant), `corsAllowAll` (après). Démo : `examples/web_mw.okp`.

## Formulaires & validation ✅

Lie les données d'une requête (`req.body`, un map) à un modèle par réflexion,
puis valide ses champs d'après leurs **décorateurs** :

```okp
use "oktopios_framework/forms.okp"

class User {
    @NotNull @MinLength(3) @MaxLength(20)
    var nom: any
    @NotNull @Email
    var email: any
    @Min(18)
    var age: any
}

var form = new Form()
var u = new User()
form.bind(u, req["body"])           // remplit u depuis le map de la requête

if (form.isValid(u) == false) {
    for (e in form.validate(u)) { print(e) }   // liste des messages d'erreur
}
```

Décorateurs reconnus : `@NotNull`, `@Email`, `@Min(n)`, `@MinLength(n)`,
`@MaxLength(n)`. `validate(entity)` renvoie la liste des erreurs (vide = valide),
`isValid(entity)` un booléen. Démo : `examples/forms_demo.okp`.

## CLI & scaffolding 🛠️ (façon `django-admin` / `symfony`)

L'installation expose la commande **`oktopios`** :

```bash
oktopios new monapp            # squelette minimal
oktopios new --full monblog    # application MVC COMPLETE (ORM + auth + vues + routes protégées)
cd monblog
oktopios serve                 # lance l'app (http://localhost:8000)
oktopios serve --port 8080     # autre port (utile si 8000 est réservé sous Windows)
```

> **Windows — `WinError 10013` sur le port 8000 ?** Le port est dans une plage
> réservée (Hyper-V / WSL / Docker). Lance sur un autre port avec
> `oktopios serve --port 8080` (ou `set OKTOPIOS_PORT=8080`). Lister les plages
> réservées : `netsh interface ipv4 show excludedportrange protocol=tcp`.

Avec **`--full`**, l'app générée est structurée comme [`examples/blog_complet.okp`](examples/blog_complet.okp)
et tourne telle quelle : `models/article.okp` (modèle décoré + validation),
`controllers/articles.okp` + `controllers/auth.okp`, `templates/` (layout + list + show),
et un `main.okp` qui migre la base, câble les routeurs public/protégé (`requireAuth`)
et démarre le serveur. Parcours prêt : `/` → `/login?user=admin&pw=admin123` →
`/admin/create?titre=..&contenu=..`.

`oktopios new` crée une arborescence prête à l'emploi :

```
monapp/
├── main.okp                 # point d'entrée (config + router + run)
├── controllers/home.okp     # contrôleur d'accueil
├── models/                  # vos modèles
├── templates/home.html      # vue d'accueil
├── bin/migrate.okp          # migrations
├── .env.local  .env.prod    # config par environnement
└── .gitignore
```

Autres commandes :

```bash
oktopios make:model Article --table articles   # -> models/article.okp (décoré)
oktopios make:controller Blog                   # -> controllers/blog.okp
oktopios migrate                                # exécute bin/migrate.okp
oktopios version
```

## Authentification & sessions 🔐

Hachage de mot de passe salé, sessions en mémoire, et un middleware de garde.
Le token est lu depuis le cookie `oktopios_session` ou l'en-tête
`Authorization: Bearer ...` (nécessite `oktopios>=0.14.0`).

```okp
use "oktopios_framework/routing.okp"
use "oktopios_framework/auth.okp"

var res = new Response()

fun login(req: any): any {
    var q = req["query"]
    // ... vérifier q["user"] / q["pw"] contre votre base ...
    var token = authService.login(q["user"])          // ouvre une session
    var entetes = { "Set-Cookie": authService.cookieHeader(token) }
    var r = { "body": "Connecte", "headers": entetes }
    return r
}

fun profile(req: any): any {
    return "Profil de " + authService.check(req)       // utilisateur courant
}

var pub = new Router()
pub.get("/login", login)                               // route publique

var priv = new Router()
priv.use(requireAuth)                                  // garde : 401 si non connecté
priv.get("/profile", profile)
priv.run(8000)
```

- `authService.hashPassword(pw)` → `"sel$empreinte"` à stocker ; `verify(pw, stored)` → booléen.
- `authService.login(user)` → token ; `check(req)` → utilisateur ou `null` ; `logout(token)`.
- `requireAuth` garde toutes les routes de **son** routeur (enregistrez les routes
  publiques sur un routeur distinct). Démo : `examples/web_auth.okp`.

## App de référence : blog complet 📰

[`examples/blog_complet.okp`](examples/blog_complet.okp) combine **toutes** les
couches en une seule application vérifiable :

| Couche | Utilisé pour |
|---|---|
| ORM (`oktopios-orm`) | modèle `Article` décoré, migration, `Repo.save/all/findBy` |
| Routing | routeur **public** (`/`, `/articles/:id`, `/login`) + **protégé** (`/admin/create`) |
| Middleware | `logRequest` sur les deux routeurs |
| Vues | `View` + layout (`blog_layout.html`, `blog_list.html`, `blog_show.html`) |
| Formulaires | `Form.bind` + `validate` (décorateurs `@NotNull`/`@MinLength`/`@MaxLength`) |
| Auth | `/login` pose un cookie, `requireAuth` garde l'espace admin |

```bash
okp examples/blog_complet.okp     # http://localhost:8000
```

Parcours : `/` liste → `/login?user=admin&pw=admin123` → `/admin/create?titre=..&contenu=..`
(protégé, validé, redirige vers `/articles/:id`).

## Tests d'intégration end-to-end ✅

Le dépôt inclut une **suite e2e** qui démarre réellement le blog et l'interroge
en HTTP (liste, détail, 404, login + cookie, création protégée 401/302,
validation 422) — le socle de robustesse de l'écosystème.

```bash
pip install oktopios-framework[test]   # ou: pip install pytest
pytest                                 # depuis la racine du dépôt
```

En développement (dépôts `oktopios`, `oktopios-orm`, `oktopios-framework` côte à
côte), les sources frères sont ajoutées automatiquement au `PYTHONPATH` du
serveur de test — aucune installation requise.

## Pagination 📄

```okp
use "oktopios_framework/pagination.okp"

var pager = new Paginator(repo, 10)      // repo (oktopios-orm), 10 par page
fun liste(req: any): any {
    var page = pager.pageFrom(req)       // lit ?page= (défaut 1)
    var items = pager.items(page)        // entités de la page
    var liens = pager.links(page, "/")   // barre « Précédent / Suivant »
    // ... construire la vue avec items + liens ...
}
```

`Paginator` : `pageFrom(req)`, `items(page)`, `total()`, `totalPages()`,
`links(page, baseUrl)`.

## Messages flash 💬

Messages one-shot affichés **une fois** à la requête suivante, puis effacés
(ex. « Article créé » après une action) :

```okp
use "oktopios_framework/flash.okp"

// après l'action (clé = token de session pour isoler l'utilisateur)
flash.add(authService.tokenFromRequest(req), "success", "Article cree")
return res.redirect("/")

// à l'affichage de la page suivante
var html = flash.render(authService.tokenFromRequest(req))   // rend puis vide
```

`FlashBag` : `add(cle, type, message)`, `pull(cle)`, `render(cle)`. Démo
complète (relations + pagination + flash) : `examples/blog_avance.okp`.

## Autorisation par rôle 🛡️

```okp
var token = authService.loginAs("patron", "admin")   // session avec rôle
authService.roleOf(req)                               // rôle courant

var priv = new Router()
priv.use(requireRole("admin"))     // 401 si anonyme, 403 si rôle != admin
priv.get("/admin/stats", stats)
```

## API REST automatique 🔌

Génère des endpoints JSON CRUD depuis un `Repo` (oktopios-orm) :

```okp
use "oktopios_framework/rest.okp"

var api = new Rest(router, repo)
api.resource("/api/articles")
//  GET  /api/articles        -> liste JSON
//  GET  /api/articles/:id    -> un élément (404 si absent)
//  POST /api/articles        -> crée depuis le corps JSON (201)
```

Démo complète (REST + rôle) : `examples/rest_api.okp`.

## Configuration `.env` (façon Symfony)

`.env.local` (développement) et `.env.prod` (production) contiennent des paires
`CLE=VALEUR`. `Config.load("local")` / `Config.load("prod")` chargent le fichier
correspondant. Ne mettez jamais de secrets réels dans un `.env.prod` versionné.

## Licence

MIT © Mouanwiya Ali Soule
