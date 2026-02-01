"""
Provenance signature helpers.

Provides HMAC signing/verification and optional RSA (PKI) signing if the
`cryptography` package is available. Designed to be lightweight and optional.
"""
from typing import Optional
import hmac
import hashlib


def create_hmac_signature(message: str, key: str, digest: str = 'sha256') -> str:
    """Create an HMAC signature (hex) for a message using the given key."""
    if isinstance(message, str):
        message = message.encode('utf-8')
    if isinstance(key, str):
        key = key.encode('utf-8')
    hm = hmac.new(key, message, getattr(hashlib, digest))
    return hm.hexdigest()


def verify_hmac_signature(message: str, key: str, signature: str, digest: str = 'sha256') -> bool:
    """Verify HMAC signature in constant-time.

    Returns True if signature matches, False otherwise.
    """
    expected = create_hmac_signature(message, key, digest=digest)
    return hmac.compare_digest(expected, signature)


try:
    # Optional RSA signing using cryptography if installed
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
    from cryptography.hazmat.primitives.asymmetric import rsa


    def create_rsa_signature(message: str, private_key_pem: bytes, password: Optional[bytes] = None) -> bytes:
        """Sign message with RSA private key (PEM). Returns raw signature bytes."""
        if isinstance(message, str):
            message = message.encode('utf-8')
        pk = load_pem_private_key(private_key_pem, password=password)
        sig = pk.sign(
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        return sig


    def verify_rsa_signature(message: str, public_key_pem: bytes, signature: bytes) -> bool:
        """Verify RSA signature. Returns True on success, raises on failure."""
        if isinstance(message, str):
            message = message.encode('utf-8')
        pub = load_pem_public_key(public_key_pem)
        try:
            pub.verify(
                signature,
                message,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

except Exception:
    # cryptography not available; rsa helpers not present
    def create_rsa_signature(*args, **kwargs):
        raise ImportError('cryptography package is required for RSA signatures')

    def verify_rsa_signature(*args, **kwargs):
        raise ImportError('cryptography package is required for RSA signatures')
