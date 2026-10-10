# PowerShell rollback helper
$env:DATABASE_URL='postgresql+psycopg2://rupmes:rupmes@localhost:5432/mes_db'
python -m alembic downgrade -1