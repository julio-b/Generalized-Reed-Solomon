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
        msg_ascii=""
        print "Received", len(data[1]), "messages from server!\n"
        for i in range(len(data[1])):
            try:
                if args.no_color:
                    code_str = str(data[1][i])
                else:
                    code_str = highlight_errors(data[1][i], D)
                if args.to_string:
                    msg_ascii += grs.decode_to_ascii(data[1][i], C, D)
                print "#%d {%s --decode-to-%s--> %s}" % (
                        i,
                        code_str,
                        "code" if args.to_code else "msg",
                        D.decode_to_code(data[1][i]) if args.to_code else D.decode_to_message(data[1][i]))
            except (sage.coding.decoder.DecodingError, ValueError) as e:
                print "#%d {%s DECODE FAILED!}" % (i, data[1][i])
                pass
        if args.to_string:
            print "Trying to decode messages to ascii text:"
            print msg_ascii
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
    parser = argparse.ArgumentParser(description="GRS client")
    parser.add_argument("-P", "--port", default=666,type=int, dest="PORT", help="Socket port (default: 666)")
    parser.add_argument("-c", "--to-code", action="store_true", help="Decode to code instead of message")
    parser.add_argument("-s", "--to-string", action="store_true", help="Decode also to ascii string")
    parser.add_argument("--no-color", action="store_true", help="Do not highlight errors in code")
    return parser.parse_args(args)

if __name__ == "__main__":
    main(sys.argv[1:])
