#!/usr/bin/python3

'''
Python module to make POST requests to the waifu2x image enhancement API.

> allow file queuing?
> reddit bot integration?
'''

import os
import sys
import requests
from uuid import uuid4

POST_URL = 'http://waifu2x.udp.jp/api'


def _get_file(img_loc):
    # TODO handle image urls as well as local filepaths
    print('Getting image from [{}]...'.format(img_loc))
    return {'file': open(img_loc, 'rb')}


def _get_options(style, noise, scale):
    '''
    style: art, photo
    noise: -1 for none, 0-3 for low, medium, high, highest
    scale: -1 for none, 1 for 1.6x, 2 for 2x
    '''
    # validate options here
    return {'style': style, 'noise': noise, 'scale': scale}


# TODO support returning PIL objects in addition to local download
# or just make local download a separate function
# TODO allow customize local path to save to
def process(img_loc, style='art', noise=3, scale=-1):
    # img_loc can be either a URL or a local filepath
    file = _get_file(img_loc)
    options = _get_options(style, noise, scale)
    print('Making request to waifu2x...')
    r = requests.post(POST_URL, files=file, data=options, stream=True)
    if r.status_code == 200:
        print('Request successful. Downloading...')
        out_fn, total, progress = str(uuid4()) + '.png', len(r.content), 0
        with open(out_fn, 'wb') as f:
            for chunk in r.iter_content(1024*64):
                f.write(chunk)
                progress += len(chunk)
                print('{} / {} bytes downloaded'.format(progress, total))
        print('Download complete. Saved to {}'.format(os.path.join(os.getcwd(), out_fn)))
    else:
        print(r.text)

def main():
    usage = '[image url/path] [style (art/photo)] [noise (-1 - 3)] [scale (-1, 1, 2)]'
    process(*tuple(input(usage + '\n').strip().split()))
    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)
