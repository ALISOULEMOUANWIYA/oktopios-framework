# Déploiement en production 🚀

Guide pour mettre une application **oktopios-framework** en ligne.

## 1. Ce qu'il faut savoir

- Le serveur HTTP intégré (namespace `Server`) est **multi-thread** depuis
  `oktopios>=0.17.1` : il traite les requêtes concurrentes en parallèle.
- En production, place-le **derrière un reverse-proxy** (nginx, Caddy,
  Traefik) qui gère le **TLS/HTTPS**, la compression et les fichiers statiques.
- Configure l'app par **variables d'environnement** (plutôt que des secrets
  dans `.env.prod` versionné).

Variables reconnues par les apps générées :

| Variable | Rôle | Valeur en conteneur |
|---|---|---|
| `OKTOPIOS_HOST` | interface d'écoute | `0.0.0.0` (indispensable) |
| `OKTOPIOS_PORT` | port d'écoute | `8000` |

## 2. Avec Docker (recommandé)

`oktopios new --full` génère déjà un **`Dockerfile`** et un `.dockerignore`.

```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir oktopios-framework
COPY . /app
ENV OKTOPIOS_HOST=0.0.0.0
ENV OKTOPIOS_PORT=8000
EXPOSE 8000
CMD ["python", "-m", "vm.main", "main.okp"]
```

Construire et lancer :

```bash
docker build -t monblog .
docker run -p 8000:8000 monblog
```

→ l'app est sur `http://localhost:8000`.

### Base de données persistante

SQLite écrit un fichier (`*.db`). Pour le conserver entre redémarrages, monte un
volume et place la base dedans :

```bash
docker run -p 8000:8000 -v oktopios_data:/app/var monblog
```

(et dans l'app, un `DB = "var/app.db"`). L'exemple scaffoldé recrée la base à
chaque démarrage — pour la prod, retire le `File.remove(DB)` de `main.okp`.

## 3. Reverse-proxy TLS (nginx)

```nginx
server {
    listen 443 ssl;
    server_name exemple.com;
    ssl_certificate     /etc/letsencrypt/live/exemple.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/exemple.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $remote_addr;
    }
}
```

## 4. Monter en charge

Le serveur intégré suffit pour de nombreux cas. Pour plus de trafic, lance
**plusieurs conteneurs** sur des ports différents et répartis la charge via le
reverse-proxy (`upstream`) :

```nginx
upstream oktopios {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
}
server {
    listen 80;
    location / { proxy_pass http://oktopios; }
}
```

Chaque instance ayant sa propre mémoire (sessions auth, flash), utilise des
sessions partagées (ex. en base) si tu répartis sur plusieurs instances — ou
active l'affinité de session (`ip_hash`) côté proxy.

## 5. Sans Docker

```bash
pip install oktopios-framework
export OKTOPIOS_HOST=0.0.0.0 OKTOPIOS_PORT=8000   # (set ... sous Windows)
python -m vm.main main.okp
```

Gère le processus avec `systemd`, `supervisor` ou `pm2`, et place nginx devant
pour le TLS.
