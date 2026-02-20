import logging

# O logger ajuda a ver no terminal mesmo se o print falhar em alguns ambientes
logger = logging.getLogger(__name__)

def redirect_by_department(strategy, details, response, user=None, *args, **kwargs):
    # 1. Imprime uma linha de destaque para achar fácil no terminal
    print("\n" + "="*50)
    print("DEBUG: DADOS RECEBIDOS DA MICROSOFT")
    
    # 2. Imprime o dicionário response completo
    print(response) 
    
    print("="*50 + "\n")

    # Por enquanto, não redireciona, só deixa o fluxo seguir para você ver o log
    return