param([Parameter(Mandatory = $true)][string]$File)
$ErrorActionPreference = "Stop"
$name = Split-Path $File -Leaf

docker compose exec -T db sh -c "pg_restore -U `$POSTGRES_USER -d `$POSTGRES_DB --clean --if-exists --no-owner /backups/$name"
if ($LASTEXITCODE -ne 0) { throw "pg_restore reported errors" }

Write-Host "Restored $name"