# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import os
import sys
import re
import urllib.request


def red(s):
    return '\033[91m' + s + '\033[0m'


def green(s):
    return '\033[32m' + s + '\033[0m'


def check(url):
    try:
        req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': "link-checker"})
        resp = urllib.request.urlopen(req, timeout=3)
        if resp.code >= 400:
            return "Got HTTP response code {}".format(resp.code)
    except Exception as e:
        return "Got exception {}".format(e)
    return None


def run(work_dir):
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

                    error = None
                    if url.startswith('http://') or url.startswith('https://'):
                        # todo
                        #error = check(url)
                        pass
                    elif url.startswith('/'):
                        # todo
                        pass
                    else:
                        url = url.split('#')[0]
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
    if len(sys.argv) < 2:
        print("usage: {} root_path\n".format(sys.argv[0]))
        print("i.e. {} source ".format(sys.argv[0]))
        sys.exit(1)

    work_dir = sys.argv[1]

    if run(work_dir) != 0:
        sys.exit(1)
