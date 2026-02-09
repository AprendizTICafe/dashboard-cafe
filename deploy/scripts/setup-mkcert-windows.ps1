# Executar este script como Administrador no PowerShell
# Ele baixa mkcert, adiciona em C:\nginx\bin (cria a pasta se necessário),
# instala a CA local e gera certificados para dashboard.local.

# Verifica se está em modo administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
if (-not $isAdmin) {
    Write-Error "Execute este script como Administrador (Run as Administrator)."
    exit 1
}

$nginxBin = "C:\nginx\bin"
$certDir = "C:\nginx\certs"
$mkcertVersion = "v1.4.4"
$mkcertFileName = "mkcert-$mkcertVersion-windows-amd64.exe"
$mkcertUrl = "https://github.com/FiloSottile/mkcert/releases/download/$mkcertVersion/$mkcertFileName"
$mkcertPath = Join-Path $nginxBin "mkcert.exe"

# Cria pastas
New-Item -ItemType Directory -Force -Path $nginxBin | Out-Null
New-Item -ItemType Directory -Force -Path $certDir | Out-Null

Write-Host "Baixando mkcert de: $mkcertUrl"
try {
    Invoke-WebRequest -Uri $mkcertUrl -OutFile $mkcertPath -UseBasicParsing -ErrorAction Stop
} catch {
    Write-Error "Falha ao baixar mkcert. Verifique a URL e a conexão de rede. Erro: $_"
    exit 1
}

# Garantir permissões e executável
icacls $mkcertPath /grant Everyone:RX | Out-Null

# Adicionar ao PATH da máquina (se ainda não estiver)
$machinePath = [Environment]::GetEnvironmentVariable("PATH", [EnvironmentVariableTarget]::Machine)
if ($machinePath -notmatch ([Regex]::Escape($nginxBin))) {
    [Environment]::SetEnvironmentVariable("PATH", "$machinePath;$nginxBin", [EnvironmentVariableTarget]::Machine)
    Write-Host "Adicionado $nginxBin ao PATH da máquina. Você pode precisar reiniciar o terminal." 
}

Write-Host "Instalando CA local (mkcert -install)"
& $mkcertPath -install
if ($LASTEXITCODE -ne 0) {
    Write-Warning "mkcert -install retornou código diferente de 0. Verifique a instalação." 
}

# Gerar certificados para dashboard.local
$certFile = Join-Path $certDir "dashboard.local.pem"
$keyFile = Join-Path $certDir "dashboard.local-key.pem"
Write-Host "Gerando certificados em $certDir"
& $mkcertPath -cert-file $certFile -key-file $keyFile "dashboard.local" "127.0.0.1" "::1"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Falha ao gerar certificados com mkcert."
    exit 1
}

Write-Host "Certificados gerados com sucesso:"
Write-Host "  Cert: $certFile"
Write-Host "  Key:  $keyFile"

Write-Host "Próximo: adicione as linhas abaixo em C:\Windows\System32\drivers\etc\hosts (como Administrador):"
Write-Host "127.0.0.1   dashboard.local"
Write-Host "::1         dashboard.local"

Write-Host "Depois, ajuste o arquivo Nginx (C:/nginx/conf/) para apontar para esses certificados e reinicie o nginx.exe." 
Write-Host "Se o navegador não confiar no certificado (Firefox), ative 'security.enterprise_roots.enabled' ou importe manualmente o certificado no Firefox." 

Write-Host "Pronto. Abra um novo PowerShell (ou reinicie o terminal) e verifique com: mkcert -CAROOT e certutil -verifystore Root <CA-SubjectName>"
