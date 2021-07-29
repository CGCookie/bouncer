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


# layout = self.layout
# window = context.window
# screen = context.screen
# TOPBAR_MT_editor_menus.draw_collapsible(context, layout)
# layout.separator()
# if not screen.show_fullscreen:
#     layout.template_ID_tabs(
#         window, "workspace",
#         new="workspace.add",
#         menu="TOPBAR_MT_workspace_menu",
#     )
# else:
#     layout.operator(
#         "screen.back_to_previous",
#         icon='SCREEN_BACK',
#         text="Back to Previous",
#     )



override_orig = None
def override_topbar():
    global override_orig
    undo_override_topbar()
    def new_draw_left(self, context):
        layout = self.layout
        layout.operator('cgcookie.blendermarket_tester', text='', icon='SCRIPTPLUGINS')
        override_orig(self, context)
    override_orig = bpy.types.TOPBAR_HT_upper_bar.draw_left
    bpy.types.TOPBAR_HT_upper_bar.draw_left = new_draw_left

def undo_override_topbar():
    global override_orig
    if not override_orig: return
    bpy.types.TOPBAR_HT_upper_bar.draw_left = override_orig
    override_orig = None



def register():
    bpy.utils.register_class(BlenderMarket_Tester)
    override_topbar()

def unregister():
    bpy.utils.unregister_class(BlenderMarket_Tester)
    undo_override_topbar()

if __name__ == "__main__":
    register()
