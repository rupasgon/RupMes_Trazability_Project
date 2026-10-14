# RupMes Helm Deployment

## Recommended model

- Frontend and backend inside Kubernetes
- External PostgreSQL as the default production database
- Optional in-cluster PostgreSQL only for lab or small environments

## 1. Build and publish images

Backend:

```bash
docker build -t ghcr.io/your-org/rupmes-backend:1.0.0 .
docker push ghcr.io/your-org/rupmes-backend:1.0.0
```

Frontend:

```bash
docker build -t ghcr.io/your-org/rupmes-frontend:1.0.0 ./frontend
docker push ghcr.io/your-org/rupmes-frontend:1.0.0
```

The frontend image now accepts runtime configuration through environment variables, so you do not need a rebuild for each cluster environment.

## 2. Create a values file

Example `values-prod.yaml`:

```yaml
images:
  backend:
    repository: ghcr.io/your-org/rupmes-backend
    tag: "1.0.0"
  frontend:
    repository: ghcr.io/your-org/rupmes-frontend
    tag: "1.0.0"

frontend:
  runtimeConfig:
    apiUrl: "https://api-rupmes.example.local"
    defaultLang: es

backend:
  env:
    frontendOrigins: "https://rupmes.example.local"
    cookieSecure: true
    cookieDomain: ".example.local"
    multiTenantEnabled: true
    defaultTenantId: DEFAULT

database:
  external:
    enabled: true
    url: "postgresql+psycopg2://rupmes_user:password@postgres.example.local:5432/mes_db"
  internal:
    enabled: false

migrationJob:
  enabled: true
  seed: false

ingress:
  enabled: true
  className: nginx
  frontendHost: rupmes.example.local
  backendHost: api-rupmes.example.local
  tls:
    enabled: true
    frontendSecretName: rupmes-frontend-tls
    backendSecretName: rupmes-backend-tls
```

Create the backend secret before the first release instead of storing database or ingest credentials in the values file:

```bash
kubectl create secret generic rupmes-rupmes-backend -n rupmes \
  --from-literal=DATABASE_URL='postgresql+psycopg2://rupmes_user:password@postgres.example.local:5432/mes_db' \
  --from-literal=PRODUCTION_INGEST_API_KEY='optional-legacy-global-key' \
  --from-literal=INTEGRATION_SECRETS_KEY='a-32-byte-url-safe-base64-fernet-key'
```

`PRODUCTION_INGEST_API_KEY` is optional and retained for legacy integrations. For new equipment, create individual clients in **Administration > Integrations** and use their `X-Client-Id` and `X-API-Key` credentials.

`INTEGRATION_SECRETS_KEY` is required before storing OAuth client credentials from the ERP server screen. Keep the same key for the life of the deployment; changing it makes previously configured credentials unreadable.

## 3. Deploy

```bash
helm upgrade --install rupmes ./deploy/helm/rupmes -n rupmes --create-namespace -f values-prod.yaml
```

## 3b. Automated Windows deployment

For the environment used in this project you can automate build, push and deploy with:

```powershell
.\scripts\deploy-k3s.ps1 -Version 1.0.1 -KubeConfigPath "$HOME\.kube\rupmes-k3s.yaml"
```

Useful options:

- `-SkipBackend` if only the frontend changed
- `-SkipFrontend` if only the backend changed
- `-SkipPush` if the images are already in Harbor
- `-RenderOnly` to validate Helm rendering without deploying
- `-HelmPath "C:\path\to\helm.exe"` if Helm is not in `PATH`

## 4. Notes

- If your database is empty, set `migrationJob.seed=true` only for the first install.
- For production, keep `backend.env.runDbMigrations=false` and `backend.env.runDbSeed=false`; use the Helm migration job instead.
- If you want PostgreSQL inside the cluster, set `database.external.enabled=false` and `database.internal.enabled=true`.
- Set `backend.env.cookieDomain` only when portal and API use subdomains of the same parent domain, for example `.example.local`. Leave it empty for a single host or local development.
- Use a new immutable image tag for every release. The portal footer exposes the deployed web and API versions for verification.
