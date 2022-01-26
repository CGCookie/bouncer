'''
Copyright (C) 2021 CG Cookie
http://cgcookie.com
hello@cgcookie.com

Created by Jonathan Denning and Matthew Muldoon

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import re
import bpy
import json

config = {
    'path': os.path.dirname(os.path.abspath(__file__)),

    'reporting options': {
        'label width': 20,

        # https://www.asciiart.eu/art-and-design/dividers
        'divider style': '^-',  # '=', '-', '^-', '+-', '--/\\/', '--<>',
        'divider width': 50,

        'squash singleton lists': False,    # True=lists with one item are reported on a single line
                                            # False=all non-empty lists are reported on multiple lines
    },

    #########################################################
    # the following configure the various tests performed

    'unpacked images': {            # checks that each image is either packed or exists as external file
        'check': True,
        'ok if file exists': True,  # True=ignore warning against if image exists
    },

    'orphaned images': {            # checks for orphaned images (an image with no user)
        'check': True,
    },

    'missing libraries': {          # checks that all linked libraries exist
        'check': True,
    },

    'object names': {               # checks bpy.data.objects for avoided names (standard Blender names, duplicates,
                                    # etc.---should have a unique, descriptive name) or misspellings
        'check avoided': True,
        'check spelling': True,
        'types': [                  # check only specific types of objects
            'CURVE',
            'LATTICE',
            'CAMERA',
            'LIGHT',
            'MESH',
            'FONT',
            'ARMATURE',
            'SURFACE',
        ],
        'regexes': [                # these are regular expressions to check against names (case insensitive!)
            r'plane',
            r'cube',
            r'circle',
            r'sphere',
            r'icosphere',
            r'cylinder',
            r'cone',
            r'torus',
            r'empty',
            r'\d{3,}$',             # any name that ends with at least 3 digits
            r'^ +',                 # leading spaces are sus
            r' +$',                 # trailing spaces are even more sus
        ],
    },

    'material names': {             # checks bpy.data.materials for avoided names or misspellings
        'check avoided': True,
        'check spelling': True,
        'regexes': [                # these are regular expressions to check against names (case insensitive!)
            r'^material$',
            r'\d{3,}$',             # any name that ends in at least 3 digits
            r'^ +',                 # leading spaces are sus
            r' +$',                 # trailing spaces are even more sus
        ],
    },

    'single image BSDF': {          # checks for special case where Principled BSDF Node has exactly one image input
        'check': True,
    },
}

label_width = config['reporting options']['label width']
label_spaces = ' '*label_width

divider_width = config['reporting options']['divider width']
divider_style = config['reporting options']['divider style']


# english words from https://github.com/dwyl/english-words
english_words = {
    re.sub(r'\d', '', word.strip().lower())
    for word in open(os.path.join(config['path'], 'words.txt'), 'rt').read().splitlines()
    if word.strip()
}
def good_spelling(name):
    return all(
        part in english_words
        for part in re.split(r' |_|-|\(|\)|,|\.|\d+|<|>', name.strip().lower())
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
        if s != '' and not bool(s):
            pass
        elif type(s) is str:
            self._lines += [s]
        elif type(s) is list:
            for l in s:
                self.print(l)
        elif type(s) is tuple:
            for l in s:
                self.print(l)
        else:
            self.print(str(s))

    def nl(self, *, count=1):
        for _ in range(count):
            self.print('')

    def hr(self, *, style=None):
        global divider_width, divider_style

        if style is None: style = divider_style
        divider = (style * int(divider_width / len(style) + 1))[:divider_width]
        self.print(divider)
        # self._lines += [f'---={"-"*label_width}=-------------------------']

    def add_section_header(self, label):
        global divider_width

        self.nl(count=2)
        self.print(label)
        self.hr(style="=")

    def add_subsection_header(self, label):
        global divider_width
        self.nl()
        self.print(label)
        self.print('-' * divider_width)

    def add_subsection_ending(self):
        global divider_width
        self.print('-'*divider_width)

    def add_result(self, label, data):
        global label_width, label_spaces
        check = 'XXX' if data else ' + '
        spaces = ' ' * max(label_width - len(label), 0)

        if not bool(data):
            self.print(f'{check} {label}{spaces} ...(nothing found)...')

        elif type(data) is list:
            if config['reporting options']['squash singleton lists'] and len(data) == 1:
                self.add_result(label, data[0])
            else:
                self.add_subsection_header(f'{check} {label}')
                data = sorted(data)
                for datum in data:
                    self.print(datum)
                self.add_subsection_ending()
                self.nl()

        elif type(data) is tuple:
            self.add_subsection_header(f'{check} {label}')
            for datum in data:
                self.print(datum)
            self.add_subsection_ending()
            self.nl()

        else:
            self.print(f'{check} {label}{spaces} {data}')

    @staticmethod
    def run():
        report = Report()
        report.hr()
        report.print(f'Bouncer Report')


        ##########################################
        # the following are considered errors

        # report.hr()
        report.add_section_header('detected errors')


        if config['unpacked images']['check']:
            # find all unpacked images
            unpacked_images = [
                img
                for img in bpy.data.images
                if img.filepath and img.users and not img.packed_file
            ]
            if config['unpacked images']['ok if file exists']:
                # only consider unpacked images if image file does not exist
                unpacked_images = [
                    img
                    for img in unpacked_images
                    if bad_file(img.filepath)
                ]
            # report!
            report.add_result('unpacked images', [
                (img.name, img.filepath)
                for img in unpacked_images
            ])

        if config['orphaned images']['check']:
            # find orphaned images
            orphaned_images = [
                (img.name, img.filepath)
                for img in bpy.data.images
                if not img.users
            ]
            # report!
            report.add_result('orphaned images', orphaned_images)

        if config['missing libraries']['check']:
            # find missing libraries
            bad_libraries = [
                (lib.name, lib.filepath)
                for lib in bpy.data.libraries
                if bad_file(lib.filepath)
            ]
            # report!
            report.add_result('missing libraries', bad_libraries)

            # # find missing library images
            # library_images = [
            #     f'{img.name}: {img.library.filepath}'
            #     for img in bpy.data.images
            #     if img.library and (bad_file(img.filepath) or bad_file(img.library.filepath))
            # ]
            # # report!
            # report.add_result('library images', library_images)



        ############################################
        # the following are considered warnings

        # report.hr()
        report.add_section_header('detected warnings')


        if config['object names']['check avoided'] or config['object names']['check spelling']:
            types = config['object names']['types']
            regexes = config['object names']['regexes']
            objs = [obj for obj in bpy.data.objects if obj.type in types]
            bad_words = []
            if config['object names']['check avoided']:
                # print([
                #     (obj.name, next(re.search(regex, obj.name) for regex in regexes))
                #     for obj in objs
                #     ])
                bad_words += [
                    f'"{obj.name}"'
                    for obj in objs
                    if any(re.search(regex, obj.name.lower()) for regex in regexes)
                ]
            if config['object names']['check spelling']:
                bad_words += [
                    f'"{obj.name}"'
                    for obj in objs
                    if not good_spelling(obj.name)
                ]
            report.add_result('object names', bad_words)

        if config['material names']['check avoided'] or config['material names']['check spelling']:
            regexes = config['material names']['regexes']
            bad_words = []
            if config['material names']['check avoided']:
                bad_words += [
                    f'"{mat.name}"'
                    for mat in bpy.data.materials
                    if any(re.search(regex, mat.name.lower()) for regex in regexes)
                ]
            if config['material names']['check spelling']:
                bad_words += [
                    f'"{mat.name}"'
                    for mat in bpy.data.materials
                    if not good_spelling(mat.name)
                ]
            report.add_result('material names', bad_words)

        if config['single image BSDF']['check']:
            materials = [
                f'"{material.name}"'
                for material in bpy.data.materials
                if material.node_tree
                for node in material.node_tree.nodes
                if node.type == 'BSDF_PRINCIPLED' and sum(
                    1 if inp.is_linked and inp.links[0].from_node.type == 'TEX_IMAGE' else 0
                    for inp in node.inputs
                ) == 1
            ]
            report.add_result('single image BSDF', materials)

        report.nl(count=2)
        report.hr()
        report.nl()


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

