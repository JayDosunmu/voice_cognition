import http.client, urllib.request, urllib.parse, urllib.error, base64
import sys,getopt

from constants import ID_PROFILE, MSKEY


file_name = "speech16k.wav"
data = ''
blocksize = 1024

opts,args = getopt.getopt(sys.argv[1:],'f:b:')
for o,a in opts:
    if o == '-f':
        file_name = a
    if o == '-b':
        blocksize = a

offset = 0
with open(file_name,"rb") as f:
    block = f.read(blocksize)
    data += str(block)

headers = {
    # Request headers
    'Content-Type': 'multipart/form-data',
    'Ocp-Apim-Subscription-Key': MSKEY,
}

params = urllib.parse.urlencode({
    # Request parameters
    'shortAudio': 'false',
})

try:
    conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
    conn.request("POST", "/spid/v1.0/identificationProfiles/%s/enroll?%s" % (MSKEY, params), open(file_name, 'rb'), headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))