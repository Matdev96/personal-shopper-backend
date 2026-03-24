from slowapi import Limiter
from slowapi.util import get_remote_address

# Instância global do rate limiter.
# key_func=get_remote_address usa o IP do cliente como chave para contar as requisições.
# Assim cada IP tem seu próprio contador independente.
limiter = Limiter(key_func=get_remote_address)
