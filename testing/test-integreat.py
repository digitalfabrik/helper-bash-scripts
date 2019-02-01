#!/usr/bin/env python3

import requests
import json
import sys



if sys.stdout.isatty():
 OKGREEN = '\033[92m'
 FAIL = '\033[91m'
 ENDC = '\033[0m'
else:
 OKGREEN = ''
 FAIL = ''
 ENDC = ''

exit_code = 0

def test_url(url, code, mimetype, redirect = None):
 r = requests.get(url, allow_redirects=False)
 if mimetype in r.headers['content-type']:
  mimetype_ok = True
 else:
  mimetype_ok = False
 if code == r.status_code:
  response_code_ok = True
 else:
  response_code_ok = False

 redirect_ok = False
 if code == 301 or code == 302:
  if redirect in r.headers['Location']:
   redirect_ok = True

 dataset_length = -1
 if mimetype == 'application/json':
  dataset_length = len(json.loads(r.text))

 if not response_code_ok or not mimetype_ok or dataset_length == 0:
  global exit_code
  exit_code = 1
  print("[{}FAIL{}] {}".format(FAIL, ENDC, url))
  print("       Status: {}, expected {} - {}".format(r.status_code, code, response_code_ok))
  print("       Mimetype: {}, expected {} - {}".format(r.headers['content-type'], mimetype, mimetype_ok))
  if 'Location' in r.headers:
   print("       Redirect: {}, expected {} - {}".format(r.headers['Location'], redirect, redirect_ok))
  if mimetype == 'application/json':
   print("       Dataset length: {}".format(dataset_length))
 else:
  print("[ {}OK{} ] {}".format(OKGREEN, ENDC, url))
 
test_url('https://cms.integreat-app.de/',
 301,
 'text/html',
 'https://integreat.app')

test_url('https://cms.integreat-app.de/testumgebung/de/wp-activate.php',
 404,
 'text/html')
 
test_url('https://cms.integreat-app.de/wp-activate.php',
 200,
 'text/html')

test_url('https://cms.integreat-app.de/wp-login.php',
 200,
 'text/html')

test_url('https://cms.integreat-app.de/wp-admin/',
 302,
 'text/html',
 'https://cms.integreat-app.de/wp-login.php')

test_url('https://cms.integreat-app.de/testumgebung/wp-admin/',
 302,
 'text/html',
 'https://cms.integreat-app.de/wp-login.php')

test_url('https://cms.integreat-app.de/wp-includes/js/tinymce/wp-tinymce.php?c=1&ver=4800-20180716-tadv-4.7.13',
 200,
 'application/javascript')

test_url('https://cms.integreat-app.de/testumgebung/wp-includes/js/tinymce/wp-tinymce.php?c=1&ver=4800-20180716-tadv-4.7.13',
 200,
 'application/javascript')

test_url('https://cms.integreat-app.de/testumgebung/wp-includes/js/jquery/ui/button.min.js?ver=1.11.4',
 200,
 'application/javascript')
  
test_url('https://cms.integreat-app.de/wp-json/extensions/v3/sites',
 200,
 'application/json')

test_url('https://cms.integreat-app.de/testumgebung/de/',
 301,
 'text/html',
 'https://integreat.app/testumgebung/de/')

test_url('https://cms.integreat-app.de/wp-content/uploads/sites/2/2015/10/network49-150x150.png',
 200,
 'image/png')

test_url('https://cms.integreat-app.de/wp-content/uploads/sites/2/2015/10/foo.png',
 404,
 'text/html')

test_url('https://cms.integreat-app.de/wp-foo/bar.php',
 404,
 'text/html')

test_url('https://cms.integreat-app.de/wp-foo.php',
 404,
 'text/html')

test_url('https://cms.integreat-app.de/testumgebung/de/foo/bar',
 301,
 'text/html',
 'https://integreat.app/testumgebung/de/foo/bar/')

test_url('https://cms.integreat-app.de/testumgebung/de/wp-json/extensions/v0/modified_content/pages?since=2015-01-25T09%3A27%3A49%2B0000',
 200,
 'application/json')

test_url('https://cms.integreat-app.de/testumgebung/de/wp-json/extensions/v3/pages',
 200,
 'application/json')

test_url('https://cms.integreat-app.de/testumgebung/ar/wp-json/extensions/v3/pages',
 200,
 'application/json')

test_url('https://cms.integreat-app.de/wp-json/extensions/v3/sites',
 200,
 'application/json')

test_url('https://cms.integreat-app.de/augsburg/wp-content/themes/integreat-webview/style.css',
 404,
 'text/html'
)

test_url('https://integreat.app/landing/en',
 200,
 'text/html'
)

test_url('https://integreat.app/fonts/open-sans/open-sans.css',
 200,
 'text/css'
)

exit(exit_code)
