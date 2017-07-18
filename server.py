#!/usr/bin/sage -python
from sage.all import *
import sys
import thread
import socket
import pickle
import genreedsolomon as grs
import argparse

def main(argv):
    args = parseArguments(argv)
    try:
        C,D = grs.generalizedReedSolomon(args.o, args.n, args.k, args.primGF, args.dual_code, args.column_multipliers)
        printInfos(C, D)
        if(args.listGF):
            listGF(C)
            return
        UserInput = []
        if(args.infile != None):
            UserInput = readUserInput(args, C)
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
            thread.start_new_thread(send2Client, (conn, addr, args, C, UserInput))
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

def send2Client(client, address, args, C, nonrandmsg):
    print "New client @", address
    try:
        msg = [C.random_element() for i in range(args.msgnum)]
        msg += nonrandmsg
        print "Sending", len(msg), "messages to", address
        for i in range(len(msg)):
            print "#%d {%s}" % (i, msg[i])
        err = grs.addRandomErrors(msg, args.error, C)
        client.send( pickle.dumps((args, err)))
    except ValueError as ve:
        print "ERROR:", ve, ", your error argument is:", args.error
        return
    except Exception as e:
        print e
    finally:
        client.close()

def printInfos(C, D):
    print "Generalized" if C.is_generalized() else "", "Reed-Solomon code generated successfully!"
    print "Minimun distance:", C.minimum_distance()
    print "Max number of error", D.decoding_radius()

def listGF(C):
    print "GRS base field:", C.base_field()
    print "\tIndex\tElement"
    for n, e in enumerate( C.base_field() ):
        print "\t", n, "\t", e

def readUserInput(args, C):
    print "Reading message from", args.infile.name, ", CTRL-D CTRL-D when you're done" if args.infile==sys.stdin else "", ":"
    UserInput = grs.encodeFile(args.infile, C)
    if(args.infile != sys.stdin):
        args.infile.seek(0)
        print args.infile.read()
    return UserInput

def parseArguments(args):
    parser = argparse.ArgumentParser(description="Generalized Reed-Solomon",
            epilog="Examples: server.py -qo59 -n40 -k12 -p0.23")
    parser.add_argument("-o", "--order", required=True, type=int, dest="o", help="GRS finite field's order")
    parser.add_argument("-q", "--primary", action="store_true", dest="primGF", help="Set GRS finite field's order to next primary")
    parser.add_argument("-n", required=True, type=int, dest="n", help="GRS evaluation points")
    parser.add_argument("-k", required=True, type=int, dest="k", help="GRS dimension")
    parser.add_argument("-m", "--messages", default=20, type=int, dest="msgnum", help="Number of messages to send")
    parser.add_argument("-D", "--dual-code", action="store_true", help="Use dual code")
    parser.add_argument("--column-multipliers", "--clmns", nargs="+", metavar=("I1","I2"), type=int, help="Specify GRS column multipliers, a list of indexes over GF (see --list-gf, ex:  --clmns 3 4 1, default: all 1)")
    parser.add_argument("--list-gf", action="store_true", dest="listGF", help="List finite field and exit")
    error_group = parser.add_mutually_exclusive_group()
    error_group.add_argument("-e", default=0, type=int, dest="error", help="Number of errors added to each message (default: 0)")
    error_group.add_argument("-E", type=int, nargs=2, metavar=("E0", "E1"), dest="error", help="Random number (between E0 and E1) of errors added to each message")
    error_group.add_argument("-p", type=float, choices=[Range(0.0, 1.0)], metavar="ERROR", dest="error", help="Error probabillity")
    parser.add_argument("-P", "--port", default=666,type=int, dest="PORT", help="Socket port (default: 666)")
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
        return '{0}-{1}'.format(self.start, self.end)

if __name__ == "__main__":
    main(sys.argv[1:])
