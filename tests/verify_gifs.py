import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

exercises = [
    'bodyweight-squat',
    'dumbbell-reverse-fly',
    'upright-row',
    'dumbbell-row',
    'crunch',
    'plank',
    'leg-raise',
    'walking'
]

for ex in exercises:
    url = f'https://fitnessprogramer.com/exercise/{ex}/'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8')
        # Find the main gif
        match = re.search(r'src="(https://fitnessprogramer\.com/wp-content/uploads/[^"]+\.gif)"', html)
        if match:
            print(f"'{ex}': '{match.group(1)}',")
        else:
            print(f"'{ex}': NO GIF FOUND on {url}")
    except Exception as e:
        print(f"'{ex}': ERR {e}")
