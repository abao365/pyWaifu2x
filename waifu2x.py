#!/usr/bin/python3

'''
Python module to make POST requests to the waifu2x image enhancement API.

> allow file queuing?
> reddit bot integration?
'''

import os
import sys
import requests
from urllib.parse import urlparse, urlsplit
from io import BytesIO

POST_URL = 'http://waifu2x.udp.jp/api'


def _get_file(img_loc):
    print('Getting image from [{}]...'.format(img_loc))
    u = urlparse(img_loc)
    if u.scheme.strip() != "" and u.netloc.strip() != "":
        r = requests.get(img_loc)
        if r.status_code == 200:
            if not img_loc.lower().endswith(('.jpg', '.png')):
                raise RuntimeError('URL does not link to a jpg/png image.')
            file = BytesIO()
            for chunk in r.iter_content(1024):
                file.write(chunk)
            file.seek(0)
            fn = os.path.splitext(os.path.basename(urlsplit(img_loc).path))[0]
            return ({'file': file.read()}, fn, False)
        else:
            raise RuntimeError('URL access failure [{}].'.format(r.status_code))
    else:
        fn = os.path.splitext(os.path.basename(img_loc))[0]
        return ({'file': open(img_loc, 'rb')}, fn, True)


def _get_options(style, noise, scale):
    # style: either art or photo
    style, noise, scale = style.lower(), int(noise), int(scale)
    if style != 'photo':
        style = 'art'
    # noise: -1 for none, 0-3 for low, medium, high, highest
    if noise not in range(-1, 4):
        noise = -1
    # scale: -1 for none, 1 for 1.6x, 2 for 2x
    if scale not in (-1, 1, 2):
        scale = -1
    options = {'style': style, 'noise': noise, 'scale': scale}
    op_str = "_waifu2x"
    for o in options:
        op_str += "_{}{}".format(o, options[o])
    return options, op_str

# TODO add option to stop output on all functions (for library output functionality)
def process_dl(img_loc, style='art', noise=3, scale=-1):
    # img_loc can be either a URL or a local filepath
    try:
        file, name, is_local_src = _get_file(img_loc)
    except RuntimeError as e:
        print("Error retrieving original image file: {}".format(e))
        return -1
    options, op_str = _get_options(style, noise, scale)
    print('Making request to waifu2x...')
    r = requests.post(POST_URL, files=file, data=options, stream=True)
    if r.status_code == 200:
        print('Request successful. Downloading...')
        result_fn = ''.join((name, op_str, '.png'))
        if is_local_src:
            result_dir = os.path.join(os.path.dirname(img_loc), result_fn)
        else:
            result_dir = os.path.join(os.getcwd(), result_fn)
        total, progress = len(r.content), 0
        with open(result_dir, 'wb') as f:
            for chunk in r.iter_content(1024*64):
                f.write(chunk)
                progress += len(chunk)
                print('{} / {} bytes downloaded'.format(progress, total))
        print('Download complete. Saved to {}'.format(result_dir))
    else:
        print(r.text)

# TODO support returning PIL objects in addition to local download
def process_pil():
    pass

def main():
    usage = '[image url/path] [style (art/photo)] [noise (-1 - 3)] [scale (-1, 1, 2)]'
    process_dl(*tuple(input(usage + '\n').strip().split()))
    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)
