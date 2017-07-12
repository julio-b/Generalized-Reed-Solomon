#!/usr/bin/sage -python
from sage.all import *
import socket
import pickle
import genreedsolomon as grs
import argparse

def main():
    #TODO improve output. --verbose
    parser = argparse.ArgumentParser(description="GRS client")
    parser.add_argument("-P", "--port", default=666,type=int, dest="PORT", help="Socket port (default: 666)")
    parser.add_argument("-c", "--to-code", action='store_true', help="Decode to code instead of message")
    args = parser.parse_args()

    HOST = "localhost"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, args.PORT))
        recv = ""
        while 1:
            r = s.recv(10000)
            recv+=r
            if not r: break
        data = pickle.loads(recv)
        server_args = data[0]
        C,D = grs.generalizedReedSolomon(server_args.o, server_args.n, server_args.k, server_args.primGF)
        for i in range(len(data[1])):
            try:
                if(args.to_code):
                    di = D.decode_to_code(data[1][i])
                else:
                    di = D.decode_to_message(data[1][i])
                print "#", i, data[1][i], "decoded to", "code" if args.to_code else "msg", di
            except (sage.coding.decoder.DecodingError, ValueError) as e:
                print "#", i, data[1][i], "decode failed"
                pass
    except socket.error as se:
        print se
        print "Check that your server is running or change port (-P PORT)"
    #TODO exceptions
    except Exception as e:
        print e
        raise
    finally:
        s.close()

if __name__ == "__main__":
    main()
