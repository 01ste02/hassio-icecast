#!/usr/bin/env python
import threading
import time
import collections
from http.server import BaseHTTPRequestHandler, HTTPServer
import uuid
from socketserver import ThreadingMixIn
from subprocess import PIPE, Popen


class LibreSpot:
    __instance = None

    samplerate = 44100
    channels = 2
    bits = 16

    samplesize = None

    _thread = None
    _proc = None
    _exit = None
    _queues = None

    def __init__(self, device_name, bitrate=160, initial_volume=50):
        self.device_name = device_name
        self.bitrate = bitrate
        self.initial_volume = initial_volume

        # Calculate byte-size for 1 sec. of audio
        self.samplesize = int(self.samplerate * self.bits * self.channels / 8)

        self._exit = threading.Event()
        self._queues = {}

    @classmethod
    def get(cls) -> 'LibreSpot':
        if not cls.__instance:
            cls.__instance = LibreSpot()
        return cls.__instance

    @property
    def is_running(self):
        return not self._exit.is_set()

    def subscribe(self):
        handle = str(uuid.uuid4())
        self._queues[handle] = collections.deque(maxlen=self.samplesize)
        return handle

    def unsubscribe(self, handle):
        del self._queues[handle]

    def run(self):
        self._proc = Popen(
            [
                'librespot',
                '--disable-audio-cache',
                '-n',
                self.device_name,
                '-b',
                str(self.bitrate),
                '--initial-volume',
                str(self.initial_volume),
                '--backend',
                'pipe',
            ],
            stdout=PIPE,
        )

        chunk_size = self.samplesize // 4
        while True:
            if self._exit.is_set():
                break

            # Read 250 ms of audio data and add it to all buffers
            chunk = self._proc.stdout.read(chunk_size)
            for handle, q in self._queues.items():
                q.extend(chunk)

            # Wait 250 ms before reading the next chunk as otherwise
            # spotify would start skipping tracks
            time.sleep(.25)

    def start(self):
        self._thread = threading.Thread(target=self.run)
        self._thread.start()

    def stop(self):
        self._exit.set()
        self._thread.join()

    def read(self, handle):
        if len(self._queues[handle]) < self.samplesize:
            return b''

        chunk = bytearray(bytes(self._queues[handle]))
        self._queues[handle].clear()
        return chunk


class StreamHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def _wav_header(self, sample_rate, bits, channels):
        # For streaming the data-size has to be 0 as otherwise clients don't
        # stream but try to buffer everything which is not possible
        datasize = 0

        header = bytes('RIFF', 'ascii')
        header += (datasize + 36).to_bytes(4, 'little')
        header += bytes('WAVE', 'ascii')
        header += bytes('fmt ', 'ascii')
        header += (16).to_bytes(4, 'little')
        header += (1).to_bytes(2, 'little')
        header += (channels).to_bytes(2, 'little')
        header += (sample_rate).to_bytes(4, 'little')
        header += (sample_rate * channels * bits // 8).to_bytes(4, 'little')
        header += (channels * bits // 8).to_bytes(2, 'little')
        header += (bits).to_bytes(2, 'little')
        header += bytes('data', 'ascii')
        header += (datasize).to_bytes(4, 'little')

        return header

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'audio/wav')
        self.end_headers()

        print('New client:', self.client_address)

        librespot = self.server.librespot

        self.wfile.write(
            self._wav_header(librespot.samplerate, librespot.bits,
                             librespot.channels))

        handle = librespot.subscribe()
        while librespot.is_running:
            chunk = librespot.read(handle)

            # Prevent high cpu-loads
            if not chunk:
                time.sleep(.1)
                continue

            try:
                self.wfile.write(chunk)
            except (ConnectionResetError, BrokenPipeError):
                break

        print('bye bye:', self.client_address)
        librespot.unsubscribe(handle)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    librespot = None

    def __init__(self, *args, librespot, **kwargs):
        self.librespot = librespot

        HTTPServer.__init__(self, *args, **kwargs)


if __name__ == '__main__':
    librespot = LibreSpot('Hela huset', 320)
    librespot.start()

    httpd = ThreadedHTTPServer(('', 6000), StreamHandler, librespot=librespot)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    librespot.stop()
    httpd.server_close()
