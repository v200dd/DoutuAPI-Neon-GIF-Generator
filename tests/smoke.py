"""Real HTTP checks against Compose, or a local PHP test server.

Set PHP_ONLY=1 for local PHP testing without the Nginx/GIF containers.
Private identifiers and passwords are never printed.
"""
import io
import json
import os
import sys
import time
from urllib.parse import urlsplit

import httpx
from PIL import Image

base = sys.argv[1].rstrip('/')
password = os.environ['ADMIN_PASSWORD']
php_only = os.getenv('PHP_ONLY') == '1'
wxid = 'integration-test-user'
client = httpx.Client(base_url=base, timeout=60)


def check(label, condition):
    assert condition, label
    print('PASS', label, flush=True)


check('landing page and Neon link', '/neon/' in client.get('/').text)
denied = client.get('/', params={'keyword': '测试', 'wxid': 'not-authorized'}).json()
check('unauthorized wxid remains code 403', denied['code'] == 403)
bad_key = client.post('/admin.php?action=api_add', data={'wxid': wxid}, headers={'X-API-Key': 'invalid'})
check('admin rejects invalid key', bad_key.status_code == 403)
added = client.post('/admin.php?action=api_add', data={'wxid': wxid}, headers={'X-API-Key': password})
check('admin adds authorized user', added.json()['status'] == 'success')
result = client.get('/', params={'keyword': '整合测试', 'wxid': wxid, 'start': 0}).json()
check('compatible items/url schema: 27 PNG + 1 GIF', result['code'] == 200 and len(result['items']) == 28)
check('configured public URL', all(item['url'].startswith(base + '/') for item in result['items']))
for item in result['items'][:-1]:
    u = urlsplit(item['url'])
    r = client.get(u.path + '?' + u.query)
    check('PNG ' + u.path, r.status_code == 200 and r.content.startswith(b'\x89PNG'))
    image = Image.open(io.BytesIO(r.content))
    image.verify()
check('pagination remains code 201', client.get('/', params={'keyword': '测试', 'wxid': wxid, 'start': 1}).json()['code'] == 201)
check('empty keyword remains code 200 with no external fallback', client.get('/', params={'keyword': '', 'wxid': wxid}).json()['items'] == [])
check('overlong keyword rejected', client.get('/', params={'keyword': 'x' * 121, 'wxid': wxid}).status_code == 400)
check('backend login', client.post('/admin.php?action=login', data={'pwd': password}).json()['status'] == 'success')
check('backend CSRF check', client.post('/admin.php?action=add', data={'new_id': 'csrf-check'}).status_code == 403)
unsafe_id = "quote'\"<test>"
client.post('/admin.php?action=api_add', data={'wxid': unsafe_id}, headers={'X-API-Key': password}).raise_for_status()
page = client.get('/admin.php').text
check('admin safely escapes HTML and onclick data', '&lt;test&gt;' in page and "delUser('quote" not in page)
client.post('/admin.php?action=api_delete', data={'wxid': unsafe_id}, headers={'X-API-Key': password}).raise_for_status()
if not php_only:
    check('Neon editor', client.get('/neon/').status_code == 200)
    check('Neon CSS route', client.get('/neon/static/style.css').status_code == 200)
    check('Neon JS route', client.get('/neon/static/script.js').status_code == 200)
    u = urlsplit(result['items'][-1]['url'])
    r = client.get(u.path + '?' + u.query)
    image = Image.open(io.BytesIO(r.content))
    check('returned Neon URL generates animated GIF', r.status_code == 200 and r.headers['content-type'] == 'image/gif' and image.n_frames > 1)
    time.sleep(1.1)
    r = client.get('/generate', params={'text': 'Hi', 'frame_count': 1})
    check('single-frame GIF regression', r.status_code == 200 and Image.open(io.BytesIO(r.content)).n_frames == 1)
    for path in ['/users.json', '/config.php', '/.env', '/docker-compose.yml', '/neon/main.py']:
        check('private/source route blocked ' + path, client.get(path).status_code in [403, 404])
    check('health endpoint', client.get('/healthz').json()['status'] == 'ok')
removed = client.post('/admin.php?action=api_delete', data={'wxid': wxid}, headers={'X-API-Key': password})
check('admin removes authorized user', removed.json()['status'] == 'success')
check('deleted user loses authorization', client.get('/', params={'keyword': '测试', 'wxid': wxid}).json()['code'] == 403)
print('ALL HTTP SMOKE CHECKS PASSED')
