// Função para login com Microsoft
        function loginWithMicrosoft(url) {
            showLoading(true);
            showError('');
            
            // Substitua pela sua URL de callback/endpoint do Django
            const microsoftLoginUrl = url || '/auth/microsoft/login/';
            
            setTimeout(() => {
                try {
                    // Redireciona para o endpoint de autenticação
                    window.location.href = microsoftLoginUrl;
                } catch (error) {
                    showError('Erro ao conectar com Microsoft. Tente novamente.');
                    showLoading(false);
                }
            }, 500);
        }

        // Funções auxiliares para mensagens
        function showError(message) {
            const errorDiv = document.getElementById('errorMessage');
            if (message) {
                errorDiv.textContent = message;
                errorDiv.classList.add('show');
            } else {
                errorDiv.classList.remove('show');
            }
        }

        function showSuccess(message) {
            const successDiv = document.getElementById('successMessage');
            if (message) {
                successDiv.textContent = message;
                successDiv.classList.add('show');
            } else {
                successDiv.classList.remove('show');
            }
        }

        function showLoading(isLoading) {
            const loading = document.getElementById('loading');
            const form = document.getElementById('loginForm');
            
            if (isLoading) {
                loading.style.display = 'block';
                form.style.display = 'none';
            } else {
                loading.style.display = 'none';
                form.style.display = 'block';
            }
        }

        // Verifica se há parâmetros de erro na URL (ex: ?error=invalid_credentials)
        window.addEventListener('DOMContentLoaded', function() {
            const params = new URLSearchParams(window.location.search);
            const error = params.get('error');
            const success = params.get('success');
            
            if (error) {
                showError(decodeURIComponent(error));
            }
            if (success) {
                showSuccess(decodeURIComponent(success));
            }
        });