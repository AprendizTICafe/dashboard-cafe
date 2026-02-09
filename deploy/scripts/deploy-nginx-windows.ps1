# Execute este script como Administrador no PowerShell
# Objetivo: copiar o arquivo de exemplo de configuração nginx do repositório
# para C:\nginx\conf\sites\, garantir que o nginx.conf inclua conf/sites/*.conf,
# testar a configuração do nginx e recarregar o serviço.

# Verifica se está em modo administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
if (-not $isAdmin) {
    Write-Error "Execute este script como Administrador (Run as Administrator)."
    exit 1
}

# Caminhos
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Resolve-Path (Join-Path $scriptDir "..\..")
$sourceConf = Join-Path $repoRoot 'deploy\nginx\dashboard.local.conf'
$nginxConfDir = 'C:\nginx\conf'
$sitesDir = Join-Path $nginxConfDir 'sites'
$destConf = Join-Path $sitesDir 'dashboard.local.conf'
$nginxExe = 'C:\nginx\nginx.exe'

if (-not (Test-Path $sourceConf)) {
    Write-Error "Arquivo de origem não encontrado: $sourceConf"
    exit 1
}

# Cria pasta sites se não existir
if (-not (Test-Path $sitesDir)) {
    New-Item -ItemType Directory -Path $sitesDir -Force | Out-Null
    Write-Host "Criada pasta: $sitesDir"
}

# Copia o arquivo
Copy-Item -Path $sourceConf -Destination $destConf -Force
Write-Host "Arquivo copiado para: $destConf"

# Garante que nginx.conf existe
$nginxConf = Join-Path $nginxConfDir 'nginx.conf'
if (-not (Test-Path $nginxConf)) {
    Write-Error "nginx.conf não encontrado em $nginxConfDir. Verifique a instalação do Nginx (C:\nginx)."
    exit 1
}

# Lê o conteúdo e insere include conf/sites/*.conf; dentro do bloco http se não existir
$content = Get-Content -Raw -Path $nginxConf -Encoding UTF8
if ($content -match 'include\s+conf/sites/\*\.conf;') {
    Write-Host "nginx.conf já contém 'include conf/sites/*.conf;'. Nenhuma alteração necessária."
} else {
    # Inserir a linha logo após a declaração 'http {'
    if ($content -match 'http\s*\{') {
        $newContent = $content -replace 'http\s*\{', 'http {\n    include conf/sites/*.conf;'
        # Faz backup antes de sobrescrever
        Copy-Item -Path $nginxConf -Destination ($nginxConf + '.bak') -Force
        Set-Content -Path $nginxConf -Value $newContent -Encoding UTF8
        Write-Host "Inserido 'include conf/sites/*.conf;' em $nginxConf e criado backup $($nginxConf + '.bak')"
    } else {
        Write-Warning "Não foi possível localizar o bloco 'http { }' em $nginxConf. Verifique manualmente e adicione 'include conf/sites/*.conf;' dentro do bloco http."
    }
}

# Testar configuração do nginx
if (-not (Test-Path $nginxExe)) {
    Write-Warning "nginx.exe não encontrado em C:\nginx\nginx.exe. Pule o teste automático ou ajuste o caminho no script."
    Write-Host "Configuração copiada; por favor, teste manualmente: C:\nginx\nginx.exe -t"
    exit 0
}

Write-Host "Testando configuração do Nginx..."
$test = & $nginxExe -t 2>&1
Write-Host $test
if ($LASTEXITCODE -ne 0) {
    Write-Error "Teste do Nginx falhou. Revise a saída acima e corrija eventuais erros."
    exit 1
}

# Recarregar nginx
Write-Host "Recarregando Nginx..."
& $nginxExe -s reload
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Falha ao recarregar Nginx com '-s reload'. Talvez o Nginx não esteja em execução. Inicie-o manualmente: Start-Process C:\nginx\nginx.exe"
} else {
    Write-Host "Nginx recarregado com sucesso."
}
