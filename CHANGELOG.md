# Changelog

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
