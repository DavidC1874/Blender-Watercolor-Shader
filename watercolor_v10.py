bl_info = {
    "name": "Watercolor Shader",
    "version": (1, 0),
    "blender": (2,90,0),
    "author": "David Cai",
    "description": "Creates a watercolor shader and adds a line frame", 
    "category": "Material",
}

import bpy
from bpy.types import Panel, Operator


def create_water_group(context, operator, group_name):
    bpy.context.scene.use_nodes = True

    
    water_group = bpy.data.node_groups.new(group_name, 'ShaderNodeTree')

    
    group_in = water_group.nodes.new('NodeGroupInput')
    group_in.location = (-1000, 0)  

    
    group_out = water_group.nodes.new('NodeGroupOutput')
    group_out.location = (400, 0)


    water_group.inputs.new('NodeSocketFloat', 'Emission Strength')
    water_group.inputs.new('NodeSocketFloat', 'Factor Value')
    water_group.inputs.new('NodeSocketColor', 'Color A')
    water_group.inputs.new('NodeSocketColor', 'Color Input')


    water_group.outputs.new('NodeSocketShader', 'Shader Output')


    water_group.inputs[0].default_value = 1.7
    water_group.inputs[0].min_value = 0
    water_group.inputs[1].default_value = 5.0
    water_group.inputs[2].default_value = (0.174, 0.585, 0.704, 1)
    water_group.inputs[3].default_value = (0, 0, 0.581, 1)


    emission = water_group.nodes.new('ShaderNodeEmission')
    emission.location = (200, 100)

    color_mix1 = water_group.nodes.new('ShaderNodeMixRGB')
    color_mix1.location = (0, 300)

    noise1 = water_group.nodes.new('ShaderNodeTexNoise')
    noise1.location = (-350, 300)
    noise1.inputs[2].default_value = 6.8
    noise1.inputs[3].default_value = 0.55

    noise2 = water_group.nodes.new('ShaderNodeTexNoise')
    noise2.location = (-650, 100)
    noise2.inputs[2].default_value = 6.7
    noise2.inputs[3].default_value = 9.8

    color_mix2 = water_group.nodes.new('ShaderNodeMixRGB')
    color_mix2.location = (-350, -300)
    color_mix2.blend_type = 'DARKEN'
    color_mix2.inputs[2].default_value = (0.079, 0.016, 0.015, 1)


    water_group.links.new(group_in.outputs[0], emission.inputs[1])
    water_group.links.new(group_in.outputs[1], noise1.inputs[2])
    water_group.links.new(group_in.outputs[2], color_mix1.inputs[1])
    water_group.links.new(group_in.outputs[3], color_mix2.inputs[1])

    water_group.links.new(noise2.outputs[0], color_mix2.inputs[0])
    water_group.links.new(color_mix2.outputs[0], color_mix1.inputs[2])
    water_group.links.new(noise1.outputs[0], color_mix1.inputs[0])
    water_group.links.new(color_mix1.outputs[0], emission.inputs[0])


    water_group.links.new(emission.outputs[0], group_out.inputs[0])

    return water_group



class WaterColor(Operator):
    bl_idname = "watercolor.operator"
    bl_label = "Add a watercolor shader"

    def execute(self, context):

        custom_node_name = "Watercolor"


        my_group = create_water_group(self, context, custom_node_name)


        mat = bpy.data.materials.new(name="Watercolor_Material")
        mat.use_nodes = True
        node_tree = mat.node_tree


        material_output = node_tree.nodes.get('Material Output')


        group_node = node_tree.nodes.new('ShaderNodeGroup')
        group_node.node_tree = my_group
        group_node.location = (-200, 0)


        node_tree.links.new(group_node.outputs[0], material_output.inputs['Surface'])


        principled_bsdf = node_tree.nodes.get("Principled BSDF")
        if principled_bsdf:
            node_tree.nodes.remove(principled_bsdf)


        if context.object:
            if context.object.active_material:
                context.object.active_material = mat
            else:
                context.object.data.materials.append(mat)

        return {"FINISHED"}



class SolidifyOperator(Operator):
    bl_idname = "frame.operator"
    bl_label = "Add A Line Frame"

    def execute(self, context):

        obj = bpy.context.active_object

        if obj is None:
            self.report({'WARNING'}, "No active object selected")
            return {'CANCELLED'}


        bpy.ops.object.material_slot_add()


        line_material = bpy.data.materials.new(name="Line")


        line_material.use_backface_culling = True


        obj.material_slots[1].material = line_material


        line_material.use_nodes = True

        if line_material.use_nodes:
            node_tree = line_material.node_tree
            principled_bsdf = node_tree.nodes.get("Principled BSDF")
            if principled_bsdf:

                principled_bsdf.inputs[0].default_value = (0, 0, 0, 1)


        solidify_modifier = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
        solidify_modifier.thickness = 0.02
        solidify_modifier.offset = -1
        solidify_modifier.use_flip_normals = True
        solidify_modifier.material_offset = 1

        return {'FINISHED'}



class MyPanel(Panel):
    bl_label = "Main Panel"
    bl_idname = "watercolor_panel"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Water_Shad"

    def draw(self, context):
        layout = self.layout
        layout.scale_y = 1.4
        row = layout.row()
        row.operator("watercolor.operator")
        row = layout.row()
        row.operator("frame.operator")



classes = [MyPanel, WaterColor, SolidifyOperator]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()