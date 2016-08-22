#!/usr/bin/python3

'''
Python module to make POST requests to the waifu2x image enhancement API.

> make into a cmd line tool by adding flags and argparse
> allow file queuing
> reddit bot integration??
'''

import sys
import requests


def main():
    files = {'file': open('photo.jpg', 'rb')}
    data = {'scale': 2, 'style': 'art', 'noise': 3}
    # style: art, photo
    # noise: -1 for none, 0-3 low, medium, high, highest
    # scale: -1 for none, 1 for 1.6x, 2 for 2x

    print('Making request to waifu2x...')
    r = requests.post('http://waifu2x.udp.jp/api', files=files, data=data, stream=True)
    if r.status_code == 200:
        print('Request successful. Downloading...')
        fs, progress = len(r.content), 0
        with open('test.png', 'wb') as f:
            for chunk in r.iter_content(1024*32):
                f.write(chunk)
                progress += len(chunk)
                print('{} / {} bytes downloaded'.format(progress, fs))
    else:
        print(r.text)


    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)
