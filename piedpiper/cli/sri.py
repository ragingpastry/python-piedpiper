import argparse
import hashlib
import sys
import piedpiper.sri as sritool


def main():
    parser = argparse.ArgumentParser('SubResource Integrity(SRI) Tool',
                                     description='Calculates the digest of a file '
                                                 'and generates an SRI string')

    parser.add_argument('--url-safe',
                        action='store_true',
                        help='Assume a URL safe base64 encoded SRI: decodes to an SRI'
                             ' of format sha256-myhash')

    subparsers = parser.add_subparsers(help='encode or decode',
                                       required=True,
                                       dest='command')

    gen = subparsers.add_parser('generate')

    gen.add_argument('file')
    gen.add_argument('--dgst',
                     default='sha256',
                     choices=hashlib.algorithms_available,
                     help='digest algorithm see: openssl dgst')

    verify = subparsers.add_parser('verify')

    verify.add_argument('file')
    verify.add_argument('sri')

    decoder = subparsers.add_parser('decode')
    decoder.add_argument('sri')

    opts = parser.parse_args()

    if opts.command == 'generate':
        print(str(sritool.generate_sri(opts.file,
                                       dgst=opts.dgst,
                                       url_safe=opts.url_safe)))
    elif opts.command == 'verify':
        if opts.url_safe:
            claimed = sritool.urlsafe_to_hash(opts.sri)
        else:
            claimed = sritool.sri_to_hash(opts.sri)

        real = sritool.generate_sri(opts.file, claimed.algorithm)

        print(f'{str(real)}\nurlsafeb64: {sritool.hash_to_urlsafeb64(real)}')

        if str(real) != str(claimed):
            print(f'{opts.file}: {str(real)} != {str(claimed)}', file=sys.stderr)
            sys.exit(1)
    elif opts.command == 'decode':
        print(str(sritool.urlsafe_to_hash(opts.sri)))
