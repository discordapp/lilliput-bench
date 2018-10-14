Lilliput/Pillow-simd benchmarker
=================

## Install and run Lilliput

Get relevant dependencies: 

```bash
$ go get github.com/discordapp/lilliput
```

Then run: 

```bash
$ GOMAXPROC=1 OPENCV_FOR_THREADS_NUM=1 go run main.go
```

Lilliput benchmarker should be invoked with this environment variables
so that it runs as a single thread.


## Install and run Pillow-SIMD

You'll need Python 2.7 or 3.5 with dev files. Also, you'll need dev versions
of some libraries, see [building-from-source](https://pillow.readthedocs.io/en/5.3.x/installation.html#building-from-source) documentation.

Installing Pillow-SIMD:

```bash
$ pip uninstall pillow
$ CC="cc -mavx2" pip install -U --force-reinstall pillow-simd
```

If installation is successful, you can run the benchmark:

```bash
$ python ./benchmark.py
```
