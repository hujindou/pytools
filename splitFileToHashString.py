import hashlib
import sys

if len(sys.argv) != 2:
    print(
        "Call this program like this:\n"
        "   ./splitFileToHashString.py filename\n"
        )
    exit()

SplitSegSize = 64 * 1024



testFile = sys.argv[1]

file_hash = hashlib.md5()
with open(testFile, "rb") as fileReader:
    while True:
        bytearray = fileReader.read(SplitSegSize)
        if not bytearray:
            break
        file_hash.update(bytearray)
    pass

fileHash = file_hash.hexdigest()

print("File Hash is ", fileHash)

with open(testFile, "rb") as fileReader:
    index = 0
    while True:
        bytearray = fileReader.read(SplitSegSize)
        if not bytearray:
            break
        content = bytearray.hex()
        index += 1
        content_hash = hashlib.md5()
        content_hash.update(bytearray)
        contentarray = content_hash.digest()

        tmphash = contentarray[0] << 24 | contentarray[1] << 16 | contentarray[2] << 8 | contentarray[3]
        encodedhash = tmphash ^ index
        encodedhash = encodedhash.to_bytes(4, byteorder='big').hex()

        resultContent = fileHash[0] + encodedhash[0]\
                        + fileHash[1] + encodedhash[1]\
                        + fileHash[2] + encodedhash[2]\
                        + fileHash[3] + encodedhash[3]\
                        + fileHash[4] + encodedhash[4]\
                        + fileHash[5] + encodedhash[5]\
                        + fileHash[6] + encodedhash[6]\
                        + fileHash[7] + encodedhash[7]

        resultContent = resultContent + fileHash[8:]
        resultContent = resultContent + content

        with open(testFile + str(index) + ".txt", 'w') as out:
            out.write(resultContent)

        #print(encodedhash)
        #print(content)
        #print(resultContent)
        #print("________")
