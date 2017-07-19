# Generalized-Reed-Solomon
## Steps
1. `chmod u+x server.py`
1. `chmod u+x client.py`
1. `./server.py -Dqo15 -n13 -k8 -m24 -E 2 6`
1. `Open a new terminal: ./client.py`

## Help
### Server

```
usage: server.py [-h] -o O [-q] -n N -k K [-D] [--clmns I1 [I2 ...]]
                 [--list-gf] [-m MSGNUM] [-e ERROR | -E E0 E1 | -p ERROR]
                 [-P PORT]
                 [infile]

Generalized Reed-Solomon, Server Side

positional arguments:
  infile                Encode and send this file also (use - for stdin,
                        default: None)

optional arguments:
  -h, --help            show this help message and exit
  -o O, --order O       GRS Galois field order
  -q, --primary         Set GRS Galois field order to next primary
  -n N                  GRS evaluation points (length of the code, n<=o)
  -k K                  GRS dimension (length of the message, k<n)
  -D, --dual-code       Use dual code (message length will be n-k)
  --clmns I1 [I2 ...], --column-multipliers I1 [I2 ...]
                        Specify GRS column multipliers, a list of indexes over
                        GF (see --list-gf, ex: -o4 -n4 -k3 --clmns 2 3 1 2,
                        default: all 1)
  --list-gf             List Galois field and exit
  -m MSGNUM, --messages MSGNUM
                        Number of messages to send
  -e ERROR              The number of errors created in each encoded message
                        (default: 0, only one of the -e,-E,-p can be used)
  -E E0 E1              Random number of errors (between E0 and E1) will be
                        created in each encoded message (ex: -E 0 3)
  -p ERROR              Error probabillity (float in [0,1), ex: -p0.2)
  -P PORT, --port PORT  Socket port (default: 666)

Example: ./server.py -Dqo15 -n13 -k8 -m24 -E 2 6
```

### Client

```
usage: client.py [-h] [-P PORT] [--no-color] [-c] [-m] [-s]

Generalized Reed-Solomon, Client Side

optional arguments:
  -h, --help            show this help message and exit
  -P PORT, --port PORT  Socket port (default: 666)
  --no-color            Do not highlight errors in code
  -c, --to-code         Decode to code
  -m, --unencode        Display message as vector instead of polynomial
  -s, --to-string       Decode all messages to ascii text

```
