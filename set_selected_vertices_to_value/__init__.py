#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#======================= END GPL LICENSE BLOCK ========================

from bpy.props import *
import bpy
import bmesh
import math

# Version history
# 1.0.0 - 2020-09-26: Created. FWIW, this doesn't seem to work with shape keys. Need to figure this out. I have left some commented-out code to pick up with later on.
# 1.0.1 - 2020-09-26: Figured out how to make it work with shape keys.
# 1.0.2 - 2021-11-29: Moved the location of the add-on from the View3D > Properties > Animation to View3D > Properties > Item since it makes more sense there.
# 1.0.3 - 2022-08-07: Misc formatting cleanup before uploading to GitHub.

###############################################################################
SCRIPT_NAME = 'set_selected_vertices_to_value'

# This Blender add-on sets all selected vertices to a particular location value on one of the axes.
#
###############################################################################

bl_info = {
    "name": "Set Selected Vertices to Value",
    "author": "Jeff Boller",
    "version": (1, 0, 3),
    "blender": (2, 93, 0),
    "location": "View3D > Properties > Item",
    "description": "Sets all selected vertices to a particular location value on one of the axes",
    "wiki_url": "https://github.com/sundriftproductions/blenderaddon-set-selected-vertices-to-value/wiki",
    "tracker_url": "https://github.com/sundriftproductions/blenderaddon-set-selected-vertices-to-value",
    "category": "3D View"}

class SETSELECTEDVERTICESTOVALUE_PT_SetSelectedVerticesToValue(bpy.types.Operator):
    bl_idname = "ssv.set_selected_vertices_to_value"
    bl_label = "Set Selected Vertices to Value"

    def execute(self, context):
        self.report({'INFO'}, '**********************************')
        self.report({'INFO'}, SCRIPT_NAME + ' - START')

        mode = bpy.context.active_object.mode

        if mode!='EDIT':
            self.report({'ERROR'}, 'Cannot run -- not in Edit Mode!')
            return {'CANCELLED'}

        # We need to switch from Edit mode to Object mode so the selection gets updated.
        bpy.ops.object.mode_set(mode='OBJECT')
        selectedVerts = [v for v in bpy.context.active_object.data.vertices if v.select]

        if not selectedVerts:
            self.report({'ERROR'}, 'Cannot run -- no vertices selected!')
            bpy.ops.object.mode_set(mode=mode)
            return {'CANCELLED'}

        if (bpy.context.scene.ssv.enum_axes == '1'):
            self.report({'INFO'}, 'Changing X...')
        elif (bpy.context.scene.ssv.enum_axes == '2'):
            self.report({'INFO'}, 'Changing Y...')
        elif (bpy.context.scene.ssv.enum_axes == '3'):
            self.report({'INFO'}, 'Changing Z...')
        else:
            self.report({'ERROR'}, 'Cannot run -- no axis selected!')
            bpy.ops.object.mode_set(mode=mode)
            return {'CANCELLED'}

        if not bpy.context.object.data.shape_keys or not bpy.context.object.data.shape_keys.key_blocks.keys():
            # We are not using shape keys, so we can change the values of the original vertices we are working with.
            for v in selectedVerts:
                self.report({'INFO'}, 'Original vertex coords: ' + str(v.co))
                if (bpy.context.scene.ssv.enum_axes == '1'):
                    v.co.x = bpy.context.preferences.addons['set_selected_vertices_to_value'].preferences.vertex_value
                elif (bpy.context.scene.ssv.enum_axes == '2'):
                    v.co.y = bpy.context.preferences.addons['set_selected_vertices_to_value'].preferences.vertex_value
                elif (bpy.context.scene.ssv.enum_axes == '3'):
                    v.co.z = bpy.context.preferences.addons['set_selected_vertices_to_value'].preferences.vertex_value
                self.report({'INFO'}, 'New vertex coords: ' + str(v.co))
        else:
            # We ARE using shape keys, so we have to affect the currently-selected shape key, not the original vertex we pulled back.
            for v in selectedVerts:
                self.report({'INFO'}, 'Original vertex coords: ' + str(v.co))
                if (bpy.context.scene.ssv.enum_axes == '1'):
                    bpy.context.active_object.data.shape_keys.key_blocks[bpy.context.object.active_shape_key_index].data[v.index].co.x = bpy.context.preferences.addons['set_selected_vertices_to_value'].preferences.vertex_value
                elif (bpy.context.scene.ssv.enum_axes == '2'):
                    bpy.context.active_object.data.shape_keys.key_blocks[bpy.context.object.active_shape_key_index].data[v.index].co.y = bpy.context.preferences.addons['set_selected_vertices_to_value'].preferences.vertex_value
                elif (bpy.context.scene.ssv.enum_axes == '3'):
                    bpy.context.active_object.data.shape_keys.key_blocks[bpy.context.object.active_shape_key_index].data[v.index].co.z = bpy.context.preferences.addons['set_selected_vertices_to_value'].preferences.vertex_value
                self.report({'INFO'}, 'New vertex coords: ' + str(v.co))

        # Go back to whatever mode we were in.
        bpy.ops.object.mode_set(mode=mode)

        self.report({'INFO'}, '  -------------------')
        self.report({'INFO'}, SCRIPT_NAME + ' - END')
        self.report({'INFO'}, '**********************************')
        self.report({'INFO'}, 'Done running script ' + SCRIPT_NAME)

        return {'FINISHED'}

class SETSELECTEDVERTICESTOVALUE_PT_GetSelectedValue(bpy.types.Operator):
    bl_idname = "ssv.get_selected_value"
    bl_label = "Get Selected Value"

    def execute(self, context):
        mode = bpy.context.active_object.mode

        if mode!='EDIT':
            self.report({'ERROR'}, 'Cannot run -- not in Edit Mode!')
            return {'CANCELLED'}

        # We need to switch from Edit mode to Object mode so the selection gets updated.
        bpy.ops.object.mode_set(mode='OBJECT')
        selectedVerts = [v for v in bpy.context.active_object.data.vertices if v.select]

        if not selectedVerts:
            self.report({'ERROR'}, 'No vertex selected!')
            bpy.ops.object.mode_set(mode=mode)
            return {'CANCELLED'}

        if len(selectedVerts) != 1:
            self.report({'ERROR'}, 'Only one vertex can be selected!')
            bpy.ops.object.mode_set(mode=mode)
            return {'CANCELLED'}

        for v in selectedVerts:
            if (bpy.context.scene.ssv.enum_axes == '1'):
                self.report({'INFO'}, 'Getting X: ' + str(v.co.x))
                bpy.context.preferences.addons['set_selected_vertices_to_value'].preferences.vertex_value = v.co.x
            elif (bpy.context.scene.ssv.enum_axes == '2'):
                self.report({'INFO'}, 'Getting Y: ' + str(v.co.y))
                bpy.context.preferences.addons['set_selected_vertices_to_value'].preferences.vertex_value = v.co.y
            elif (bpy.context.scene.ssv.enum_axes == '3'):
                self.report({'INFO'}, 'Getting Z: ' + str(v.co.z))
                bpy.context.preferences.addons['set_selected_vertices_to_value'].preferences.vertex_value = v.co.z
            else:
                self.report({'ERROR'}, 'No axis selected!')
                #bpy.ops.object.mode_set(mode=mode)
                return {'CANCELLED'}

        # Go back to whatever mode we were in.
        bpy.ops.object.mode_set(mode=mode)

        return {'FINISHED'}

class SetSelectedVerticesPreferencesPanel(bpy.types.AddonPreferences):
    bl_idname = __module__
    vertex_value: bpy.props.FloatProperty(name='Vertex Value', default=0.00,
                                                       description='The value to set to the selected vertices')

class SETSELECTEDVERTICESTOVALUE_ScriptsProps(bpy.types.PropertyGroup):
    enum_axes: bpy.props.EnumProperty(
        name="enum_axes",
        description="Axes",
        items=[
            ('1', 'X', 'X'),
            ('2', 'Y', 'Y'),
            ('3', 'Z', 'Z')
        ], default='1')

class SETSELECTEDVERTICESTOVALUE_PT_Main(bpy.types.Panel):
    bl_idname = "SETSELECTEDVERTICESTOVALUE_PT_Main"
    bl_label = "Set Selected Vertices to Value"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"

    def draw(self, context):
        row = self.layout.row(align=True)
        self.layout.prop(context.scene.ssv, "enum_axes", expand=True)

        row = self.layout.row(align=True)
        row.prop(bpy.context.preferences.addons['set_selected_vertices_to_value'].preferences, "vertex_value")

        row = self.layout.row(align=True)
        row = self.layout.row(align=True)
        self.layout.operator("ssv.get_selected_value", icon='EYEDROPPER')

        row = self.layout.row(align=True)
        self.layout.operator("ssv.set_selected_vertices_to_value", icon='SNAP_VERTEX')

def register():
    bpy.utils.register_class(SetSelectedVerticesPreferencesPanel)
    bpy.utils.register_class(SETSELECTEDVERTICESTOVALUE_ScriptsProps)
    bpy.utils.register_class(SETSELECTEDVERTICESTOVALUE_PT_Main)
    bpy.utils.register_class(SETSELECTEDVERTICESTOVALUE_PT_SetSelectedVerticesToValue)
    bpy.utils.register_class(SETSELECTEDVERTICESTOVALUE_PT_GetSelectedValue)
    bpy.types.Scene.ssv = bpy.props.PointerProperty(type=SETSELECTEDVERTICESTOVALUE_ScriptsProps)

def unregister():
    bpy.utils.unregister_class(SetSelectedVerticesPreferencesPanel)
    bpy.utils.unregister_class(SETSELECTEDVERTICESTOVALUE_ScriptsProps)
    bpy.utils.unregister_class(SETSELECTEDVERTICESTOVALUE_PT_Main)
    bpy.utils.unregister_class(SETSELECTEDVERTICESTOVALUE_PT_SetSelectedVerticesToValue)
    bpy.utils.unregister_class(SETSELECTEDVERTICESTOVALUE_PT_GetSelectedValue)

if __name__ == "__main__":
    register()
