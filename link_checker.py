# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import os
import sys
import re
import urllib.request
import argparse


def red(s):
    return '\033[91m' + s + '\033[0m'


def green(s):
    return '\033[32m' + s + '\033[0m'


def check(url):
    try:
        req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': "link-checker"})
        resp = urllib.request.urlopen(req, timeout=4)
        if resp.code >= 400:
            return "Got HTTP response code {}".format(resp.code)
    except Exception as e:
        return "Got exception {}".format(e)
    return None


def run(work_dir, disable_relative_link=False, enable_external_link=False,
        enable_internal_link=False, base_url=""):
    error_count = 0
    for path, dirs, filenames in os.walk(work_dir):
        for filename in [i for i in filenames if i.endswith('.md')]:
            with open(os.path.join(path, filename), mode='r', encoding="utf-8") as f:
                printed_filename = False
                content = f.read()
                urls = re.findall("""\[[^\]]+\]\(([^\)^"^']+)\)""", content)
                urls += re.findall('(?:href|src)\s*=\s*"\s*([^"]+)', content)
                for url in urls:
                    url = url.strip()

                    if url.startswith('#'):
                        # skip in-url reference
                        continue
                    '''
                    if url.startswith('/') and not url.startswith('//'):
                        url = base_url + url
                    '''
                    url = url.split('#')[0]

                    error = None
                    if url.startswith('http://127.0.0.1') or url.startswith('https://127.0.0.1') or url.startswith('http://localhost') or url.startswith('https://localhost'):
                        continue
                    elif url.startswith('http://') or url.startswith('https://'):
                        if enable_external_link:
                            error = check(url)
                            pass
                    elif url.startswith('/'):
                        if enable_internal_link:
                            url = base_url + url
                            error = check(url)
                    elif url.startswith('mailto:'):
                        pass
                    else:
                        if disable_relative_link:
                            continue

                        url = path + '/' + url
                        if os.path.exists(url) == False:
                            error = " does not exist"

                    if error is not None:
                        if not printed_filename:
                            print()
                            print("{} {}".format(filename, red('x')))
                            print('-' * len(filename))
                            printed_filename = True
                        print(url, error)
                        error_count += 1
                if not printed_filename:
                    print("{} {}".format(filename, green('‎✔')))
                else:
                    print()

    return error_count


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--enable-external", action='store_true',
                        help="enable check external link")
    parser.add_argument("--enable-internal", action='store_true',
                        help="enable check internal link, 'base-url' is \
                        needed.")
    parser.add_argument("--base-url",
                        help="for check internal link")
    parser.add_argument("--disable-relative", action='store_true',
                        help="disable check relative link")
    parser.add_argument("workdir")
    args = parser.parse_args()
    # print(args)
    if args.enable_internal and not args.base_url:
        print("base-url is needed")
        sys.exit(1)

    internal_links = []  # /a/b/c
    external_links = []
    relative_links = []

    if run(args.workdir, args.disable_relative, args.enable_external,
           args.enable_internal, args.base_url) != 0:
        sys.exit(1)
