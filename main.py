import os
import re
import bpy
import json

path_here = os.path.dirname(os.path.abspath(__file__))

config = json.load(open(os.path.join(path_here, 'config.json'), 'rt'))
label_width = config['label width']
label_spaces = ' '*label_width

# english words from https://github.com/dwyl/english-words
good_words = {
    re.sub(r'\d', '', word.strip().lower())
    for word in open(os.path.join(path_here, 'words.txt'), 'rt').read().splitlines()
    if word.strip()
}

def fancy_report(label, data):
    check = 'XXX' if data else ' + '
    result = f': {data}' if data else ''
    label = f'{label}{label_spaces}'[:max(len(label), label_width)]

    if not data:
        print(f'{check} {label} {result}')

    elif type(data) is list:
        data = sorted(data)
        for datum in data:
            print(f'{check} {label} {datum}')
            check = '   '
            label = label_spaces

    else:
        print(f'{check} {label} {result}')


print(f'results')
print(f'---={"-"*label_width}=-------------------------')

if config['check unpacked images']:
    unpacked_images = [
        f'{img.name}: {img.filepath}'
        for img in bpy.data.images
        if img.filepath and img.users and not img.packed_file
    ]
    fancy_report('unpacked images', unpacked_images)

if config['check orphaned images']:
    orphaned_images = [
        f'{img.name}: {img.filepath}'
        for img in bpy.data.images
        if not img.users
    ]
    fancy_report('orphaned images', orphaned_images)

if config['check library images']:
    library_images = [
        f'{img.name}: {img.library.filepath}'
        for img in bpy.data.images
        if img.library
    ]
    fancy_report('library images', library_images)

if config['check avoided words']:
    avoided_words = [
        f'{obj.name}'
        for obj in bpy.data.objects
        if obj.name in config['words to avoid']
    ]
    avoided_words += [
        f'{obj.name}'
        for obj in bpy.data.objects
        if re.search(config['regex to avoid'], obj.name)
    ]
    avoided_words += [
        f'{mat.name}'
        for mat in bpy.data.materials
        if re.search(config['regex to avoid'], mat.name)
    ]
    fancy_report('avoided words', avoided_words)

if config['check single image BSDF']:
    materials = [
        f'{material.name}'
        for material in bpy.data.materials
        if material.node_tree
        for node in material.node_tree.nodes
        if node.type == 'BSDF_PRINCIPLED' and sum(
            1 if inp.is_linked and inp.links[0].from_node.type == 'TEX_IMAGE' else 0
            for inp in node.inputs
        ) == 1
    ]
    fancy_report('single image BSDF', materials)

if config['check spelling']:
    def good_spelling(name):
        name = re.sub(r'\d', '', name.strip().lower())
        parts = re.split(r' |_|-|\(|\)|,|\.', name)
        return all(part in good_words for part in parts if part)
    bad_spelling = [
        f'{obj.name}'
        for obj in bpy.data.objects
        if not good_spelling(obj.name)
    ]
    fancy_report('bad spelling', bad_spelling)

print(f'done!')