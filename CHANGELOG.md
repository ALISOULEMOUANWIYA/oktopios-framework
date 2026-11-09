# Changelog

## [0.12.1] — `oktopios migrate` incrémental

### Changé
- Le `bin/migrate.okp` généré par `new --full` utilise désormais le **`Migrator`**
  d'`oktopios-orm` (migrations incrémentales façon Alembic) : on ajoute ses
  migrations à la liste, `oktopios migrate` n'applique que les nouvelles
  (idempotent). Dépendance relevée à `oktopios-orm>=0.5.0`.

## [0.12.0] — Déploiement production (Docker)

### Ajouté
- **Guide [`DEPLOYMENT.md`](DEPLOYMENT.md)** : conteneurisation, reverse-proxy
  TLS (nginx), base persistante (volume), montée en charge.
- `oktopios new --full` génère désormais un **`Dockerfile`** + `.dockerignore`
  (app déployable prête à l'emploi).
- `Router.run` lit **`OKTOPIOS_HOST`** (défaut `127.0.0.1`) : mettre `0.0.0.0`
  pour écouter sur toutes les interfaces en conteneur.

### Changé
- Dépendance relevée à **`oktopios>=0.17.1`** (serveur HTTP multi-thread).

## [0.11.0] — Boucles de gabarits dans les vues

### Changé
- Les vues peuvent désormais **boucler** avec `{{#each liste}} … {{/each}}`
  (nécessite `oktopios>=0.17.0`). L'exemple `examples/blog_avance.okp` passe une
  **liste de maps** à la vue au lieu de construire le HTML dans le contrôleur :
  ```
  {{#each articles}}<li>{{titre}} — {{auteur}}</li>{{/each}}
  ```
- Dépendances relevées : `oktopios>=0.17.0`, `oktopios-orm>=0.4.0`
  (relations `@OneToMany` / `@ManyToMany`).

## [0.10.0] — Pagination & messages flash

### Ajouté
- `oktopios_framework/pagination.okp` : classe **`Paginator`** (s'appuie sur
  `Repo.count`/`Repo.page`) — `pageFrom(req)` (lit `?page=`), `items(page)`,
  `totalPages()`, `links(page, baseUrl)` (barre « Précédent / Suivant »).
- `oktopios_framework/flash.okp` : classe **`FlashBag`** + instance partagée
  `flash` — messages one-shot entre requêtes (`add` / `pull` / `render`),
  rangés par clé (en général le token de session) et effacés après affichage.
- Démo `examples/blog_avance.okp` (relations `@ManyToOne` + pagination + flash +
  auth) et templates `av_list.html` / `av_show.html`.
- Tests e2e `tests/test_blog_avance_e2e.py`.

### Corrigé
- `oktopios serve` / `migrate` : `Ctrl+C` s'arrête proprement (plus de trace
  `KeyboardInterrupt`).

### Changé
- Dépendance relevée à **`oktopios-orm>=0.3.0`** (relations + pagination).

## [0.9.3] — `serve` / `migrate` fiables (sans lanceur `okp.exe`)

### Corrigé
- `oktopios serve` et `oktopios migrate` exécutent l'app via
  **`python -m vm.main`** (le même interpréteur que la CLI) plutôt que via le
  lanceur `okp.exe`. Évite l'erreur Windows *« Fatal error in launcher: Unable
  to find an appended archive »* quand les lanceurs `.exe` de l'installation
  Python sont cassés. On ne se rabat sur `okp` que si le module `vm` n'est pas
  importable.

## [0.9.2] — Port configurable (`serve --port` / `OKTOPIOS_PORT`)

### Ajouté / Changé
- **`oktopios serve --port <N>`** change réellement le port d'écoute (il
  définit `OKTOPIOS_PORT` pour le processus). Les apps générées (`new` et
  `new --full`) et l'exemple `blog_complet` lisent `OKTOPIOS_PORT` (défaut
  `8000`). Évite l'erreur Windows **WinError 10013** quand `8000` est dans une
  plage de ports réservée (Hyper-V / WSL / Docker).
- `Router.run(port)` accepte désormais un port entier **ou** chaîne (valeur lue
  d'une variable d'environnement).

## [0.9.1] — Invocation `python -m oktopios_framework`

### Ajouté
- Point d'entrée module : la CLI s'invoque aussi via
  **`python -m oktopios_framework ...`** (équivalent à `oktopios ...`). Utile
  quand le lanceur `oktopios.exe` n'est pas sur le PATH ou est cassé (souci
  fréquent sous Windows).

## [0.9.0] — Scaffolding complet `oktopios new --full`

### Ajouté
- **`oktopios new --full <projet>`** — échafaude une application MVC **complète**
  (et non le squelette minimal), structurée comme `blog_complet` :
  - `models/article.okp` (modèle décoré `@Entity`/`@Id`/`@Column` + validation
    `@NotNull`/`@MinLength`/`@MaxLength`) ;
  - `controllers/articles.okp` (liste, détail, création validée) et
    `controllers/auth.okp` (login, logout) ;
  - `templates/layout.html`, `list.html`, `show.html` ;
  - `main.okp` câblant ORM (migration + seed), services partagés, routeurs
    public + protégé (`requireAuth`) et démarrage.
  L'app générée tourne telle quelle (`oktopios serve`) et couvre tout le parcours
  (liste → login → création protégée → détail).
- Tests `tests/test_cli_scaffold.py` (structure + contenu de `new` et `new --full`).

## [0.8.0] — App de référence « blog complet » + tests e2e

### Ajouté
- **`examples/blog_complet.okp`** — application de référence combinant **toutes**
  les couches de l'écosystème dans un seul parcours vérifiable : ORM (modèle
  décoré, migration, `Repo`), routing (routeurs public + protégé), middleware
  (`logRequest`), vues (`View` + layout), formulaires (`Form` : binding +
  validation par décorateurs) et auth (login, sessions, cookie, `requireAuth`).
  Templates `examples/templates/blog_layout.html`, `blog_list.html`, `blog_show.html`.
- **Suite de tests d'intégration end-to-end** (`tests/test_blog_e2e.py`) : démarre
  réellement le serveur et exerce le parcours complet via HTTP (liste, détail,
  404, login + cookie, création protégée 401/302, validation 422). Lançable avec
  `pytest` ; extra `test` (`pip install oktopios-framework[test]`).

### Changé
- Dépendances relevées : **`oktopios>=0.16.0`** (concat de listes indexable,
  `execSQL`→id, en-têtes) et **`oktopios-orm>=0.2.0`** (clé primaire auto-générée).

## [0.7.0] — Authentification & sessions

### Ajouté
- `oktopios_framework/auth.okp` :
  - classe **`Auth`** — hachage de mot de passe salé (`hashPassword` / `verify`
    via SHA-256 + sel aléatoire), sessions en mémoire (`login` / `userFor` /
    `logout`), lecture du token depuis la requête (cookie `oktopios_session`
    ou `Authorization: Bearer ...`), `check(req)` → utilisateur courant, et
    `cookieHeader(token)` pour poser le cookie ;
  - **`authService`** — instance partagée entre l'app et le middleware ;
  - **`requireAuth`** — middleware « avant » renvoyant `401` si non authentifié.
- Démo `examples/web_auth.okp` (login + cookie + route protégée).

### Changé
- Dépendance relevée à **`oktopios>=0.14.0`** (la requête expose désormais
  `headers`, requis pour lire cookie / Bearer).

## [0.6.0] — CLI & scaffolding

### Ajouté
- Commande **`oktopios`** (entry-point du paquet, façon `django-admin` / `symfony`) :
  - `oktopios new <projet>` — échafaude un projet complet prêt à lancer
    (`main.okp`, `controllers/`, `models/`, `templates/`, `bin/migrate.okp`,
    `.env.local` / `.env.prod`, `.gitignore`) ;
  - `oktopios make:model <Nom> [--table t]` — génère un modèle décoré ;
  - `oktopios make:controller <Nom>` — génère un contrôleur ;
  - `oktopios serve [entry]` — lance l'application (`okp main.okp`) ;
  - `oktopios migrate` — exécute `bin/migrate.okp` ;
  - `oktopios version` — affiche la version du framework.
- Module `oktopios_framework/cli.py`.

## [0.5.0] — Formulaires & validation

### Ajouté
- `oktopios_framework/forms.okp` : classe **`Form`** — lie les données d'une
  requête (`req.body`, un map) à un modèle par réflexion (`bind`), puis valide
  ses champs d'après leurs décorateurs :
  - `@NotNull` — champ requis ;
  - `@Email` — format e-mail ;
  - `@Min(n)` — valeur numérique ≥ n ;
  - `@MinLength(n)` / `@MaxLength(n)` — longueur de chaîne.
- `Form.validate(entity)` retourne la liste des erreurs (vide = valide) ;
  `Form.isValid(entity)` retourne un booléen.
- Démo `examples/forms_demo.okp` (cas invalide + cas valide).

## [0.4.0] — Middleware (pipeline avant / après)

### Ajouté
- `Router.use(mw)` : middleware **avant** `fun(req) -> réponse|null` (null = continuer,
  sinon court-circuite) — idéal pour les gardes d'authentification, le logging.
- `Router.after(mw)` : middleware **après** `fun(req, resp) -> resp` — transforme la
  réponse (ex. en-têtes CORS).
- Middlewares fournis : `logRequest` (journalise via `Log`) et `corsAllowAll`
  (ajoute `Access-Control-Allow-Origin: *`).
- Démo `examples/web_mw.okp`.

## [0.3.0] — Couche Vue : templates HTML

### Ajouté
- `oktopios_framework/view.okp` : classe **`View`** — rend des fichiers template
  d'un dossier via le namespace natif `Template`, avec **layout** optionnel
  (héritage : le rendu de la page s'insère dans `{{content}}` du layout).
- Démo `examples/web_views.okp` + templates `examples/templates/` (layout + page).

## [0.2.0] — Routing & contrôleurs

### Ajouté
- `oktopios_framework/routing.okp` : classe **`Router`** (get/post/put/delete + run)
  bâtie sur le namespace natif `Server` (oktopios >= 0.12.0), et classe
  **`Response`** (json/text/html/status/redirect) pour fabriquer les réponses.
- Démo `examples/web.okp` (routes, params, JSON, statut).
- Dépendance directe `oktopios>=0.12.0` (pour `Server`).

## [0.1.0] — ORM + configuration
- Couche ORM (via `oktopios-orm`) et configuration par environnement
  (`.env.local` / `.env.prod`).
