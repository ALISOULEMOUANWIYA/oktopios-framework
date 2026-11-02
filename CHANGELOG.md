# Changelog

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
