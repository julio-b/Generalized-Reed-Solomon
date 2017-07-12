from sage.all import *

def generalizedReedSolomon(o, n, k, q, clms):
    if( q and not is_prime(o) ):
        o = next_prime(o)
    F = GF(o, "a")
    if(clms is None):
        columns = [1 for i in range(n)]
    else:
        columns = [F.list()[i] for i in clms]
    #TODO gen with num of bits
    C = codes.GeneralizedReedSolomonCode(F.list()[:n], k, columns)
    if(C.dual_code() is not None):
        C = C.dual_code()
    D = codes.decoders.GRSGaoDecoder(C)
    return C,D

def addRandomErrors(elements, err, C):
    if(isinstance(err, float)):
        Chan = channels.QarySymmetricChannel(C.ambient_space(), err)
    else:
        Chan = channels.StaticErrorRateChannel(C.ambient_space(), err)
    if( not isinstance(elements, list)):
        elements = [elements]
    return [ Chan.transmit_unsafe(e) for e in elements ]
