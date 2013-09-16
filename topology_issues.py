# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2
#  of the License.
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
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "Topology check plugin",
    "author": "Mikhail Kochegarov",
    "version": (1,0,2),
    "blender": (2, 66, 0),
    "location": "View3D > EditMode > ToolShelf",
    "description": "Checks topology issues.",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Mesh"}

import bpy

class VIEW3D_PT_tools_TOPOLOGY_mesh(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "mesh_edit"
    bl_label = "Topology"
    
    @classmethod
    def poll(cls, context):
        return context.active_object
    
    def draw(self, context):
        layout = self.layout
        
        scn = context.scene
        ob = context.object
        
        col = layout.column(align=True)
        row = layout.row()
        row.separator()
        col.operator("topology.check_issues", text="Check Topology Issues")
        col.prop(scn, "TOPOLOGY_allow5poles")
        col.prop(scn, "TOPOLOGY_allowTriangles")
        col.prop(scn, "TOPOLOGY_searchEdges")
        col.operator("topology.show_5poles", text="Show 5-edge poles")
        
        
class TOPOLOGY_check_issues(bpy.types.Operator):
    bl_idname = "topology.check_issues"
    bl_label = "Check Topology issues"
    bl_description = "Checks topology issues"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        o = context.active_object

        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.context.tool_settings.mesh_select_mode = [True, False, False]
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')

        # Find polygons with more then 5 edges
        for poly in o.data.polygons:
            if (len(poly.vertices) != 4 and not bpy.context.scene.TOPOLOGY_allowTriangles) or (bpy.context.scene.TOPOLOGY_allowTriangles and (len(poly.vertices) != 4 and len(poly.vertices) != 3)):
                poly.select = True
                for vert in poly.vertices:
                    o.data.vertices[vert].select = True

        # Find poles with more then 5 edges
        poles = [0] * len(o.data.vertices)

        for edge in o.data.edges:
            poles[edge.vertices[0]]+=1;
            poles[edge.vertices[1]]+=1;

        i=0
        for pole in poles:
            if (bpy.context.scene.TOPOLOGY_allow5poles and pole>5) or (not bpy.context.scene.TOPOLOGY_allow5poles and pole>4):
                o.data.vertices[i].select = True
            # Find orphan vertices
            if pole < 3:
                o.data.vertices[i].select = True
            i = i + 1;
            
        # Find inner edges
        if bpy.context.scene.TOPOLOGY_searchEdges:
            edges = [0] * len(o.data.edges)
            
            for edge in o.data.edges:
              vert0 = edge.vertices[0]
              vert1 = edge.vertices[1]
              polys_count = 0
              for pol in o.data.polygons:
                  if vert0 in pol.vertices and vert1 in pol.vertices:
                      polys_count +=1
                      
              if polys_count > 2:
                  o.data.vertices[vert0].select = True;
                  o.data.vertices[vert1].select = True;
                  edge.select = True;
                  
        bpy.ops.object.mode_set(mode = 'EDIT')   
        
        return {"FINISHED"}
    
class TOPOLOGY_show_5poles(bpy.types.Operator):
    bl_idname = "topology.show_5poles"
    bl_label = "Show 5-edged poles"
    bl_description = "Show 5-edged poles"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        o = context.active_object

        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.context.tool_settings.mesh_select_mode = [True, False, False]
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        poles = [0] * len(o.data.vertices)

        for edge in o.data.edges:
            poles[edge.vertices[0]]+=1;
            poles[edge.vertices[1]]+=1;

        i=0
        for pole in poles:
            if pole==5:
                o.data.vertices[i].select = True
            i = i + 1;


        bpy.ops.object.mode_set(mode = 'EDIT')   
        
        return {"FINISHED"}

def register():
    bpy.utils.register_class(VIEW3D_PT_tools_TOPOLOGY_mesh)
    bpy.utils.register_class(TOPOLOGY_show_5poles)
    bpy.utils.register_class(TOPOLOGY_check_issues)
    
    bpy.types.Scene.TOPOLOGY_allow5poles = bpy.props.BoolProperty(
        name="Allow 5-edged Poles",
        description="Allow 5-sided poles in topology.",
        default=True)
        
    bpy.types.Scene.TOPOLOGY_allowTriangles = bpy.props.BoolProperty(
        name="Allow Triangles",
        description="Allow Trianles in topology.",
        default=False)

    bpy.types.Scene.TOPOLOGY_searchEdges = bpy.props.BoolProperty(
        name="Search for strange intersects",
        description="Search for strange intersects",
        default=False)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_tools_TOPOLOGY_mesh)
    bpy.utils.unregister_class(TOPOLOGY_show_5poles)
    bpy.utils.unregister_class(TOPOLOGY_check_issues)
    
    del bpy.types.Scene.TOPOLOGY_allow5poles
    del bpy.types.Scene.TOPOLOGY_allowTriangles
    del bpy.types.Scene.TOPOLOGY_searchEdges

    
if __name__ == "__main__":
    register()
    