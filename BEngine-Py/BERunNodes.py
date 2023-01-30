try:

    import bpy

    import traceback
    # from unicodedata import decimal

    import sys
    import os

    import json

    import time

    import pathlib

    try:
        from .Utils import BEUtils
    except:
        # Load BEUtils
        PACKAGE_PARENT = pathlib.Path(__file__).parent
        #PACKAGE_PARENT = pathlib.Path.cwd().parent # if on jupyter notebook
        SCRIPT_DIR = PACKAGE_PARENT
        sys.path.append(str(SCRIPT_DIR) + "/Utils")

        import BEUtils


    # def IsInstanceFromSelected(object_instance):
    #     # For instanced objects we check selection of their instancer (more accurately: check
    #     # selection status of the original object corresponding to the instancer).
    #     if object_instance.parent:
    #         return object_instance.parent.original.select_get()
    #     # For non-instanced objects we check selection state of the original object.
    #     return object_instance.object.original.select_get()


    def MainWork():
        context = bpy.context

        BEUtils.ClearScene()

        be_proj_paths = BEUtils.BEProjectPaths()

        # Base Stuff
        beBaseStuff_path = be_proj_paths.be_tmp_folder + "BEngineBaseFromEngine.json"
        js_base_stuff = BEUtils.LoadJSON(beBaseStuff_path)

        be_base_stuff = BEUtils.BEBaseStuff(js_base_stuff)

        process_gn_obj, geom_mod, node_tree = BEUtils.LoadNodesTreeFromJSON(context, be_proj_paths, be_base_stuff)

        if node_tree:

            # GET BLENDER INPUTS
            beInputs_path = be_proj_paths.be_tmp_folder + "BEngineInputs.json"
            js_input_data = BEUtils.LoadJSON(beInputs_path)

            if js_input_data:
                # If GN
                if node_tree.bl_idname == BEUtils.TYPE_GN and process_gn_obj:
                    # Set Transform
                    process_gn_obj.location = js_input_data["Pos"]
                    BEUtils.SetRotationFromJSON(process_gn_obj, js_input_data["Rot"], be_base_stuff.be_type)
                    process_gn_obj.scale = js_input_data["Scale"]

                    # Setup inputs
                    BEUtils.SetupInputsFromJSON(context, node_tree, geom_mod,
                                                js_input_data, be_proj_paths, be_base_stuff.be_type)
                    # geom_mod.show_viewport = True

                    # Set the GN Object Active and Selected
                    bpy.ops.object.select_all(action='DESELECT')
                    process_gn_obj.select_set(True)
                    context.view_layer.objects.active = process_gn_obj

                    process_gn_obj.data.update()

                    # Save Node Outputs
                    BEUtils.SaveBlenderOutputs(context, [process_gn_obj], be_proj_paths, be_base_stuff.be_type, True)

                # If SV
                elif node_tree.bl_idname == BEUtils.TYPE_SV:
                    # node_tree = node_tree.evaluated_get(context.evaluated_depsgraph_get())

                    # Setup inputs
                    BEUtils.SetupInputsFromJSON(context, node_tree, None,
                                                js_input_data, be_proj_paths, be_base_stuff.be_type)

                    # Update All Nodes
                    # node_tree.update()
                    context.view_layer.update()
                    node_tree.process_ani(True, False)

                    # Save Node Outputs
                    BEUtils.SaveBlenderOutputs(context, BEUtils.GetSVOutputObjects(node_tree), 
                                               be_proj_paths, be_base_stuff.be_type, False)

                else:
                    print("Nodes were not Loaded! Please check Paths and NodeTree Name!")
                    return False
            else:
                print("JSON Object is Empty: " + beInputs_path)
                return False

            return True

        else:
            print("Nodes were not Loaded! Please check Paths and NodeTree Name!")
            return False


    # start = time.time()

    is_done = MainWork()

    # end = time.time()
    # print(end - start)

    if is_done:
        print("!PYTHON DONE!")
    else:
        print("!PYTHON ERROR!")

except Exception as e:
    print(traceback.format_exc())
