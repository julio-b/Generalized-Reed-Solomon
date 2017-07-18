from sage.all import *

def generalized_reed_solomon(o, n, k, prime=False, dual=False, clms=None):
    if prime and not is_prime(o):
        o = next_prime(o)
    F = GF(o, "w")
    if n>o: print "Warning: you set -n=%d > -o=%d, Using n=%d" % (n, o, o)
    try:
        if clms is None:
            C = codes.GeneralizedReedSolomonCode(F.list()[:n], k)
        else:
            columns = [F.list()[i] for i in clms]
            C = codes.GeneralizedReedSolomonCode(F.list()[:n], k, columns)
    except IndexError as ie:
        raise IndexError("Column multipliers indexes are out of range")
    if dual and C.dual_code() is not None:
        C = C.dual_code()
    D = codes.decoders.GRSGaoDecoder(C)
    return C,D

def add_random_errors(elements, err, C):
    if isinstance(err, float):
        Chan = channels.QarySymmetricChannel(C.ambient_space(), err)
    else:
        Chan = channels.StaticErrorRateChannel(C.ambient_space(), err)
    if not isinstance(elements, list):
        elements = [elements]
    return [ Chan.transmit_unsafe(e) for e in elements ]

def encode_ascii_to_code(s, C):
    v = vector(C.base_field(), [C.base_field().list()[ord(i)] for i in s])
    return C.encode(v)

def encode_file(f, C):
    codeslist=[]
    b = [0]*C.dimension()
    buff = bytearray(b)
    try:
        while f.readinto(buff) == C.dimension():
            codeslist.append(encode_ascii_to_code(str(buff), C))
            buff = bytearray(b)
        if buff.count('\x00') != len(buff):
            codeslist.append(encode_ascii_to_code(str(buff), C))
    except IndexError as ie:
        raise Exception("GRS finite fields order is not big enough to encode your text (Try -o128 or -o256 for ascii)")
    return codeslist

def decode_to_ascii(c, C, D):
    m = D.decode_to_message(c)
    s = [chr(C.base_field().list().index(i)) for i in m]
    return ''.join(s)
