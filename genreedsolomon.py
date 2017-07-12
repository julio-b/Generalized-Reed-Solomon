from sage.all import *

def generalizedReedSolomon(o,n,k):
    F = GF(o, "a")
    #####TODO set column_multipliers
    #TODO gen with num of bits
    C = codes.GeneralizedReedSolomonCode(F.list()[:n],k, [1 for i in range(n)])
    if(C.dual_code() is not None):
        C = C.dual_code()
    D = codes.decoders.GRSGaoDecoder(C)
    return C,D

def addRandomErrors(elements, err, C):
    if(isinstance(err, float)):
        Chan = channels.QarySymmetricChannel(C.ambient_space(), err)
    else:
        Chan = channels.StaticErrorRateChannel(C.ambient_space(), err)
    if(isinstance(elements,list)):
        return [ Chan.transmit_unsafe(e) for e in elements ]
    else:
        return [Chan.transmit_unsafe(elements)]
