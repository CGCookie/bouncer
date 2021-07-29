import os
import re
import bpy
import json

config = {
    # 'path to dictionary': os.path.dirname(os.path.abspath(__file__)),
    # 'path to dictionary': 'C:\\Users\\homestation\\Downloads\\market-testers-main\\market-testers-main',
    'path to dictionary': '/home/jon/projects/market-testers',

    'reporting options': {
        'label width': 20,
    },

    #########################################################
    # the following configure the various tests performed

    'unpacked images': {
        'check': True,
        'ok if file exists': True,  # True=ignore warning against if image exists
    },

    'orphaned images': {
        'check': True,
    },

    'library images': {
        'check': True,
    },

    'object names': {       # checks bpy.data.objects for avoided names (standard Blender names, duplicates, etc.---should have a unique, descriptive name) or misspellings
        'check avoided': True,
        'check spelling': True,
        'types': [          # check only specific types of objects
            'CURVE',
            'LATTICE',
            'CAMERA',
            'LIGHT',
            'MESH',
            'FONT',
            'ARMATURE',
            'SURFACE',
        ],
        'regexes': [        # these are regular expressions to check against names
            r'^Plane$',
            r'^Cube$',
            r'^Circle$',
            r'^Sphere$',
            r'^Icosphere$',
            r'^Cylinder$',
            r'^Cone$',
            r'^Torus$',
            r'^Empty$',
            r'\.\d\d\d$',   # any name that ends in period (.) followed by exactly 3 digits
        ],
    },

    'material names': {     # checks bpy.data.materials for avoided names or misspellings
        'check avoided': True,
        'check spelling': True,
        'regexes': [        # these are regular expressions to check against names
            r'^Material$',
            r"\.\d\d\d$",   # any name that ends in period (.) followed by exactly 3 digits
        ],
    },

    'single image BSDF': {  # checks for special case where Principled BSDF Node has exactly one image input
        'check': True,
    },
}

label_width = config['reporting options']['label width']
label_spaces = ' '*label_width

# english words from https://github.com/dwyl/english-words
english_words = {
    re.sub(r'\d', '', word.strip().lower())
    for word in open(os.path.join(config['path to dictionary'], 'words.txt'), 'rt').read().splitlines()
    if word.strip()
}
def good_spelling(name):
    return all(
        part in english_words
        for part in re.split(r' |_|-|\(|\)|,|\.|\d+', name.strip().lower())
        if part
    )

def bad_file(path):
    path = bpy.path.abspath(path)
    path = os.path.abspath(path)
    return not os.path.exists(path)


class Report:
    def __init__(self):
        self._lines = []

    def __str__(self):
        return '\n'.join(self._lines)

    def print(self, s):
        self._lines += [s]

    def hr(self):
        self._lines += [f'---={"-"*label_width}=-------------------------']

    def add_result(self, label, data):
        check = 'XXX' if data else ' + '
        result = f': {data}' if data else ''
        label = f'{label}{label_spaces}'[:max(len(label), label_width)]

        if not data:
            self.print(f'{check} {label} ...(nothing found)...')

        elif type(data) is list:
            data = sorted(data)
            for datum in data:
                self.print(f'{check} {label} {datum}')
                check = '   '
                label = label_spaces

        else:
            self.print(f'{check} {label} {data}')


report = Report()
report.print(f'Bouncer Report\n')
report.hr()


if config['unpacked images']['check']:
    unpacked_images = [
        img
        for img in bpy.data.images
        if img.filepath and img.users and not img.packed_file
    ]
    if config['unpacked images']['ok if file exists']:
        unpacked_images = [
            img
            for img in unpacked_images
            if bad_file(img.filepath)
        ]
    unpacked_images = [
        f'{img.name}: {img.filepath}'
        for img in unpacked_images
    ]
    report.add_result('unpacked images', unpacked_images)

if config['orphaned images']['check']:
    orphaned_images = [
        f'{img.name}: {img.filepath}'
        for img in bpy.data.images
        if not img.users
    ]
    report.add_result('orphaned images', orphaned_images)

if config['library images']['check']:
    library_images = [
        f'{img.name}: {img.library.filepath}'
        for img in bpy.data.images
        if img.library and (bad_file(img.filepath) or bad_file(img.library.filepath))
    ]
    report.add_result('library images', library_images)

if config['object names']['check avoided'] or config['object names']['check spelling']:
    types = config['object names']['types']
    regexes = config['object names']['regexes']
    objs = [obj for obj in bpy.data.objects if obj.type in types]
    bad_words = []
    if config['object names']['check avoided']:
        bad_words += [
            f'{obj.name}'
            for obj in objs
            if any(re.search(regex, obj.name) for regex in regexes)
        ]
    if config['object names']['check spelling']:
        bad_words = [
            f'{obj.name}'
            for obj in objs
            if not good_spelling(obj.name)
        ]
    report.add_result('object names', bad_words)

if config['material names']['check avoided'] or config['material names']['check spelling']:
    regexes = config['material names']['regexes']
    bad_words = []
    if config['material names']['check avoided']:
        bad_words += [
            f'{mat.name}'
            for mat in bpy.data.materials
            if any(re.search(regex, mat.name) for regex in regexes)
        ]
    if config['material names']['check spelling']:
        bad_words = [
            f'{mat.name}'
            for mat in bpy.data.materials
            if not good_spelling(mat.name)
        ]
    report.add_result('material names', bad_words)

if config['single image BSDF']['check']:
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
    report.add_result('single image BSDF', materials)

report.hr()
report.print(f'\ndone!')


# steps
# - create new window
# - switch to text editor in new window
# - create new text block
# - add content to text editor
# - open new text block in text editor
# - scroll text editor to top

bpy.ops.wm.window_new()
win = bpy.data.window_managers['WinMan'].windows[-1]
win.screen.areas[0].type = 'TEXT_EDITOR'
txt = bpy.data.texts.new('Bouncer Report')
txt.from_string(str(report))
win.screen.areas[0].spaces[0].text = txt
win.screen.areas[0].spaces[0].top = 0
win.screen.areas[0].spaces[0].show_syntax_highlight = False

