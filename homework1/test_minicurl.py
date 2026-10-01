"""Local integration tests; no Internet connection required."""
import http.server
import pathlib
import subprocess
import sys
import tempfile
import threading
import unittest

SCRIPT = pathlib.Path(__file__).with_name('minicurl.py')


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == '/redirect':
            self.send_response(302)
            self.send_header('Location', '/binary')
            self.end_headers()
            return
        self.send_response(404 if self.path == '/missing' else 200)
        self.send_header('X-Test', 'yes')
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(b'\x00\xffhello' if self.path == '/binary' else b'hello')

    do_HEAD = do_GET

    def do_POST(self):
        data = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(self.command.encode() + b'|' + self.headers.get('X-Custom', '').encode() + b'|' + data)

    do_PUT = do_POST


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, timeout=5)

    def test_get(self):
        result = self.run_cli(self.base)
        self.assertEqual((result.returncode, result.stdout), (0, b'hello'))

    def test_post_and_headers(self):
        result = self.run_cli('-d', 'name=student', '-H', 'X-Custom: yes', self.base)
        self.assertEqual(result.stdout, b'POST|yes|name=student')

    def test_put_unicode(self):
        result = self.run_cli('-X', 'PUT', '-d', '你好', self.base)
        self.assertEqual(result.stdout, 'PUT||你好'.encode())

    def test_head(self):
        result = self.run_cli('-I', self.base)
        self.assertIn(b'200 OK', result.stdout)
        self.assertNotIn(b'hello', result.stdout)

    def test_include(self):
        result = self.run_cli('-i', self.base)
        self.assertIn(b'X-Test: yes\r\n', result.stdout)
        self.assertTrue(result.stdout.endswith(b'\r\n\r\nhello'))

    def test_redirect(self):
        self.assertEqual(self.run_cli(self.base + '/redirect').stdout, b'')
        self.assertEqual(self.run_cli('-L', self.base + '/redirect').stdout, b'\x00\xffhello')

    def test_binary_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / 'result.bin'
            result = self.run_cli('-o', str(path), self.base + '/binary')
            self.assertEqual(result.returncode, 0)
            self.assertEqual(path.read_bytes(), b'\x00\xffhello')

    def test_http_failure(self):
        self.assertEqual(self.run_cli(self.base + '/missing').stdout, b'hello')
        result = self.run_cli('-f', self.base + '/missing')
        self.assertEqual((result.returncode, result.stdout), (22, b''))

    def test_bad_inputs(self):
        for args in [('file:///etc/passwd',), ('--timeout', '0', self.base), ('-H', 'bad', self.base), ('-I', '-d', 'x', self.base)]:
            with self.subTest(args=args):
                self.assertNotEqual(self.run_cli(*args).returncode, 0)


if __name__ == '__main__':
    unittest.main()
