from cryptography.fernet import Fernet
from config import Config
 
 
def _get_fernet():
    if not Config.CRYPTO_KEY:
        raise ValueError("❌ CRYPTO_KEY não encontrada no .env")
    return Fernet(Config.CRYPTO_KEY.encode())
 
 
def criptografar(senha: str) -> str:
    """Criptografa uma senha para gravar no banco."""
    return _get_fernet().encrypt(senha.encode()).decode()
 
 
def descriptografar(senha_criptografada: str) -> str:
    """Descriptografa uma senha lida do banco para usar no login."""
    return _get_fernet().decrypt(senha_criptografada.encode()).decode()
 