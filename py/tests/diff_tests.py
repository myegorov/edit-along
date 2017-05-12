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

# delta is the currency of exchange between client and server?
# or use patches?
delta = diff.diff_main(oo, nc)
print('delta:', delta)
# JSON encode
delta_json = json.dumps(delta)
print('JSON formatted delta:', delta_json)
# decode from JSON
delta_ = json.loads(delta_json)
print('delta decoded from JSON:', delta_)

# over network best to transfer patch, not diff
# calculate patches to turn original text via diff into new text (Method 3)
# returns array of patch objects
# note that dmp is happy to accept lists in place of tuples!
# patches = diff.patch_make(oo, delta)
patches = diff.patch_make(oo, delta)
patch_txt = diff.patch_toText(patches)
print("patch converted to text:", patch_txt)
# JSON encode
patch_json = json.dumps(patch_txt)
print('JSON formatted patches:', patch_json)
# decode from JSON
patch_txt_ = json.loads(patch_json)
print('patches decoded from JSON:', patch_txt_)
# reconstruct patches object
patches_ = diff.patch_fromText(patch_txt_)
assert patch_txt == patch_txt_

# compare size of diff vs text vs binary
print("diff size (bytes):", sys.getsizeof(delta))
print("patch size (bytes):", sys.getsizeof(patch_txt))
print("binary patch size (bytes):", sys.getsizeof(patches_))

## changes the object in place
# diff.diff_cleanupSemantic(delta)
# print('delta_semantic:', delta)

# html = diff.diff_prettyHtml(delta)
# print('html:', html)

# now apply patches to oo (and check for zero delta against nc) 
# and also fuzzy patch ns
# nc_ = diff.patch_apply(patches, oo) # check against nc, identical?
nc_ = diff.patch_apply(patches_, oo) # check against nc, identical?
# ns_ = diff.patch_apply(patches, ns) # check if good patch?
ns_ = diff.patch_apply(patches_, ns) # check if good patch?

# print('nc_:', nc_)
# print('nc:', nc)
assert nc_[0] == nc
# print()
# print('patches:', diff.patch_toText(patches))
# print('ns_:', ns_)
print()

# obj = {
#           'clock':[-1,-1], 
#           'edits': [[0, 'Mac'], [1, 'intoshe'], \
#                     [0, 's had the original point and click '], \
#                     [-1, 'UI'], [1, 'interface'], [0, '.']],
#           'client_id': None
#         }
# encoded = json.dumps(obj)
# decoded = json.loads(encoded)
# print(encoded)
# print(decoded)

## Try longer text

oo = """A Project Gutenberg of Australia eBook

Title: Gone With The Wind
Author: Margaret Mitchell (1900-1949)
eBook No.:  0200161.txt
Edition:    1
Language:   English
Character set encoding:     ASCII--7 bit
Date first posted: February 2002
Date most recently updated: November 2010

This eBook was produced by: Don Lainson dlainson@sympatico.ca

Project Gutenberg of Australia eBooks are created from printed editions
which are in the public domain in Australia, unless a copyright notice
is included. We do NOT keep any eBooks in compliance with a particular
paper edition.

Copyright laws are changing all over the world. Be sure to check the
copyright laws for your country before downloading or redistributing this
file.

This eBook is made available at no cost and with almost no restrictions
whatsoever. You may copy it, give it away or re-use it under the terms
of the Project Gutenberg of Australia License which may be viewed online at
http://gutenberg.net.au/licence.html

To contact Project Gutenberg of Australia go to http://gutenberg.net.au


Title:      Gone With The Wind
Author:     Margaret Mitchell (1900-1949)




PART ONE



CHAPTER I


Scarlett O'Hara was not beautiful, but men seldom realized it when
caught by her charm as the Tarleton twins were.  In her face were
too sharply blended the delicate features of her mother, a Coast
aristocrat of French descent, and the heavy ones of her florid
Irish father.  But it was an arresting face, pointed of chin,
square of jaw.  Her eyes were pale green without a touch of hazel,
starred with bristly black lashes and slightly tilted at the ends.
Above them, her thick black brows slanted upward, cutting a
startling oblique line in her magnolia-white skin--that skin so
prized by Southern women and so carefully guarded with bonnets,
veils and mittens against hot Georgia suns.

Seated with Stuart and Brent Tarleton in the cool shade of the
porch of Tara, her father's plantation, that bright April
afternoon of 1861, she made a pretty picture.  Her new green
flowered-muslin dress spread its twelve yards of billowing
material over her hoops and exactly matched the flat-heeled green
morocco slippers her father had recently brought her from Atlanta.
The dress set off to perfection the seventeen-inch waist, the
smallest in three counties, and the tightly fitting basque showed
breasts well matured for her sixteen years.  But for all the
modesty of her spreading skirts, the demureness of hair netted
smoothly into a chignon and the quietness of small white hands
folded in her lap, her true self was poorly concealed.  The green
eyes in the carefully sweet face were turbulent, willful, lusty
with life, distinctly at variance with her decorous demeanor.
Her manners had been imposed upon her by her mother's gentle
admonitions and the sterner discipline of her mammy; her eyes were
her own."""
nc = oo + " asdf"
## Looks like best to transmit patch in general, except for whole-document
## transfer cases (in the event of initial handshake, error recovery)
# nc = " asdf"

# delta is the currency of exchange between client and server
delta = diff.diff_main(oo, nc)
patches = diff.patch_make(oo, delta)
patch_txt = diff.patch_toText(patches)
# reconstruct patches object
patches_ = diff.patch_fromText(patch_txt_)

# compare size of diff vs text vs binary
print("diff size (bytes):", sys.getsizeof(delta))
print("patch size (bytes):", sys.getsizeof(patch_txt))
print("binary patch size (bytes):", sys.getsizeof(patches_))

# print ("delta:", delta)
# print("patch text:", patch_txt)


# what happens if transfering altogether new text:
oo = ''
nc = "Altogether brand new doc. See how it goes.\n or doesn't."
delta = diff.diff_main(oo, nc)
patches = diff.patch_make(oo, delta)
new_doc = diff.patch_apply(patches, "") # check that it's not rejected
print()
print("new doc:", new_doc)
print('delta:', delta)
print(diff.patch_toText(patches))


print('now apply patch to smth completely different:', diff.patch_apply(patches, "Something completely different"))

new_doc = diff.patch_apply(diff.patch_fromText(''), "asdf") # what if empty patch string??
print("empty patch applied to asdf:", new_doc) # looks like a bug?

print(diff.patch_toText(diff.patch_make('',diff.diff_main('', ''))))

### TODO: presentation

dmp_fuzzy = dmp.diff_match_patch(0.4) # fuzzy Match_Threshold

oo = "The mouse saw the cat on the mat with the hat." 
client = "The mouse saw the cat on the mat with the jet."
server = "The dog sat on the jet."

delta = diff.diff_main(client, server)
patches = diff.patch_make(client, delta)
patch_txt = diff.patch_toText(patches)
print (patch_txt)

client_patched = dmp_fuzzy.patch_apply(dmp_fuzzy.patch_fromText(patch_txt), client)
print('patched client:', client_patched)
