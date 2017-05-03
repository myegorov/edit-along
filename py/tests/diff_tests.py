import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import diff_match_patch as dmp

import json


diff = dmp.diff_match_patch()

# oo = 'qwerzxf\nadfa\nsdf\n'
# nn = 'werzxf\nadfa\nsdf\n'
oo = 'Macs had the original point and click UI.'
nc = 'Macintoshes had the original point and click interface.'
ns = 'Smith & Wesson had the original point and click UI.'

# delta is the currency of exchange between client and server
delta = diff.diff_main(oo, nc)
print('delta:', delta)
# JSON encode
delta_json = json.dumps(delta)
print('JSON formatted delta:', delta_json)
# decode from JSON
delta_ = json.loads(delta_json)
print('delta decoded from JSON:', delta_)

## changes the object in place
# diff.diff_cleanupSemantic(delta)
# print('delta_semantic:', delta)

# html = diff.diff_prettyHtml(delta)
# print('html:', html)

# calculate patchest to turn original text via diff into new text (Method 3)
# returns array of patch objects
# note that dmp is happy to accept lists in place of tuples!
# patches = diff.patch_make(oo, delta)
patches = diff.patch_make(oo, delta_)
# now apply patches to oo (and check for zero delta against nc) 
# and also fuzzy patch ns
nc_ = diff.patch_apply(patches, oo) # check against nc, identical?
ns_ = diff.patch_apply(patches, ns) # check if good patch?

# print('nc_:', nc_)
# print('nc:', nc)
assert nc_[0] == nc
print()
print('patches:', diff.patch_toText(patches))
print('ns_:', ns_)


print()

obj = {
          'clock':[-1,-1], 
          'edits': [[0, 'Mac'], [1, 'intoshe'], \
                    [0, 's had the original point and click '], \
                    [-1, 'UI'], [1, 'interface'], [0, '.']],
          'client_id': None
        }
encoded = json.dumps(obj)
decoded = json.loads(encoded)
print(encoded)
print(decoded)
