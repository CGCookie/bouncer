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

import bpy

from .main import Report

bl_info = {
    "name":        "Blender Market Testers",
    "description": "A testing suite for automating the Blender Market product review process",
    "author":      "Jonathan Denning and Matthew Muldoon",
    "version":     (0, 0, 1),
    "blender":     (2, 83, 0),
    "location":    "View 3D > Header",
    # "warning":     "Alpha",                   # used for warning icon and text in addons panel
    # "warning":     "Beta",
    # "warning":     "Release Candidate 1",
    # "warning":     "Release Candidate 2",
    "doc_url":     "https://github.com/CGCookie/market-testers/blob/main/README.md",
    "tracker_url": "https://github.com/CGCookie/market-testers/issues",
    "category":    "3D View",
}


class BlenderMarket_Tester(bpy.types.Operator):
    bl_idname = "cgcookie.blendermarket_tester"
    bl_label = "BM: Run Review Testers"
    bl_description = "A testing suite for automating the Blender Market product review process"
    bl_space_type = "EMPTY"
    # bl_region_type = ""
    bl_options = {'REGISTER'}

    def execute(self, context):
        Report.run()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BlenderMarket_Tester)

def unregister():
    bpy.utils.unregister_class(BlenderMarket_Tester)

if __name__ == "__main__":
    register()
