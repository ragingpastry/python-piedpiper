import base64
import hashlib
import os
import subresource_integrity as integrity


def hash_to_urlsafeb64(hash):
    assert isinstance(hash, integrity.Hash), 'to_urlsafe encodes a Hash to urlsafe b64'
    return base64.urlsafe_b64encode(str(hash).encode('ascii')).decode('utf-8')


def urlsafe_to_hash(value):
    """Convert a urlsafe_b64encode'd string to and integrity.Hash object"""
    assert isinstance(value, str), 'decodes urlsafe b64 to a Hash'
    value = base64.urlsafe_b64decode(value.encode('ascii')).decode('utf-8')
    return integrity.parse(value)[0]


def hash_to_sri_hash(dgst, hash):
    """Coverts a b64 encoded binary hash string to subresource_integrity.Hash"""
    if isinstance(hash, str):
        hash = hash.encode('ascii')

    if isinstance(hash, bytes):
        return integrity.Hash(dgst, hash)
    else:
        raise ValueError('hash is not a bytes or str can\'t encode')


def hash_file(dgst, path):
    """Generate a dgst hash from file path"""
    h = hashlib.new(dgst)

    with open(path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b""):
            h.update(chunk)
    return h.digest()


def b64_hash(bhash):
    """Converts a bhash to b64encoded hash for manual sri generation"""
    assert isinstance(bhash, bytes)
    return base64.b64encode(bhash)


def generate_sri(path, dgst='sha256', url_safe=False):
    """Generate an SRI from a file path"""
    path = os.path.realpath(path)
    bhash = hash_file(dgst, path)
    hash = hash_to_sri_hash(dgst, bhash)
    return hash_to_urlsafeb64(hash) if url_safe else hash
