import urllib
import ijson
import sys

f = open(sys.argv[1])
objects = ijson.items(f, '')
print objects

for item in objects:
    for x in item["data"]:
        if x.has_key("domain"):
            print x["domain"], x["ncbi_tax_id"]

