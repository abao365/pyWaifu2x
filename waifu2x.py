#!/usr/bin/python3

'''
Python module to enhance/smoothen/upscale images by automating the process
of submitting POST requests to the waifu2x image enhancement API.

TODO:
clean up all the code (really messy atm) before making reddit bot
when finished, comment out all output statements
'''

import os
import sys
import requests
from io import BytesIO
from PIL import Image
from urllib.parse import urlparse

API_URL = 'http://waifu2x.udp.jp/api'


def _get_file(img_loc):
    print('Getting image from [{}]...'.format(img_loc))
    u = urlparse(img_loc)
    if u.scheme.strip() != "" and u.netloc.strip() != "":
        r = requests.get(img_loc)
        if r.status_code == 200:
            file = BytesIO(r.content)
            for chunk in r.iter_content(1024):
                file.write(chunk)
            file.seek(0)
            return {'file': file.read()}, False
        else:
            raise RuntimeError('URL access failure ({})'.format(r.status_code))
    else:
        return {'file': open(img_loc, 'rb')}, True


def process(img_loc, mode='pil', style='art', noise=-1, scale=0):
    '''
    Img_loc: Can be either a URL or a local filepath
    Style: art / photo
    Noise: -1 for none, 0-3 for low, medium, high, highest
    Scale: 0 for none, 1 for 1.6x, 2 for 2x
    '''
    try:
        file, is_stored_locally = _get_file(img_loc)
    except RuntimeError as e:
        print("Error retrieving original image: {}".format(e))
        return -1
    filename = os.path.splitext(os.path.basename(img_loc))[0]

    style, noise, scale = style.lower(), int(noise), int(scale)
    assert(style in ('photo', 'art'))
    assert(noise in range(-1, 4))
    assert(scale in range(0, 3))
    options = {'style': style, 'noise': noise, 'scale': scale}
    op_str = "_waifu2x"
    for o in options:
        op_str += "_{}{}".format(o, options[o])

    print('Making request to waifu2x...')
    r = requests.post(API_URL, files=file, data=options, stream=True)
    if r.status_code == 200:
        if mode.lower() == 'dl':
            print('Request successful. Downloading...')
            result_fn = ''.join((filename, op_str, '.png'))
            if is_stored_locally:
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
            return result_dir
        else:
            return Image.open(BytesIO(r.content))
    else:
        print(r.text)
        print("Limits: Size (5MB), Noise Reduction (3000x3000px), Upscaling (1500x1500px)")


def multi_process(img_loc, reps, mode='pil', style='art', noise=-1, scale=0):
    # TODO make this work with PIL too
    # download or can use bytestream passing directly?
    # TODO enforce reps is 1 to 10
    # better way to not repeat params...?
    path = img_loc
    for i in range(1, int(reps)+1):
        print("Enhancing ... {} of {} iterations".format(i, reps))
        prev = path
        path = process(path, mode, style, noise, scale)
        if 1 < i < int(reps)+1:
            print("Removing intermediate image...")
            os.remove(prev)


def main():
    # TESTING CODE
    usage = '[img url/path] [repeat (1-10)] [mode (dl/pil)] ' \
            '[style (art/photo)] [noise (-1 to 3)] [scale (-1, 1, 2)]'
    multi_process(*tuple(input(usage + '\n').strip().split()))
    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)
