#!/usr/bin/sage -python
from sage.all import *
import socket
import pickle
import genreedsolomon as grs
import argparse

def main(argv):
    args = parse_arguments(argv)
    HOST = "localhost"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, args.PORT))
        data = pickle.loads(recv_all(s))
        server_args = data[0]
        C,D = grs.generalized_reed_solomon(
                server_args.o,
                server_args.n,
                server_args.k,
                server_args.prime_GF,
                server_args.dual_code,
                server_args.column_multipliers)
        print "Received", len(data[1]), "messages from server!\n"
        print_messages(data[1], args, C, D)
    except socket.error as se:
        print se
        print "Check that your server is running or change port (-P PORT)"
    except EOFError:
        print "Received empty response from server"
    except Exception as e:
        print e
        raise
    finally:
        s.close()

def recv_all(s):
    recv = ""
    while 1:
        r = s.recv(10000)
        recv += r
        if not r: break
    return recv

def print_messages(codes, args, C, D):
    msg_ascii=""
    for i in range(len(codes)):
        try:
            print "#%d {\n %s %s %s %s %s\n}" % (
                    i,
                    str(codes[i]) if args.no_color else highlight_errors(codes[i], D),
                    "--decode-to-code->\n" if args.to_code else "\b",
                    D.decode_to_code(codes[i]) if args.to_code else "\b",
                    "--decode-to-msg->\n",
                    C.unencode(D.decode_to_code(codes[i])) if args.unencode else D.decode_to_message(codes[i]))
            if args.to_string:
                msg_ascii += grs.decode_to_ascii(codes[i], C, D)
        except (sage.coding.decoder.DecodingError, ValueError) as e:
            print "#%d [%s DECODE FAILED!]" % (i, codes[i])
            pass
    if args.to_string:
        print "\nTrying to decode messages to ascii text:"
        print msg_ascii

def highlight_errors(errcode, D):
    code_str = "("
    code = D.decode_to_code(errcode)
    for c in range(len(errcode)):
        if code[c] != errcode[c]:
            code_str += "\033[6;30;41m" + str(errcode[c]) + "\033[0m"
        else:
            code_str += str(errcode[c])
        code_str += ", "
    code_str += "\b\b)"  #*, ) --> *)
    return code_str

def parse_arguments(args):
    parser = argparse.ArgumentParser(description="Generalized Reed-Solomon, Client Side")
    parser.add_argument("-P", "--port", default=666, type=int, dest="PORT", help="Socket port (default: 666)")
    parser.add_argument("--no-color", action="store_true", help="Do not highlight errors in code")
    parser.add_argument("-c", "--to-code", action="store_true", help="Decode to code")
    parser.add_argument("-m", "--unencode", action="store_true", help="Display message as vector instead of polynomial")
    parser.add_argument("-s", "--to-string", action="store_true", help="Decode all messages to ascii text")
    return parser.parse_args(args)

if __name__ == "__main__":
    main(sys.argv[1:])
