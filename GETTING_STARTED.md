# Prise en main — l'écosystème Oktopios 🐙

Ce guide part de zéro et aboutit à une **application web complète qui tourne**,
en combinant les trois couches de l'écosystème :

| Couche | Paquet PyPI | Rôle | Équivalent |
|---|---|---|---|
| Langage | [`oktopios`](https://pypi.org/project/oktopios/) | interpréteur `.okp` | Python / PHP |
| ORM | [`oktopios-orm`](https://pypi.org/project/oktopios-orm/) | modèles, migrations, relations | Django ORM / Doctrine |
| Framework | [`oktopios-framework`](https://pypi.org/project/oktopios-framework/) | MVC web (routing, vues, auth…) | Django / Symfony |

---

## 1. Installation

Un seul paquet suffit : installer le framework tire automatiquement l'ORM et le
langage.

```bash
pip install oktopios-framework
```

> **Windows — si `pip` affiche « Fatal error in launcher »** : ton lanceur
> `pip.exe` est cassé (souci d'installation Python, pas d'Oktopios). Utilise
> `python -m pip install oktopios-framework`. De manière générale sous Windows,
> `python -m <outil>` contourne tous les lanceurs `.exe` capricieux.

Vérifier :

```bash
python -m oktopios_framework version
```

---

## 2. Créer une application complète

```bash
python -m oktopios_framework new --full monblog
cd monblog
```

`new --full` génère une application MVC **prête à tourner** :

```
monblog/
├── main.okp                 # point d'entrée (migration + routeurs + run)
├── models/article.okp       # modèle décoré + validation
├── controllers/
│   ├── articles.okp         # liste, détail, création
│   └── auth.okp             # login, logout
├── templates/               # layout.html, list.html, show.html
├── bin/migrate.okp
└── .env.local / .env.prod
```

(Pour un squelette minimal à la place, utilise `new` sans `--full`.)

---

## 3. Lancer

```bash
python -m oktopios_framework serve --port 8080
```

Ouvre **http://localhost:8080/**. Tu verras la liste des articles (un article de
départ est créé automatiquement).

> **Port** : par défaut `8000`. Sous Windows, `8000` est parfois réservé
> (Hyper-V / WSL / Docker) et provoque `WinError 10013` — d'où `--port 8080`
> ci-dessus. L'app lit la variable `OKTOPIOS_PORT`, donc
> `set OKTOPIOS_PORT=8080` puis `python -m vm.main main.okp` marche aussi.

### Parcours de démonstration

1. `http://localhost:8080/` — la liste
2. `http://localhost:8080/login?user=admin&pw=admin123` — ouvre une session (cookie)
3. `http://localhost:8080/admin/create?titre=Bonjour&contenu=Mon%20billet` —
   crée un article (route **protégée** : 401 sans session)
4. Reviens sur `/` — l'article apparaît.

---

## 4. Les couches, en pratique

### Modèle + ORM (oktopios-orm)

```okp
@Entity("articles")
class Article {
    @Id var id: int
    @NotNull @MinLength(3) @Column("titre") var titre: string
    @Column("contenu") var contenu: string
    @ManyToOne("Auteur") var auteur: any      // relation -> colonne auteur_id
}

var repo = new Repo("app.db", new Article())
repo.save(article)            // insère, réaffecte article.id
repo.find(1)                  // charge l'article + son auteur
repo.page(10, 2)             // pagination : page 2, 10 par page
```

### Routing + contrôleurs

```okp
var router = new Router()
router.use(logRequest)              // middleware
router.get("/articles/:id", montrer)
router.run(8000)
```

Un contrôleur `(req) -> réponse` reçoit `{ method, path, query, params, headers, body }`
et renvoie une chaîne (HTML) ou `res.json(...)` / `res.status(...)` / `res.redirect(...)`.

### Vues (templates)

```okp
var vue = new View("templates")
vue.setLayout("layout.html")                       // {{content}}
vue.render("list.html", { "titre": "Accueil" })    // {{titre}}
```

### Validation de formulaire

```okp
var form = new Form()
form.bind(article, req["query"])     // remplit l'objet depuis la requête
form.validate(article)               // liste d'erreurs (@NotNull/@Email/@Min…)
```

### Authentification

```okp
var token = authService.login("admin")             // session
authService.check(req)                              // utilisateur courant | null
router.use(requireAuth)                             // garde : 401 si non connecté
```

### Pagination & flash

```okp
var pager = new Paginator(repo, 10)
pager.links(pager.pageFrom(req), "/")               // barre Précédent/Suivant

flash.add(authService.tokenFromRequest(req), "success", "Article cree")
flash.render(authService.tokenFromRequest(req))     // affiche une fois puis vide
```

L'exemple **`examples/blog_avance.okp`** combine relations + pagination + flash +
auth dans une seule application.

---

## 5. Configuration par environnement

`.env.local` (dev) et `.env.prod` (prod), façon Symfony :

```okp
var cfg = new Config()
cfg.load("local")            // lit .env.local ("prod" -> .env.prod)
print(cfg.get("DB_PATH"))
```

---

## 6. Générateurs (CLI)

```bash
python -m oktopios_framework make:model Produit --table produits
python -m oktopios_framework make:controller Panier
python -m oktopios_framework migrate
```

(Une fois les lanceurs `.exe` sains, les commandes courtes `oktopios …` et
`okp …` fonctionnent aussi.)

---

## 7. Aller plus loin

- Chaque dépôt a son `README.md` et son `CHANGELOG.md`.
- Les trois dépôts ont une **CI GitHub Actions** qui lance `pytest` à chaque push.
- Exemples : `examples/` (blog complet, blog avancé, vues, middleware, auth…).

Bon développement ! 🐙
