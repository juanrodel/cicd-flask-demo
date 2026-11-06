$ErrorActionPreference = "Stop"
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
New-Item -ItemType Directory -Force -Path backups | Out-Null

docker compose exec -T db sh -c "pg_dump -U `$POSTGRES_USER -d `$POSTGRES_DB -Fc -f /backups/notes-$stamp.dump"
if ($LASTEXITCODE -ne 0) { throw "pg_dump failed" }

Write-Host "Backup written to backups\notes-$stamp.dump"