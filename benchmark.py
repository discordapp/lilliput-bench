from __future__ import print_function

import time
from io import BytesIO
from PIL import Image, ImageOps


def print_timings(timings, precision=2):
    timings.sort()
    print(('avg: %%.%sf ms' % precision) % (sum(timings)/len(timings) * 1000), end='\t')
    print(('min: %%.%sf ms' % precision) % (timings[0] * 1000), end='\t')
    print(('max: %%.%sf ms' % precision) % (timings[-1] * 1000))


def analyze_gif(blob):
    im = Image.open(blob)
    results = {
        'size': im.size,
        'mode': 'full',
    }
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results['mode'] = 'partial'
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return results


def resize_gif(blob, width, height, write_to=''):
    mode = analyze_gif(blob)['mode']
    im = Image.open(blob)

    i = 0
    p = im.getpalette()
    last_frame = ImageOps.fit(im.convert('RGBA'), (width, height), Image.LANCZOS)
    frames = []

    try:
        while True:
            if not im.getpalette():
                im.putpalette(p)

            new_frame = Image.new('RGBA', (width, height))

            if mode == 'partial':
                new_frame.paste(last_frame)

            resized_frame = ImageOps.fit(im, (width, height), Image.LANCZOS)
            new_frame.paste(resized_frame, (0,0), resized_frame.convert('RGBA'))

            i += 1
            last_frame = new_frame
            frames.append(new_frame)
            im.seek(im.tell() + 1)
    except EOFError:
        pass

    output = BytesIO()
    first_frame = frames[0]
    first_frame.save(output, 'GIF', save_all=True, append_images=frames[1:])
    size = len(output.getvalue())
    if write_to:
        with open(write_to, 'wb') as f:
            f.write(output.getvalue())
    output.close()
    return size


def bench_header(path, num_iter):
    with open(path, 'rb') as f:
        blob = f.read()
    blob = BytesIO(blob)
    timings = []
    for i in range(num_iter):
        start = time.time()
        im = Image.open(blob)
        width, height = im.size
        if i == 0:
            print('%dx%d,' % (width, height), end='\t')
        stop = time.time()
        timings.append(stop - start)
    print_timings(timings, precision=6)


save_opts = {
    'JPEG': {
        'quality': 85,
    },
    'PNG': {
        'compress_level': 7,
    },
    'WEBP': {
        'quality': 85,
    },
    'GIF': {},
}


def bench_resize(path, output_type, width, height, num_iter):
    with open(path, 'rb') as f:
        blob = f.read()
    blob = BytesIO(blob)
    timings = []
    for i in range(num_iter):
        start = time.time()
        im = Image.open(blob)
        im = im.convert('RGB' if output_type == 'JPEG' else 'RGBA')
        im = ImageOps.fit(im, (width, height), Image.LANCZOS)
        output = BytesIO()
        im.save(output, output_type, **save_opts[output_type])
        if i == 0:
            print('%d Bytes,' % len(output.getvalue()), end='\t')
            with open('py_%d.%s' % (width, output_type.lower()), 'wb') as f:
                f.write(output.getvalue())
        output.close()
        stop = time.time()
        timings.append(stop - start)
    print_timings(timings)


def bench_resize_gif(path, width, height, num_iter):
    with open(path, 'rb') as f:
        blob = f.read()
    blob = BytesIO(blob)
    timings = []
    for i in range(num_iter):
        start = time.time()
        path = '' if i != 0 else 'py_%d.gif' % width
        size = resize_gif(blob, width, height, path)
        if i == 0:
            print('%d Bytes,' % size, end='\t')
        stop = time.time()
        timings.append(stop - start)
    print_timings(timings)


def bench_transcode(path, output_type, num_iter):
    with open(path, 'rb') as f:
        blob = f.read()
    blob = BytesIO(blob)
    timings = []
    for i in range(num_iter):
        start = time.time()
        im = Image.open(blob)
        output = BytesIO()
        im.save(output, output_type, **save_opts[output_type])
        if i == 0:
            print('%d Bytes,' % len(output.getvalue()), end='\t')
            with open('py_%s_transcode.%s' % (path, output_type.lower()), 'wb') as f:
                f.write(output.getvalue())
        output.close()
        stop = time.time()
        timings.append(stop - start)
    print_timings(timings)


def main():
    print('JPEG 1920x1080 header read:', end='\t')
    bench_header('1920.jpeg', 10000)
    print('PNG 1920x1080 header read:', end='\t')
    bench_header('1920.png', 10000)
    print('WEBP 1920x1080 header read:', end='\t')
    bench_header('1920.webp', 100)
    print('GIF 1920x1080 header read:', end='\t')
    bench_header('1920.gif', 10000)

    print('JPEG 256x256 => 32x32:', end='\t')
    bench_resize('256.jpeg', 'JPEG', 32, 32, 1000)
    print('PNG 256x256 => 32x32:', end='\t')
    bench_resize('256.png', 'PNG', 32, 32, 1000)
    print('WEBP 256x256 => 32x32:', end='\t')
    bench_resize('256.webp', 'WEBP', 32, 32, 1000)
    print('GIF 256x256 => 32x32:', end='\t')
    bench_resize_gif('256.gif', 32, 32, 1000)

    print('JPEG 1920x1080 => 800x600:', end='\t')
    bench_resize('1920.jpeg', 'JPEG', 800, 600, 100)
    print('PNG 1920x1080 => 800x600:', end='\t')
    bench_resize('1920.png', 'PNG', 800, 600, 100)
    print('WEBP 1920x1080 => 800x600:', end='\t')
    bench_resize('1920.webp', 'WEBP', 800, 600, 100)
    print('GIF 1920x1080 => 800x600:', end='\t')
    bench_resize_gif('1920.gif', 800, 600, 50)

    print('PNG 256x256 => WEBP 256x256:', end='\t')
    bench_transcode('256.png', 'WEBP', 100)
    print('JPEG 256x256 => PNG 256x256:', end='\t')
    bench_transcode('256.jpeg', 'PNG', 100)
    print('GIF 256x256 => PNG 256x256:', end='\t')
    bench_transcode('256.gif', 'PNG', 100)

if __name__ == '__main__':
    main()
