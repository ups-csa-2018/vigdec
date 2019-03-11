# Vigdec usage

```
usage: vigdec.py [-h] [-k KEY_LENGTH] [-m MIN_KEY_LENGTH] [-M MAX_KEY_LENGTH]
                 [-l LANGUAGE] [-v]

The simple vigenère decryption tool. Give me a ciphered text in standard input
and I'll try my best to give you back the key and decrypted text. Use the
`--verbose' flag to get more info about the cracking operation.

optional arguments:
  -h, --help            show this help message and exit
  -k KEY_LENGTH, --key-length KEY_LENGTH
                        use a specific key length, if not set try to find the
                        best match (default: None)
  -m MIN_KEY_LENGTH, --min-key-length MIN_KEY_LENGTH
                        minimum key length to try (default: 1)
  -M MAX_KEY_LENGTH, --max-key-length MAX_KEY_LENGTH
                        maximum key length to try (default: 8)
  -l LANGUAGE, --language LANGUAGE
                        language to use for frequency analysis: en or fr
                        (default: en)
  -v, --verbose
```
