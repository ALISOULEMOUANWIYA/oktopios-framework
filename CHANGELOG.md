# Changelog

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
