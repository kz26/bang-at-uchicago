import hashlib
import random
import string

def GenRandomStr(length):
    alphabet = string.letters[0:52] + string.digits
    s = str().join([random.choice(alphabet) for i in range(length)])
    return s

def GenRandomHash(s):
    salt = GenRandomStr(64)
    hasher = hashlib.sha256()
    hasher.update(s + salt)
    return hasher.hexdigest()
