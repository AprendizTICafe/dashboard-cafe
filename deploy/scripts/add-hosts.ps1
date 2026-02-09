# Execute como Administrador
# Adiciona dashboard.local ao hosts

$hostsPath = 'C:\Windows\System32\drivers\etc\hosts'
$lines = @('127.0.0.1   dashboard.local', '::1         dashboard.local')

foreach ($line in $lines) {
    if (-not (Select-String -Path $hostsPath -Pattern ([regex]::Escape($line)) -SimpleMatch -Quiet)) {
        Add-Content -Path $hostsPath -Value $line
        Write-Host "Adicionado: $line"
    } else {
        Write-Host "Já existe: $line"
    }
}

Write-Host "Arquivo hosts atualizado."
Get-Content $hostsPath | Select-String dashboard
