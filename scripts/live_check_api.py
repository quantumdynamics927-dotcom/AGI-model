import urllib.request, json, sys

BASE = 'http://127.0.0.1:8001'
try:
    resp = urllib.request.urlopen(BASE + '/health', timeout=3)
    print('HEALTH', resp.status, resp.read().decode())
except Exception as e:
    print('HEALTH ERR', e)

try:
    resp = urllib.request.urlopen(BASE + '/certificates', timeout=5)
    data = json.load(resp)
    print('FOUND', len(data), 'certificates')
    for item in data[:50]:
        name = item.get('name') or item.get('metadata', {}).get('name')
        path = item.get('path')
        print('-', name, path)
    if data:
        name = data[0].get('name') or data[0].get('metadata', {}).get('name')
        try:
            r2 = urllib.request.urlopen(BASE + f'/certificate/{urllib.request.quote(name)}/image', timeout=5)
            print('IMG_STATUS', r2.status, 'IMG_LEN', len(r2.read()))
        except Exception as e:
            print('IMG_ERR', e)
except Exception as e:
    print('CERTS ERR', e)
