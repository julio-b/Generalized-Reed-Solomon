#!/usr/bin/sage -python
from sage.all import *
import socket
import pickle
import genreedsolomon as grs
import argparse

def main(argv):
    args = parseArguments(argv)
    print args
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
        C,D = grs.generalizedReedSolomon(server_args.o, server_args.n, server_args.k, server_args.primGF, server_args.column_multipliers)
        strmsg=""
        print "Received", len(data[1]), "messages from server!\n"
        for i in range(len(data[1])):
            try:
                if(args.no_color):
                    strcode = str(data[1][i])
                else: #highlight errors
                    strcode = "("
                    code = D.decode_to_code(data[1][i])
                    for c in range(len(data[1][i])):
                        if(code[c]!=data[1][i][c]):
                            strcode += "\033[6;30;41m" + str(data[1][i][c]) + "\033[0m"
                        else:
                            strcode += str(data[1][i][c])
                        strcode += ", "
                    strcode += "\b\b)"  #*, ) --> *)
                if(args.to_string):
                    strmsg += grs.decodeToAscii(data[1][i], C, D)
                print "#%d {%s --decode-to-%s--> %s}" % (i, strcode, "code" if args.to_code else "msg", D.decode_to_code(data[1][i]) if args.to_code else D.decode_to_message(data[1][i]))
            except (sage.coding.decoder.DecodingError, ValueError) as e:
                print "#%d {%s DECODE FAILED!}" % (i, data[1][i])
                pass
        if(args.to_string):
            print "Trying to decode messages to ascii text:"
            print strmsg
    except socket.error as se:
        print se
        print "Check that your server is running or change port (-P PORT)"
    except EOFError:
        print "Received empty response from server"
    #TODO exceptions
    except Exception as e:
        print e
        raise
    finally:
        s.close()

def parseArguments(args):
    parser = argparse.ArgumentParser(description="GRS client")
    parser.add_argument("-P", "--port", default=666,type=int, dest="PORT", help="Socket port (default: 666)")
    parser.add_argument("-c", "--to-code", action="store_true", help="Decode to code instead of message")
    parser.add_argument("-s", "--to-string", action="store_true", help="Decode also to ascii string")
    parser.add_argument("--no-color", action="store_true", help="Do not highlight errors in code")
    return parser.parse_args(args)

if __name__ == "__main__":
    main(sys.argv[1:])
