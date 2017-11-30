import http.client, urllib.request, urllib.parse, urllib.error, base64

headers = {
    # Request headers
    'Content-Type': 'multipart/form-data',
    'Ocp-Apim-Subscription-Key': 'e5e05379080c473eab00638e44ed3ad4',
}

params = urllib.parse.urlencode({
    # Request parameters
    'shortAudio': 'false',
})

body = 

try:
    conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
    conn.request("POST", "/spid/v1.0/identificationProfiles/e5e05379080c473eab00638e44ed3ad4/enroll?%s" % params, "{body}", headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))