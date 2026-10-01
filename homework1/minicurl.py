"""A small HTTP/HTTPS command-line client using only Python's standard library."""
import argparse
import math
import sys
import urllib.error
import urllib.parse
import urllib.request


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlsplit(newurl).scheme not in ('http', 'https'):
            raise ValueError('Redirect must use HTTP or HTTPS')
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is not None:
            old = urllib.parse.urlsplit(req.full_url)
            new = urllib.parse.urlsplit(newurl)
            origin = lambda u: (u.scheme, u.hostname, u.port or (443 if u.scheme == 'https' else 80))
            if origin(old) != origin(new):
                for name in ('Authorization', 'Cookie', 'Proxy-authorization'):
                    redirected.remove_header(name)
        return redirected


def parser():
    p = argparse.ArgumentParser(description='MiniCurl: a minimal HTTP/HTTPS client')
    p.add_argument('url')
    p.add_argument('-X', '--request', help='HTTP method, e.g. GET, POST, PUT, DELETE')
    p.add_argument('-H', '--header', action='append', default=[], help='Name: value; repeatable')
    p.add_argument('-d', '--data', help='UTF-8 request body (defaults to POST)')
    p.add_argument('-I', '--head', action='store_true', help='Send HEAD and print headers')
    p.add_argument('-i', '--include', action='store_true', help='Include response headers')
    p.add_argument('-L', '--location', action='store_true', help='Follow redirects')
    p.add_argument('-o', '--output', help='Write response to a file')
    p.add_argument('--timeout', type=float, default=10, help='Socket timeout in seconds (default: 10)')
    p.add_argument('-f', '--fail', action='store_true', help='Exit 22 and suppress body on HTTP 4xx/5xx')
    return p


def main(argv=None):
    p = parser()
    args = p.parse_args(argv)
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        p.error('--timeout must be a positive finite number')
    if args.head and (args.data is not None or args.request):
        p.error('-I cannot be combined with -d or -X')
    try:
        url = urllib.parse.urlsplit(args.url)
        if url.scheme not in ('http', 'https') or not url.hostname:
            raise ValueError('URL must begin with http:// or https:// and contain a host')
        headers = {'User-Agent': 'MiniCurl/1.0'}
        for raw in args.header:
            name, sep, value = raw.partition(':')
            if not sep or not name.strip() or '\r' in raw or '\n' in raw:
                raise ValueError('Header must have the form Name: value')
            headers[name.strip()] = value.strip()
        body = args.data.encode('utf-8') if args.data is not None else None
        method = 'HEAD' if args.head else (args.request or ('POST' if body is not None else 'GET')).upper()
        req = urllib.request.Request(args.url, data=body, headers=headers, method=method)
        opener = urllib.request.build_opener(SafeRedirect() if args.location else NoRedirect())
        try:
            response = opener.open(req, timeout=args.timeout)
        except urllib.error.HTTPError as exc:
            # HTTP errors still carry a valid HTTP response and body.
            response = exc
        with response:
            if args.fail and response.status >= 400:
                print(f'minicurl: HTTP {response.status} {response.reason}', file=sys.stderr)
                return 22
            out = open(args.output, 'wb') if args.output else sys.stdout.buffer
            try:
                if args.include or args.head:
                    version = {10: '1.0', 11: '1.1'}.get(response.version, str(response.version))
                    head = f'HTTP/{version} {response.status} {response.reason}\r\n'
                    head += ''.join(f'{k}: {v}\r\n' for k, v in response.headers.items()) + '\r\n'
                    out.write(head.encode('iso-8859-1', errors='replace'))
                if method != 'HEAD':
                    while True:
                        chunk = response.read(65536)
                        if not chunk:
                            break
                        out.write(chunk)
                out.flush()
            finally:
                if args.output:
                    out.close()
        return 0
    except (ValueError, OSError, urllib.error.URLError) as exc:
        print(f'minicurl: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
