# -*- coding: utf-8 -*-
#!/usr/bin/env python3

# https://github.com/xuruidong/markdown-link-checker

import os
import sys
import re
import urllib.request
import argparse
import ssl


def red(s):
    return '\033[91m' + s + '\033[0m'


def green(s):
    return '\033[32m' + s + '\033[0m'


external_links_cache = {}


def check(url):
    if url in external_links_cache:
        # print("[debug] in cache")
        return external_links_cache[url]

    try:
        context = ssl._create_unverified_context()
        req = urllib.request.Request(url, method='GET', headers={'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"})
        resp = urllib.request.urlopen(req, context=context, timeout=4)
        if resp.code >= 400:
            ret = "Got HTTP response code {}".format(resp.code)
            external_links_cache[url] = ret
            return ret
    except Exception as e:
        ret = "Got exception {}".format(e)
        external_links_cache[url] = ret
        return ret

    external_links_cache[url] = None
    return None


class LinkChecker(object):
    def __init__(self, disable_relative_link=False, enable_external_link=False,
                 enable_internal_link=False, base_url="", ignore_list=[], *args, **kwargs):
        self.disable_relative_link = disable_relative_link
        self.enable_external_link = enable_external_link
        self.enable_internal_link = enable_internal_link
        self.base_url = base_url
        self.ignore_list = ignore_list
        print(self.enable_external_link)

    def check_file(self, path):
        error_count = 0
        dirname = os.path.dirname(path)
        filename = os.path.basename(path)
        with open(path, mode='r', encoding="utf-8") as f:
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

                ignore_this = False
                for ign in self.ignore_list:
                    if re.match(ign, url):
                        ignore_this = True
                        break

                if ignore_this:
                    # print("[debug] ignore")
                    continue

                error = None
                if url.startswith('http://') or url.startswith('https://'):
                    if self.enable_external_link:
                        error = check(url)
                        pass
                elif url.startswith('/'):
                    if self.enable_internal_link:
                        url = self.base_url + url
                        error = check(url)
                elif url.startswith('mailto:'):
                    pass
                else:
                    if self.disable_relative_link:
                        continue

                    url = dirname + '/' + url
                    url = url.rstrip('/')
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

    def check_dir(self, directory):
        pass


def run(work_dir, disable_relative_link=False, enable_external_link=False,
        enable_internal_link=False, base_url="", ignores=[]):
    if not ignores:
        ignores = []

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

                    ignore_this = False
                    for ign in ignores:
                        if re.match(ign, url):
                            ignore_this = True
                            break

                    if ignore_this:
                        # print("[debug] ignore")
                        continue

                    error = None
                    if url.startswith('http://') or url.startswith('https://'):
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
                        url = url.rstrip('/')
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
    parser.add_argument("--ignore", nargs='*',
                        help="ignore link")
    parser.add_argument("path")
    args = parser.parse_args()
    # print(args)
    if args.enable_internal and not args.base_url:
        print("base-url is needed")
        sys.exit(1)

    internal_links = []  # /a/b/c
    external_links = []
    relative_links = []

    if not args.ignore:
        args.ignore = []

    checker = LinkChecker(args.disable_relative, args.enable_external,
                          args.enable_internal, args.base_url, args.ignore)
    if os.path.isfile(args.path):
        if checker.check_file(args.path) != 0:
            sys.exit(1)

        sys.exit(0)

    if run(args.path, args.disable_relative, args.enable_external,
           args.enable_internal, args.base_url, args.ignore) != 0:
        sys.exit(1)
