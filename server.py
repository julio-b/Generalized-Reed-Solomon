#!/usr/bin/sage -python
from sage.all import *
import sys
import thread
import socket
import pickle
import genreedsolomon as grs
import argparse

def main(argv):
    args = parse_arguments(argv)
    try:
        C,D = grs.generalized_reed_solomon(
                args.o,
                args.n,
                args.k,
                args.prime_GF,
                args.dual_code,
                args.column_multipliers)
        print_infos(C, D)
        if args.list_GF:
            list_GF(C)
            return
        user_input = []
        if args.infile != None:
            user_input = read_user_input(args, C)
        del args.infile
    except KeyboardInterrupt:
        print "Terminating"
        return
    except (ValueError, IndexError) as vie:
        print "Error:", vie
        print "GRS code generation failed. Check your arguments. Use -h for help"
        return
    except Exception as e:
        print e
        return

    HOST = "localhost"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print ""
    try:
        s.bind((HOST, args.PORT))
        s.listen(5)
        print "Server started"
        while 1:
            conn, addr = s.accept()
            thread.start_new_thread(send_to_client, (conn, addr, args, C, user_input))
    except KeyboardInterrupt:
        print "Terminating server"
    except socket.error as se:
        print se
        print "Check that your specified port", args.PORT, "is available. Use -P to change it"
    except Exception as e:
        print e
        raise
    finally:
        print "Socket closed"
        s.close()

def send_to_client(client, address, args, C, non_rand_msg):
    print "New client @", address
    try:
        msg = [C.random_element() for i in range(args.msgnum)]
        msg += non_rand_msg
        print "Sending", len(msg), "messages to", address
        for i in range(len(msg)):
            print "#%d {%s}" % (i, msg[i])
        err = grs.add_random_errors(msg, args.error, C)
        client.send(pickle.dumps((args, err)))
    except ValueError as ve:
        print "ERROR:", ve, ", your error argument is:", args.error
        return
    except Exception as e:
        print e
    finally:
        client.close()

def print_infos(C, D):
    print "Generalized" if C.is_generalized() else "", "Reed-Solomon code generated successfully!"
    print "Code length", C.length()
    print "Message length", C.dimension()
    print "Minimun distance:", C.minimum_distance()
    print "Max number of error", D.decoding_radius()

def list_GF(C):
    print "GRS base field:", C.base_field()
    print "\tIndex\tElement"
    for n, e in enumerate(C.base_field() ):
        print "\t", n, "\t", e

def read_user_input(args, C):
    print "Reading message from", args.infile.name, ", CTRL-D CTRL-D when you're done" if args.infile==sys.stdin else "", ":"
    user_input = grs.encode_file(args.infile, C)
    if args.infile != sys.stdin:
        args.infile.seek(0)
        print args.infile.read()
    return user_input

def parse_arguments(args):
    parser = argparse.ArgumentParser(description="Generalized Reed-Solomon, Server Side",
            epilog="Example: ./server.py -Dqo15 -n13 -k8 -m24 -E 2 6")
    parser.add_argument("-o", "--order", required=True, type=int, dest="o", help="GRS Galois field order")
    parser.add_argument("-q", "--primary", action="store_true", dest="prime_GF", help="Set GRS Galois field order to next primary")
    parser.add_argument("-n", required=True, type=int, dest="n", help="GRS evaluation points (length of the code, n<=o)")
    parser.add_argument("-k", required=True, type=int, dest="k", help="GRS dimension (length of the message, k<n)")
    parser.add_argument("-D", "--dual-code", action="store_true", help="Use dual code (message length will be n-k)")
    parser.add_argument("--clmns", "--column-multipliers", dest="column_multipliers", nargs="+", metavar=("I1","I2"), type=int, help="Specify GRS column multipliers, a list of indexes over GF (see --list-gf, ex: -o4 -n4 -k3 --clmns 2 3 1 2, default: all 1)")
    parser.add_argument("--list-gf", action="store_true", dest="list_GF", help="List Galois field and exit")
    parser.add_argument("-m", "--messages", default=20, type=int, dest="msgnum", help="Number of messages to send")
    error_group = parser.add_mutually_exclusive_group()
    error_group.add_argument("-e", default=0, type=int, dest="error", help="The number of errors created in each encoded message (default: 0, only one of the -e,-E,-p can be used)")
    error_group.add_argument("-E", type=int, nargs=2, metavar=("E0", "E1"), dest="error", help="Random number of errors (between E0 and E1) will be created in each encoded message (ex: -E 0 3)")
    error_group.add_argument("-p", type=float, choices=[Range(0.0, 1.0)], metavar="ERROR", dest="error", help="Error probabillity (float in [0,1), ex: -p0.2)")
    parser.add_argument("-P", "--port", default=666, type=int, dest="PORT", help="Socket port (default: 666)")
    parser.add_argument("infile", nargs="?", type=argparse.FileType("r"), help="Encode and send this file also (use - for stdin, default: None)")
    return parser.parse_args(args)

#copied from https://stackoverflow.com/a/12117089
class Range(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end
    def __eq__(self, other):
        return self.start <= other < self.end
    def __repr__(self):
        return "{0}-{1}".format(self.start, self.end)

if __name__ == "__main__":
    main(sys.argv[1:])
