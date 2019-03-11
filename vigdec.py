#!/usr/bin/env python3
from operator import itemgetter, attrgetter, methodcaller
import math
import re
import sys
import argparse
import logging

avg_ic = {'en': 1.73, 'fr': 2.02}
chars_freq = {
        'en': {
            'E': 12.02, 'T': 9.10, 'A': 8.12, 'O': 7.68, 'I': 7.31,
            'N': 6.95, 'S': 6.28, 'R': 6.02, 'H': 5.92, 'D': 4.32,
            'L': 3.98, 'U': 2.88, 'C': 2.71, 'M': 2.61, 'F': 2.30,
            'Y': 2.11, 'W': 2.09, 'G': 2.03, 'P': 1.82, 'B': 1.49,
            'V': 1.11, 'K': 0.69, 'X': 0.17, 'Q': 0.11, 'J': 0.10,
            'Z': 0.07
        }, 'fr': { # that doesn't add up to 100%, because of accents
            'E': 15.10, 'A': 8.13, 'S': 7.91, 'T': 7.11, 'I': 6.94,
            'R': 6.43, 'N': 6.42, 'U': 6.05, 'L': 5.68, 'O': 5.27,
            'D': 3.55, 'M': 3.23, 'C': 3.15, 'P': 3.03, 'V': 1.83,
            'H': 1.08, 'G': 0.97, 'F': 0.96, 'B': 0.93, 'Q': 0.89,
            'J': 0.71, 'X': 0.42, 'Z': 0.21, 'Y': 0.19, 'K': 0.16,
            'W': 0.04
        }}

def vigenere_encode(msg, key):
    encoded = ''

    for i in range(0, len(msg)):
        a = ord(msg[i]) - ord('A')
        b = ord(key[i % len(key)]) - ord('A')
        c = (a + b) % (ord('Z') - ord('A') + 1)

        encoded += chr(c + ord('A'))

    return encoded

def vigenere_decode(msg, key):
    encoded = ''

    for i in range(0, len(msg)):
        a = ord(msg[i]) - ord('A')
        b = ord(key[i % len(key)]) - ord('A')
        c = (a - b) % (ord('Z') - ord('A') + 1)

        encoded += chr(c + ord('A'))

    return encoded

def caesar_encode(msg, offset):
    encoded = ''
    for c in msg:
        encoded += chr((ord(c) - ord('A') + offset) % (ord('Z') - ord('A') + 1) + ord('A'))

    return encoded

def caesar_decode(msg, offset):
    return caesar_encode(msg, 0 - offset)

def char_occurence(msg, char):
    occ = 0

    for c in msg:
        if c == char:
            occ += 1

    return occ

def char_occurences(msg):
    occurences = {}

    for c in range(ord('A'), ord('Z') + 1):
        c = chr(c)
        occurences[c] = char_occurence(msg, c)

    return occurences

def msg_parts(msg, key_size):
    parts = []

    for i in range(0, key_size):
        parts.append('')

    i = 0
    for c in msg:
        parts[i] += c
        i = (i + 1) % key_size

    return parts

def index_coincidence(msg):
    index_sum = 0
    msg_length = len(msg)
    occurences = char_occurences(msg)

    for c in occurences:
        n = occurences[c]
        index_sum += n * (n - 1)

    return 26 * index_sum / (msg_length * (msg_length - 1))

def chi_squared(msg, lang):
    score = 0
    msg_length = len(msg)
    occurences = char_occurences(msg)

    for c in occurences:
        expected_occ = msg_length * chars_freq[lang][c] / 100
        score += math.pow(occurences[c] - expected_occ, 2) / expected_occ

    return score

def caesar_decrypt(msg, lang):
    guesses = []

    for i in range(0, 26):
        decoded = caesar_decode(msg, i)
        guesses.append((i, decoded, chi_squared(decoded, lang)))

    return sorted(guesses, key=itemgetter(2))

def vigenere_decrypt_key_size(msg, key_size, lang):
    parts = msg_parts(msg, key_size)
    key = ''

    logging.debug('calculating the key characters')
    i = 0
    for part in parts:
        guesses = caesar_decrypt(part, lang)
        offset, text, score = guesses[0]
        next_offset, next_text, next_score = guesses[1]
        c = chr(ord('A') + offset)
        key += c
        logging.debug('character #%d: %s (score: %f, next: %f)', i, c, score, next_score)
        i += 1

    logging.debug('key cracked!')

    plaintext = vigenere_decode(msg, key)
    chi = chi_squared(plaintext, lang)

    return {'key': key, 'plaintext': plaintext, 'score': chi}

def vigenere_decrypt(msg, min_key_length, max_key_length, lang):
    logging.debug('max key length: %d', max_key_length)
    logging.debug('min key length: %d', min_key_length)
    logging.debug('lang: %s', lang)

    key_size_ic = []

    # compute ic for each key size
    logging.debug('calculating the best key size')
    for key_size in range(min_key_length, max_key_length + 1):
        index_sum = 0
        parts = msg_parts(msg, key_size)

        for part in parts:
            index_sum += index_coincidence(part)

        delta = abs(index_sum / key_size - avg_ic[lang])

        key_size_ic.append((key_size, delta))
        logging.debug('key size: %d, delta: %f', key_size, delta)

    # decrypt caesar parts
    key_size_ic = sorted(key_size_ic, key=itemgetter(1))

    key_size, delta = key_size_ic[0]

    logging.debug('the best key size is: %d', key_size)

    return vigenere_decrypt_key_size(msg, key_size, lang)


def preprocess_input(msg):
    msg = msg.upper()
    msg = re.sub('[^a-zA-Z]+', '', msg)

    return msg

def postprocess_output(input_msg, output_msg):
    for i in range(0, len(input_msg)):
        if not input_msg[i].isalpha():
            output_msg = output_msg[:i] + input_msg[i] + output_msg[i:]
        elif not input_msg[i].isupper():
            output_msg = output_msg[:i] + output_msg[i].lower() + output_msg[(i + 1):]

    return output_msg

def main():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='The simple vigenère decryption tool. \
            Give me a ciphered text in standard input and I\'ll try my best to \
            give you back the key and decrypted text. \
            Use the `--verbose\' flag to get more info about the cracking \
            operation.')
    parser.add_argument('-k', '--key-length',
            dest='key_length',
            help='use a specific key length, if not set try to find the best match',
            type=int)
    parser.add_argument('-m', '--min-key-length',
            dest='min_key_length',
            help='minimum key length to try',
            default=1,
            type=int)
    parser.add_argument('-M', '--max-key-length',
            dest='max_key_length',
            help='maximum key length to try',
            default=8,
            type=int)
    parser.add_argument('-l', '--language',
            help='language to use for frequency analysis: en or fr',
            default='en')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true')
    args = parser.parse_args()

    if args.language != 'fr' and args.language != 'en':
        parser.error('invalid language %s', args.language)
        sys.exit(2)

    logging_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(format='%(message)s', level=logging_level)

    ciphered_text = sys.stdin.readlines()
    ciphered_text = ''.join(ciphered_text)
    ciphered_text = ciphered_text.rstrip()
    preprocessed_ciphered_text = preprocess_input(ciphered_text)
    logging.debug('preprocessed input: %s', preprocessed_ciphered_text)

    if args.key_length != None:
        result = vigenere_decrypt_key_size(preprocessed_ciphered_text,
                args.key_length,
                args.language)
    else:
        result = vigenere_decrypt(preprocessed_ciphered_text,
                args.min_key_length,
                args.max_key_length,
                args.language)

    plaintext = postprocess_output(ciphered_text, result['plaintext'])
    if args.verbose:
        logging.debug('key: %s', result['key'])
        logging.debug('plaintext: %s', result['plaintext'])
        logging.debug('postprocessed plaintext: %s', plaintext)
        logging.debug('score (chi squared): %s', result['score'])
    else:
        logging.info('%s', result['key'])
        logging.info('%s', plaintext)

if __name__ == "__main__":
    main()
