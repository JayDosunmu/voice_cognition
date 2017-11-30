import sys,getopt

filename = "speech16k.wav"
blocksize = 1024

opts,args = getopt.getopt(sys.argv[1:],'f:b:')
for o,a in opts:
    if o == '-f':
        filename = a
    if o == '-b':
        blocksize = a

offset = 0
with open(filename,"rb") as f:
    block = f.read(blocksize)
    string = ""
    print(str(block))
    print(type(str(block)))
    for ch in block:
        print(ord(str(ch)))
        string += hex(ord(ch))+" "
print(string)