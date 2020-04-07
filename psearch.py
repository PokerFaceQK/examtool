import pdfminer
import sys
import os
import argparse
from colorama import Fore
from colorama import Style
from pdfminer.high_level import extract_text
import multiprocessing


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", "-d", type=str, default='.',
                        help="folder to be searched")
    parser.add_argument("--keyword", '-k', type=str, default='aaaaaaaaa',
                        help="key word to be found")
    return parser.parse_args(args)


def search_pdf(*args):
    filename, key = args
    if not os.path.isfile(filename):
        return None

    def up(word):
        return word[0].upper() + word[1:]

    def low(word):
        return word[0].lower() + word[1:]

    def display(text, word, idx, interval):
        start = max(idx - interval, 0)
        end = min(idx + interval + length, len(text))
        context_before = '...' + text[start:idx]
        context_after = text[idx + length:end] + '...'
        print(context_before + f"{Fore.GREEN} %s{Style.RESET_ALL}" % (word,) + context_after)

    length = len(key)
    text = extract_text(filename)
    interval = 20

    forms = [low(key), up(key), key.lower(), key.upper()]
    found_flag = False
    for word in forms:
        idx = text.find(word)
        if not idx == -1:
            if not found_flag:
                print('-----------------------------------------------------------------------------')
                print('key word found in ' + f"{Fore.LIGHTYELLOW_EX} %s{Style.RESET_ALL}" % (filename,))
            found_flag = True
            display(text, word, idx, interval)

    if found_flag:
        print('-----------------------------------------------------------------------------')
    else:
        print('key word not found in ' + f"{Fore.LIGHTRED_EX} %s{Style.RESET_ALL}" % (filename,))


def main(folder, keyword):
    if not os.path.isdir(folder):
        print('invalid path')
        return
    files = [os.path.join(folder, fname) for fname in os.listdir(folder)
             if os.path.isfile(os.path.join(folder, fname)) and fname.split('.')[-1] == 'pdf']
    files = sorted(files)

    # use multiple cores to speed up search
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    for file in files:
        pool.apply_async(search_pdf, (file, keyword))

    pool.close()
    pool.join()


if __name__ == '__main__':
    arg = parse_args(sys.argv[1:])
    main(arg.dir, arg.keyword)