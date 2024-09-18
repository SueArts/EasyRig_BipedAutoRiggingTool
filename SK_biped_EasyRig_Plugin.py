"""
This plug-in tool is designed to help rig a bipedal creature for
game animation purposes inside Autodesk Maya 2023+. It operates
with PyMel and the Maya Python API 1.0.

The script generates a GUI with a 3-step system. The first sets
an initial locator hierarchy, to help position the coming joints
beforehand. The second creates the oriented joint hierarchy in
reference to the locator positions. The joint orientations should
still be checked, in order to ensure correct orientations. Lastly,
the script creates a primarily IK control rig for the entire
skeleton. Shoulders, Neck, Head and Hands are built in a FK system.

The GUI contains another automatic skinning partition, which binds
the inputted joint hierarchy to the inputted mesh. The inputted
mesh can also be unbound.

This program was built within a bachelors project. As this plug-in
handles itself as a custom script for Autodesk Maya, it is marked
as free software: You can redistribute and/or modify it.
This program is distributed in the hope that it will be useful,
but without any warranty.

Installation methods:
1) Through Maya GUI - Windows > Settings/Preferences > Plug-in Manager > Browse > your filepath > load
2) Through Python Script Editor - cmds.loadPlugin("your filepath")
Loading will take a bit as it imports PyMel core.

Execution code:
cmds.sk_biped_EasyRig()
"""

__author__ = "Suzanne Knoop"
__email__ = "suzanne.tamara@gmail.com"
__credits__ = ["Suzanne Knoop, Stella Springer"]
__date__ = "20/02/2024"
__version__ = "1.0.2"


# necessary for Plugin
import maya.OpenMaya as om
import maya.OpenMayaMPx as omx
import sys

# necessary for Script
from functools import partial
import maya.cmds as cmds
import pymel.core as pm

# Plug-in Name / to be function name
kPluginCmdName = "sk_biped_EasyRig"


# command class
class SK_RT(omx.MPxCommand):

    def __init__(self):
        omx.MPxCommand.__init__(self)

    def doIt(self, argList):

        # Auto Rigging Script
        """
        arrays:
            names - general convention for calling and creating objects
            coords - coordinates of initial locator positions, aligned with names index
            jnts - strings to call joints
            og_root_pos - root and hip positions for 'Reset to Skeleton', filled during 'Create Skeleton'

            ik_jnts_check - list of all ik joints to check their existence
            l_fingers - names intervall for left side fingers
            r_fingers - names intervall for right side fingers
            basic_ctrl_grp - controller with standard setup (position/orientation directly on to be controlled object)
            null_grp - all controller null / offset groups
            full_ctrl_grp - all controller
        """

        names = ["c_root", "c_hips", "c_spine_b", "c_spine_c", "c_chest", "c_neck", "c_head",
                 "l_thigh", "l_knee", "l_foot", "l_ball", "l_toe",
                 "l_clavicle", "l_shoulder", "l_elbow", "l_hand",
                 "l_thumb_a", "l_thumb_b", "l_thumb_c",
                 "l_pointer_a", "l_pointer_b", "l_pointer_c",
                 "l_middle_a", "l_middle_b", "l_middle_c",
                 "l_ring_a", "l_ring_b", "l_ring_c",
                 "l_pinkie_a", "l_pinkie_b", "l_pinkie_c",
                 "l_tip", "l_heel",
                 "r_thigh", "r_knee", "r_foot", "r_ball", "r_toe",
                 "r_clavicle", "r_shoulder", "r_elbow", "r_hand",
                 "r_thumb_a", "r_thumb_b", "r_thumb_c",
                 "r_pointer_a", "r_pointer_b", "r_pointer_c",
                 "r_middle_a", "r_middle_b", "r_middle_c",
                 "r_ring_a", "r_ring_b", "r_ring_c",
                 "r_pinkie_a", "r_pinkie_b", "r_pinkie_c",
                 "r_tip", "r_heel"]

        # default coordinate template (T-Pose)
        d_coords = [[0, 0, 0], [0, 97.8, -3.1], [0, 109.4, -3.1], [0, 127, -3.1], [0, 148.8, -3.1], [0, 160.2, -1.4],
                    [0, 167.7, -1.4],
                    [17, 96.2, -1.2], [17, 53, -1.2], [17, 14, -7.9], [17, 2.9, 3.7], [17, 2.8, 9.6],
                    [2.6, 149.8, -1], [17.6, 149.8, -3.4], [47.9, 149.8, -5.9], [72.1, 149.8, -5.6],
                    [79.6, 149.8, 1.9], [83.1, 149.8, 5.4], [86.6, 149.8, 8.9],
                    [88, 149.8, -1], [93.3, 149.8, -1], [97.8, 149.8, -1],
                    [89.1, 149.8, -4.7], [94.7, 149.8, -4.7], [99.6, 149.8, -4.7],
                    [88, 149.8, -8.4], [93.3, 149.8, -8.4], [97.8, 149.8, -8.4],
                    [86.8, 149.8, -11.7], [90.3, 149.8, -11.7], [94.4, 149.8, -11.7],
                    [17, 0, 9.8], [17, 0, -11.2],
                    [-17, 96.2, -1.2], [-17, 53, -1.2], [-17, 14, -7.9], [-17, 2.9, 3.7], [-17, 2.8, 9.6],
                    [-2.6, 149.8, -1], [-17.6, 149.8, -3.4], [-47.9, 149.8, -5.9], [-72.1, 149.8, -5.6],
                    [-79.6, 149.8, 1.9], [-83.1, 149.8, 5.4], [-86.6, 149.8, 8.9],
                    [-88, 149.8, -1], [-93.3, 149.8, -1], [-97.8, 149.8, -1],
                    [-89.1, 149.8, -4.7], [-94.7, 149.8, -4.7], [-99.6, 149.8, -4.7],
                    [-88, 149.8, -8.4], [-93.3, 149.8, -8.4], [-97.8, 149.8, -8.4],
                    [-86.8, 149.8, -11.7], [-90.3, 149.8, -11.7], [-94.4, 149.8, -11.7],
                    [-17, 0, 9.8], [-17, 0, -11.2]]

        # mannequin coordinates template (A-Pose)
        coords = [[0, 0, 0], [0, 97.8, -3.1], [0, 107.7, 0], [0, 127, -2.2], [0, 149.8, -9.1], [0, 160.2, -3.4],
                  [0, 167.7, -1.7],
                  [9.2, 96.2, -1.2], [13.3, 53.2, -1.2], [17.1, 14.4, -7.9], [17.1, 3, 6.9], [17.1, 2.7, 13],
                  [5.2, 149.8, -6.1], [17.6, 149.8, -10], [37.1, 126.6, -12.2], [56.8, 111.9, -0.3],
                  [57.7, 107.5, 3.8], [57.6, 105.5, 7.1], [57.8, 102.2, 9.6],
                  [63, 103.7, 6.7], [64.7, 100.1, 8.2], [65.3, 96.8, 8.9],
                  [64.5, 103.5, 4.4], [66.5, 99.9, 5.7], [67.5, 96.1, 6.5],
                  [64.6, 103, 2.2], [66.6, 99.2, 2.9], [67.4, 96, 3.5],
                  [64.1, 103, -0.1], [66, 100, 0.2], [67, 97.2, 0.4],
                  [15.9, 0.4, 13.9], [17.8, 0.4, -13.9],
                  [-9.2, 96.2, -1.2], [-13.3, 53.2, -1.2], [-17.1, 14.4, -7.9], [-17.1, 3, 6.9], [-17.1, 2.7, 13],
                  [-5.2, 149.8, -6.1], [-17.6, 149.8, -10], [-37.1, 126.6, -12.2], [-56.8, 111.9, -0.3],
                  [-57.7, 107.5, 3.8], [-57.6, 105.5, 7.1], [-57.8, 102.2, 9.6],
                  [-63, 103.7, 6.7], [-64.7, 100.1, 8.2], [-65.3, 96.8, 8.9],
                  [-64.5, 103.5, 4.4], [-66.5, 99.9, 5.7], [-67.5, 96.1, 6.5],
                  [-64.6, 103, 2.2], [-66.6, 99.2, 2.9], [-67.4, 96, 3.5],
                  [-64.1, 103, -0.1], [-66, 100, 0.2], [-67, 97.2, 0.4],
                  [-15.8, 0.4, 13.9], [-17.8, 0.4, -13.9]]

        locs = []
        jnts = []
        og_root_pos = []
        # used for controller
        ik_jnts_check = []
        l_fingers = names[16:31]
        r_fingers = names[42:57]
        basic_ctrl_grp = []
        null_grp = []
        full_ctrl_grp = []

        '''
        Function:
            check existence of objectname
            object_check - raise error if not existent or more than one exist
            non_object_check - raise error if object exists
        Vars:
            var_string / non_var_string - object to be checked
        Result: 
            raise errors if object (doesn't) exist(s)
        '''

        def object_check(var_string):
            var_check = pm.ls(var_string)
            if not pm.objExists(var_string):
                raise Exception(f"!!! Error: '{var_string}' doesn't exist.")
            else:
                if len(var_check) > 1:
                    raise Exception(f"!!! Error: More than one object called '{var_string}' exist.")

        def non_object_check(non_var_string):
            if pm.objExists(non_var_string):
                raise Exception(f"!!! Error: '{non_var_string}' already exists.")

        '''
        Function:
            lock specific transforms
            if t in trans_check true then t in transforms locked
        Vars:
            transforms - transform attributes
            axis - transform axes
            obj - assigned object
            trans_check - list of bools for transform indecies [bool, bool, bool] 
            lock - boolean for lock/unlock
            key - boolean for un-/keyable
        Result: 
            uniquely locked transform attributes on given object
        '''

        def lock_attr(l_obj, trans_check, lock, key):
            transforms = [".translate", ".rotate", ".scale"]
            axis = ["X", "Y", "Z"]
            object_check(l_obj)
            for a in axis:
                for t in range(len(transforms)):
                    if trans_check[t]:
                        pm.setAttr(l_obj + transforms[t] + a, lock=lock, keyable=key)

        '''
        Function
            recolor object with overrideColor index
        Vars:
            re_object - to be recolored object
            recol - color | red - 13, blue - 6, yellow - 17, dark red - 4
        Result:
            recolored object
        '''

        def recolor(re_obj, recol):
            object_check(re_obj)
            crv = pm.PyNode(re_obj)
            crv.overrideEnabled.set(1)
            crv.overrideColor.set(recol)

        '''
        Function:
            create, move and scale locators at coords / d_coords positions
            colorize locators
            append to locs list
        Vars:
            name_list - names
            coord_list - coords / d_coords
        Result: 
            unconnected, yellow locators that form a basic bipedal structure
        '''

        def loc_creation(name_list, coord_list):
            for (i, c) in zip(name_list, coord_list):
                non_object_check("loc_" + i)
                loc = pm.spaceLocator(name=("loc_" + i))
                pm.xform(translation=c)
                pm.scale(5, 5, 5)
                pm.select(clear=True)
                recolor(loc, 17)
                locs.append(loc)

            print("!!! Operation: Locator Creation successful.")

        '''
        Function:
            mirror one locator side to the other one
            source locator from scene
            set side (l/r), get objects of side
            get position and rotation from side object
            set position (x*-1) and rotation from other side object
        Vars:
            side - l (left)/ r (right)
            mirror_locs = l/r objects of locs
            other - opposite of l/r side
        Result:
            mirrored given side to the other
        '''

        def loc_mirror(side, *args):
            m_locs = []
            for n_obj in names:
                side_obj = "loc_" + n_obj
                object_check(side_obj)
                m_locs.append(side_obj)
            if side is "l":
                mirror_locs = m_locs[7:33]
                other = "r"
            elif side is "r":
                mirror_locs = m_locs[33:59]
                other = "l"
            else:
                raise Exception("Wrong parameter")
            for mir_loc in mirror_locs:
                loc_pos = pm.xform(mir_loc, query=True, worldSpace=True, translation=True)
                loc_rot = pm.xform(mir_loc, query=True, worldSpace=True, rotation=True)
                other_suff = mir_loc.split("loc_" + side)
                other_loc = "loc_" + other + other_suff[1]
                pm.xform(other_loc, worldSpace=True, translation=[loc_pos[0] * -1, loc_pos[1], loc_pos[2]],
                         rotation=[loc_rot[0], loc_rot[1] * -1, loc_rot[2] * -1])

        '''
        Function:
            separating hand locator from locs array
            downscaling hand locator to 2cm
        '''

        def handScale():
            hand_locs = locs[16:57]
            del hand_locs[15:26]
            for hl in hand_locs:
                pm.select(hl)
                pm.scale(2, 2, 2)

        '''
        Function:
            iterating through a 2D array
            parenting 2. element to 1. element in the list
            cycle stops when no further parent exists
        Vars:
            list - loc_grps
            grp[loc] - 2. element / child
            grp[loc-1] - 1. element / parent
        Result: 
            hierarchy chains of objects of the list
        '''

        def parenting(list):
            for grp in list:
                locator_amount = len(grp)
                for loc in range(1, locator_amount):
                    pm.parent(grp[loc], grp[loc - 1])

        '''
        Function:
            switching between a locator hierarchy and individual locators within "grp_loc_rig"
            create locator array with all locators of with name of names
            if optionMenu menuItem 1 (hierarchy) selected, create loc_grps, precaution unlock,  parent them to hierarchy, lock
            if optionMenu menuItem 2 (solo) selected, precaution unlock, parent each to "grp_loc_rig", lock
        Vars:
            proxy_locs - same as locs but flexible, relys on viewport instead of script internal variables
            loc_grps - 2D array for locator: spine, l/r arm, l/r leg, l/r single fingers
        Result:
            depending on the optionMenu selection the locator structure switches between hierarchy and individual locator
        '''

        def loc_solo_hierarchy():
            proxy_locs = []

            for loc_name in names:
                object_check("loc_" + loc_name)
                proxy_locs.append("loc_" + loc_name)

            if pm.optionMenu("hierarchy_option", query=True, select=True) == 1:

                loc_grps = [proxy_locs[1:7], proxy_locs[7:12], proxy_locs[12:16], proxy_locs[16:19], proxy_locs[19:22],
                            proxy_locs[22:25], proxy_locs[25:28], proxy_locs[28:31],
                            proxy_locs[33:38], proxy_locs[38:42], proxy_locs[42:45], proxy_locs[45:48],
                            proxy_locs[48:51],
                            proxy_locs[51:54], proxy_locs[54:57]]

                for ll in proxy_locs:
                    lock_attr(ll, [0, 0, 1], 0, 1)

                parenting(loc_grps)

                # parenting limb groups into compound hierarchy
                pm.parent(proxy_locs[31], proxy_locs[32], proxy_locs[9])
                pm.parent(proxy_locs[57], proxy_locs[58], proxy_locs[35])
                pm.parent(proxy_locs[16], proxy_locs[19], proxy_locs[22], proxy_locs[25], proxy_locs[28],
                          proxy_locs[15])
                pm.parent(proxy_locs[42], proxy_locs[45], proxy_locs[48], proxy_locs[51], proxy_locs[54],
                          proxy_locs[41])
                pm.parent(proxy_locs[1], proxy_locs[7], proxy_locs[12], proxy_locs[33], proxy_locs[38], proxy_locs[0])

                pm.parent(proxy_locs[0], "grp_loc_rig")

                for ll in proxy_locs:
                    lock_attr(ll, [0, 0, 1], 1, 1)

                pm.select(clear=True)

            if pm.optionMenu("hierarchy_option", query=True, select=True) == 2:
                for solo_l in proxy_locs:
                    lock_attr(solo_l, [0, 0, 1], 0, 1)
                for hier_loc in proxy_locs:
                    pm.parent(hier_loc, "grp_loc_rig")
                for solo_l in proxy_locs:
                    lock_attr(solo_l, [0, 0, 1], 1, 0)

                pm.select(clear=True)

        # loc_solo_hierarchy for button
        def loc_solo_hierarchy_button(*args):
            loc_solo_hierarchy()

        '''
        Function:
            complete locator hierarchy
            create group for locator
            clear locs for safety
            create locator with d_coords or coords depending on selected optionMenu Item 1 (A-Pose) or else (T-Pose)
            rescale hand locator
            recolor/ rescale heel and tips
            create locator hierarchy or individual locators inside group depending on selected optionMenu Item
        Result: 
            bipedal locator hierarchy with locked scale attributes
            ready for further personal manipulation
        '''

        def create_locator_hierarchy(*args):
            pm.currentUnit(linear="cm")

            non_object_check("grp_loc_rig")
            pm.group(name="grp_loc_rig", world=True, empty=True)

            locs.clear()

            if pm.optionMenu("pose_option", query=True, select=True) == 1:
                loc_creation(names, coords)
            else:
                loc_creation(names, d_coords)

            handScale()

            # recolor heel and tip joints
            for teel in locs[31:33] + locs[57:59]:
                recolor(teel, 4)
                pm.select(teel)
                pm.scale(3, 3, 3)

            loc_solo_hierarchy()

            print("!!! Operation: Locator Rig Creation successful.")

        '''
        Function:
            iterate through names to create named joints
            position joints at corresponding locator positions
            remove obsolete joints from outliner and array
            append joints to jnts array
        Vars:
            jnts - array for created joints
        Result: 
            single joints on corresponding locator positions
        '''

        def jnt_creation():
            for name in names:
                object_check("loc_" + name)
                non_object_check("jnt_" + name)
                pm.select(clear=True)
                jnt = pm.joint(name="jnt_" + name)
                pm.delete(pm.pointConstraint(("loc_" + name), jnt))
                jnts.append(jnt)
            jnts.remove("jnt_l_tip")
            jnts.remove("jnt_l_heel")
            jnts.remove("jnt_r_tip")
            jnts.remove("jnt_r_heel")
            pm.delete("jnt_r_heel", "jnt_r_tip", "jnt_l_heel", "jnt_l_tip")

            print("!!! Operation: Joint Creation successful.")

        '''
        Function:
            iterate through jnts array to orient separate limb hierarchies: spine, l/r arm, l/r leg, l/r single fingers
            orient last joint to none, to let if follow the same direction as previous joint
        Vars:
            j_array - jnts
            orientJ - orientJoint "xyz" - standard
            sao - secondaryAxisOrient "y-up" - standard
        Result: 
            xyz orientation with y-up as secondary axis on every limb hierarchy
        '''

        def jnt_orientation(j_array, orientJ, sao):
            for or_j in j_array:
                pm.select(or_j)
                if pm.listRelatives(allDescendents=True, children=True, type='joint'):
                    pm.joint(edit=True, orientJoint=orientJ, secondaryAxisOrient=sao, zeroScaleOrient=True)
                else:
                    pm.joint(edit=True, orientJoint="none")

        '''
        Function:
            bipedal joint skeleton with generalized joint orientations
            create joints, create limb hierarchies, orient hierarchies, general orientation adjustments
            parent limbs to compound hierarchy, group in outliner, hide locator group
        Vars:
            jnt_grps - 2D array for joints: spine, l/r arm, l/r leg, l/r individual fingers
            r_leg_or - orientation of right knee
            jnts - indices for joints
        Result: 
            Ready to be exported/worked with joint-based bipedal skeleton
        '''

        def create_joint_hierarchy(*args):
            pm.currentUnit(linear="cm")

            jnts.clear()

            jnt_creation()

            jnt_grps = [jnts[1:7], jnts[7:12], jnts[12:16], jnts[16:19], jnts[19:22], jnts[22:25], jnts[25:28],
                        jnts[28:31],
                        jnts[31:36], jnts[36:40], jnts[40:43], jnts[43:46], jnts[46:49], jnts[49:52], jnts[52:55]]

            parenting(jnt_grps)

            jnt_orientation(jnts, "xyz", "yup")

            # fixes of default orientation for orientation continuity
            # Left Arm and Hand - mirror
            jnt_orientation(jnt_grps[2], "xyz", "ydown")
            jnt_orientation(jnt_grps[3], "xyz", "ydown")
            jnt_orientation(jnt_grps[4], "xyz", "ydown")
            jnt_orientation(jnt_grps[5], "xyz", "ydown")
            jnt_orientation(jnt_grps[6], "xyz", "ydown")
            jnt_orientation(jnt_grps[7], "xyz", "ydown")

            # Left Thigh
            pm.joint(jnts[7], jnts[8], edit=True, orientJoint="xyz", secondaryAxisOrient="zup",
                     zeroScaleOrient=True)

            # Right Thigh
            pm.joint(jnts[31], edit=True, orientJoint="xyz", secondaryAxisOrient="zdown", zeroScaleOrient=True)

            # Right Foot
            pm.joint(jnts[33], edit=True, orientJoint="xyz", children=True, secondaryAxisOrient="ydown",
                     zeroScaleOrient=True)
            pm.joint(jnts[35], edit=True, orientJoint="none")

            # Right Knee orientation fix
            pm.parent(jnts[33], world=True)
            r_leg_or = pm.joint(jnts[32], query=True, orientation=True)
            pm.joint(jnts[32], edit=True, orientation=[0, r_leg_or[1], r_leg_or[2]])
            pm.parent(jnts[33], jnts[32])

            # Neck/Head
            pm.joint(jnts[4], edit=True, children=True, orientJoint="xyz", secondaryAxisOrient="ydown",
                     zeroScaleOrient=True)
            pm.joint(jnts[6], edit=True, orientJoint="none")

            # Hip
            pm.joint(jnts[1], edit=True, children=False, orientJoint="xyz", secondaryAxisOrient="ydown",
                     zeroScaleOrient=True)

            # parent limb hierarchies to compound skeletal hierarchy
            # hips/thighs
            pm.parent(jnts[7], jnts[31], jnts[1])
            # chest/clavicles
            pm.parent(jnts[12], jnts[36], jnts[4])
            # l_hand/fingers
            pm.parent(jnts[16], jnts[19], jnts[22], jnts[25], jnts[28], jnts[15])
            # r_hand/fingers
            pm.parent(jnts[40], jnts[43], jnts[46], jnts[49], jnts[52], jnts[39])
            # root/hips
            pm.parent(jnts[1], jnts[0])

            # clean-up outliner
            non_object_check("grp_bind_rig")
            pm.group(name="grp_bind_rig", empty=True)
            pm.parent(jnts[0], "grp_bind_rig")
            lock_attr("grp_bind_rig", [1, 1, 1], 1, 1)

            pm.hide("grp_loc_rig")
            pm.select(clear=True)

            # disable mirror buttons
            pm.button("b_l_mirror", edit=True, enable=False)
            pm.button("b_r_mirror", edit=True, enable=False)

            # get hip / root joint position for reset
            root_jnt_pos = pm.joint(jnts[0], query=True, position=True, absolute=True)
            hip_jnt_pos = pm.joint(jnts[1], query=True, position=True, absolute=True)
            og_root_pos.append(root_jnt_pos)
            og_root_pos.append(hip_jnt_pos)

            print("!!! Operation: Joint Hierarchy Creation successful.")

        '''
        Function:
            duplicate jnt skeleton 
            iterate through ik_jnts to rename ik skeleton
            group ik skeleton
            rename ik_c_root1 to ik_c_root
            parent groups and hierarchies
        Vars:
            ik_jnts - list of the hierarchy of "jnt_root_1"
        Result:
            separate duplicate ik skeleton 
        '''

        def create_control_rig():
            # check if original joints are there
            for check_jnt in names[0:31] + names[33:57]:
                object_check("jnt_" + check_jnt)

            # check if ik joint names already exist
            for ik_jnt_check in names:
                non_object_check("ik_" + ik_jnt_check)

            pm.duplicate("jnt_" + names[0], returnRootsOnly=True)

            pm.select("jnt_" + names[0] + "1", hierarchy=True, replace=True)
            ik_jnts = pm.ls(selection=True)

            for ik_j in ik_jnts:
                ik_suf = ik_j.split("jnt_")
                ik_joint = pm.rename(ik_j, "ik_" + ik_suf[1])
                ik_jnts_check.append(ik_joint)

            # cut the 1 from ik_root1
            pm.rename("ik_c_root1", "ik_c_root")

            # create groups
            non_object_check("grp_control_rig")
            pm.group(name="grp_control_rig", world=True, empty=True)

            non_object_check("grp_ik_rig")
            pm.group(name="grp_ik_rig", parent="grp_control_rig", empty=True)

            # parent root and legs to ik group
            non_object_check("grp_rig_system")
            pm.group(name="grp_rig_system", parent="grp_control_rig", empty=True)
            pm.parent(ik_jnts_check[0], ik_jnts_check[45], ik_jnts_check[50], "grp_ik_rig")
            pm.select(clear=True)

            print("!!! Operation: IK Rig Creation successful.")

        '''
        Function: 
            connect translate and rotate attributes of each jnt_joint to the corresponding ik_joint
            connect same attributes to the respective root joints afterwards, as they are left out in vars
        Vars:
            jnts_con - list of 'names' joints except thigh joints
            ik_con - list of 'names' IK joints except thigh joints
        Result: 
            ik skeleton drives translates and rotates of jnt skeleton
            -> ik skeleton can be modified while jnt skeleton stays untouched
        '''

        def connect_rig():
            # create arrays for hierarchies - why do they iterate twice (one without and one with clavicles)
            ik_con = []
            jnts_con = []

            for jnt_con_j in names[0:7] + names[8:31] + names[34:57]:
                jnt_con_name = "jnt_" + jnt_con_j
                ik_con_name = "ik_" + jnt_con_j
                jnts_con.append(jnt_con_name)
                ik_con.append(ik_con_name)

            # connect hierarchies
            for (ikc, jc) in zip(ik_con, jnts_con):
                object_check(ikc)
                object_check(jc)
                pm.connectAttr(ikc + ".translate", jc + ".translate", force=True)
                pm.connectAttr(ikc + ".rotate", jc + ".rotate", force=True)

            # manual connection as root isn't a descendant, thus not listed in the _con arrays
            cmds.connectAttr("ik_c_root.translate", "jnt_c_root.translate", force=True)
            cmds.connectAttr("ik_c_root.rotate", "jnt_c_root.rotate", force=True)

            # parent constraint leg bases to another
            pm.parentConstraint("ik_" + names[7], "jnt_" + names[7])
            pm.parentConstraint("ik_" + names[33], "jnt_" + names[33])

            print("!!! Operation: IK to Bind Rig Connection successful.")

        '''
        Function:
            create IK handle
            calculates start joint based on called solver (sc - parent, rp - grandparent)
        Vars:
            end - end-effector
            solv - IK solver (sc - singleChain, rp - rotatePlane)
        Result: 
            IK handle on chosen joints
        '''

        def create_ik(end, solv):
            suf = end.split("ik_")
            startRP = pm.listRelatives(pm.listRelatives(end, parent=True), parent=True)
            startSC = pm.listRelatives(end, parent=True)
            if solv is "sc":
                pm.ikHandle(name="hdl_" + suf[1], solver="ikSCsolver", startJoint=startSC[0], endEffector=end)
            if solv is "rp":
                pm.ikHandle(name="hdl_" + suf[1], solver="ikRPsolver", startJoint=startRP[0], endEffector=end)
            pm.parent("hdl_" + suf[1], "grp_rig_system")

        '''
        Function:
            create offset group for initial locator placement - group keeps transforms, locator stays zeroed out
            pole vector constraint from locator to corresponding IK handle
            PV fix - create 2 supp locator to parent ik supp to ik elbow and jnt supp to jnt elbow 
                     > move locator to trans > unparent supp > parent PV grp to ik support > move ik supp to jnt supp
                     > unparnt PV grp > delete supp locator
                     -> ik elbow should be at the same position als jnt elbow
        Vars:
            prnt - elbow/knee joint, where locator will be created
            hdl - IK handle, on which the constraint will be added
            trans - translation coordinates to move offset-group to base position (away from the joint)
            grp - offset group for PV locator
            loc_pj - support locator to be parented to jnt elbow
            loc_pi - support locator to be parented to ik elbow
        Result: 
            correctly positioned pole vector constraint for chosen ik handle and locator
        '''

        def setupPV(prnt, hdl, trans):
            # create PV setup with locator
            prnt_s = prnt.split("ik_")
            grp = pm.group(empty=True, parent=prnt, absolute=False, name=("grp_null_PV_" + prnt_s[1]))
            pm.parent(world=True)
            pm.parent(pm.spaceLocator(name="loc_PV_" + prnt_s[1]), grp, relative=True)
            pm.poleVectorConstraint(("loc_PV_" + prnt_s[1]), hdl)

            # setup 2 locator to fix the IK wiggle when PV positions
            loc_pj = pm.spaceLocator()
            loc_pi = pm.spaceLocator()
            pm.parent(loc_pj, ("jnt_" + prnt_s[1]), relative=True)
            pm.parent(loc_pi, prnt, relative=True)
            pm.xform(loc_pj, loc_pi, grp, translation=trans, relative=True, objectSpace=True, worldSpaceDistance=True)

            # create temporary hierarchy to correctly align PV through loc_pj and loc_pi positions
            pm.parent(loc_pj, loc_pi, world=True)
            pm.parent(grp, loc_pi)
            pm.delete(pm.parentConstraint(loc_pj, loc_pi, maintainOffset=False))
            pm.parent(grp, "grp_rig_system")
            pm.delete(loc_pj, loc_pi)

        '''
        Function:
            reverse foot rig: working from toe to leg
            create, name and position locator
            parent locator and leg IK handles
            group reverse rig
            -> toe moves ball when used, both move with heel when used, ball just moves itself
        Vars:
            feet - foot locator of locs in correct sequence for reverse rig
            ik_feet - list of created ik locator
            ik_feet_grp - 2D array with l/r ik locator
            names - indices for object names
        Result: 
            reverse foot setup for both feet, ready to be installed into ctrls
            ideal setup for ground/foundation movement
        '''

        def reverseFoot():
            # create locators - l/r heel>tip>ball
            feet = ["loc_" + names[32], "loc_" + names[31], "loc_" + names[10], "loc_" + names[58],
                    "loc_" + names[57], "loc_" + names[36]]
            ik_feet = []
            for fl in feet:
                non_object_check("ik_" + fl)
                f_loc = pm.spaceLocator(name=("ik_" + fl))
                pm.delete(pm.pointConstraint(fl, f_loc))
                ik_feet.append(f_loc)

            # group into lists for parenting
            ik_feet_grp = []
            ik_feet_grp.append(ik_feet[0:3])
            ik_feet_grp.append(ik_feet[3:7])

            parenting(ik_feet_grp)

            # parentIK handles to locator structure
            pm.parent("hdl_" + names[35], "hdl_" + names[36], "ik_loc_" + names[36])
            pm.parent("hdl_" + names[9], "hdl_" + names[10], "ik_loc_" + names[10])
            pm.parent("hdl_" + names[37], "ik_loc_" + names[58])
            pm.parent("hdl_" + names[11], "ik_loc_" + names[32])

            # create and parent to groups
            non_object_check("grp_null_" + names[32])
            pm.group(name="grp_null_" + names[32], empty=True)
            pm.delete(pm.parentConstraint("ik_loc_" + names[32], "grp_null_" + names[32]))

            non_object_check("grp_null_" + names[58])
            pm.group(name="grp_null_" + names[58], empty=True)
            pm.delete(pm.parentConstraint("ik_loc_" + names[58], "grp_null_" + names[58]))

            pm.parent("ik_loc_" + names[32], "grp_null_" + names[32])
            pm.parent("ik_loc_" + names[58], "grp_null_" + names[58])

            pm.parent("grp_null_" + names[32], "grp_null_" + names[58], "grp_rig_system")

            print("!!! Operation: Reverse Foot Setup successful.")

        '''
        Function:
            freeze transforms of called object
            delete non-deformer history of called object
        Vars:
            fdh_obj - called object
        '''

        def freezeDelHistory(fdh_obj):
            object_check(fdh_obj)
            pm.makeIdentity(fdh_obj, apply=True, translate=True, rotate=True, scale=True)
            pm.delete(fdh_obj, constructionHistory=True)
            pm.select(clear=True)

        '''
        Functions:
            adjusted controller curves for each limb, including recolor
            crv_basic - nurbs circle, for fingers and neck
            hands_core - diamond shaped nurbs curve, for hands, root and centerOfMass
            feet_core - nurbs curve shaped to UE Mannequin, for feet and shoulderblades
            crv_kneel - pyramid shaped nurbs curve, for knees and elbows
            chest_core - organic, swung nurbs curve, for chest and head
            crv_spine_b / crv_spine_c - nurbs circle formed to corresponding torso partitions
        Inside basic_ctrl_grp:
            crv_basic, crv_hands, crv_root, crv_centerOfMass, crv_chest, crv_head, crv_spineB, crv_spineC
        '''

        # basic circle
        def crv_basic(basic_name, b_scale, b_col):
            non_object_check(basic_name)
            crv = pm.circle(name=basic_name)
            pm.scale(basic_name, b_scale, b_scale, b_scale)
            pm.rotate(basic_name, 0, 90, 0)
            recolor(basic_name, b_col)
            freezeDelHistory(basic_name)
            basic_ctrl_grp.append(basic_name)

        # hands core
        def hands_core(hands_core_name):
            non_object_check(hands_core_name)
            pm.curve(name=hands_core_name, degree=1, point=[(0, 0, -9), (-9, 0, 0), (0, 0, 9), (9, 0, 0), (0, 0, -9)],
                     knot=[0, 1, 2, 3, 4])

        # hands
        def crv_hands(hands_name, h_col):
            hands_core(hands_name)
            pm.rotate(hands_name, 0, 0, 90)
            recolor(hands_name, h_col)
            basic_ctrl_grp.append(hands_name)

        # root
        def crv_root(root_name):
            hands_core(root_name)
            pm.scale(root_name, 5.8, 5.8, 5.8)
            pm.rotate(root_name, 0, 0, 0)
            recolor(root_name, 4)
            basic_ctrl_grp.append(root_name)

        # center of mass
        def crv_centerOfMass(com_name):
            hands_core(com_name)
            pm.scale(com_name, 2.9, 2.9, 2.9)
            pm.rotate(com_name, 0, 0, 90)
            recolor(com_name, 4)
            basic_ctrl_grp.append(com_name)

        # feet core
        def feet_core(feet_core_name):
            non_object_check(feet_core_name)
            pm.curve(name=feet_core_name, degree=3,
                     point=[(-6.192026, 0, -7.222708), (-7.145403, 0, -1.658433), (-9.052156, 0, 9.470118),
                            (-4.930124, 0, 14.939794), (7.070467, 0, 18.394924), (4.812628, 0, 1.483525),
                            (6.788087, 0, -9.800724), (1.855148, 0, -17.409909), (-4.789274, 0, -17.035881),
                            (-5.724442, 0, -10.493766), (-6.192026, 0, -7.222709)],
                     knot=[0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8])

        # feet
        def crv_feet(feet_name, f_col):
            feet_core(feet_name)
            recolor(feet_name, f_col)

        # shoulderblades
        def crv_shoulder(shoulder_name, s_col):
            feet_core(shoulder_name)
            pm.rotate(shoulder_name, 0, 15, 0, relative=True, objectSpace=True, forceOrderXYZ=True)
            pm.scale(shoulder_name, 1.222765, 1, 1, relative=True)
            recolor(shoulder_name, s_col)

        # elbow/knee
        def crv_kneel(kneel_name, ke_col):
            non_object_check(kneel_name)
            pm.curve(name=kneel_name, degree=1,
                     point=[(-4.469147, 0, -3.90705e-07), (-1.95353e-07, 0, 4.469147), (0, 8.938294, 0),
                            (4.469147, 0, 0),
                            (5.86058e-07, 0, -4.469147), (0, 8.938294, 0), (-4.469147, 0, -3.90705e-07),
                            (5.86058e-07, 0, -4.469147), (4.469147, 0, 0), (-1.95353e-07, 0, 4.469147)],
                     knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
            recolor(kneel_name, ke_col)

        # chest core
        def chest_core(chest_core_name):
            non_object_check(chest_core_name)
            pm.circle(name=chest_core_name)
            pm.rotate(chest_core_name, 90, 0, 0)
            pm.scale(chest_core_name, 25, 25, 25, relative=True)
            pm.makeIdentity(chest_core_name, apply=True, rotate=True, scale=True)
            pm.select(chest_core_name + ".cv[1]", chest_core_name + ".cv[5]", replace=True)
            pm.scale(1, 1, 0.657641, relative=True, pivot=(0, 142.343345, -4.855895))
            pm.select(chest_core_name + ".cv[6]", chest_core_name + ".cv[0]", chest_core_name + ".cv[2]",
                      chest_core_name + ".cv[4]", replace=True)
            pm.move(0, -8.118699, 0, relative=True, objectSpace=True, worldSpaceDistance=True)
            pm.select(chest_core_name + ".cv[3]", chest_core_name + ".cv[7]", replace=True)
            pm.scale(0.780896, 0.780896, 0.780896, relative=True, pivot=(-1.019395, 0.569853, 0))
            pm.move(0, -13.464986, 0, relative=True, objectSpace=True, worldSpaceDistance=True)
            pm.rotate(chest_core_name, 0, 0, 90, objectSpace=True)
            recolor(chest_core_name, 17)
            pm.select(clear=True)

        # chest
        def crv_chest(chest_name):
            chest_core(chest_name)
            pm.scale(chest_name, 0.9, 0.3, 0.9)
            pm.rotate(chest_name, 0, 0, 43.5 + 28.4)
            pm.move(chest_name, -3.8, 3.5, 0, relative=True)
            pm.move(3.8, -3.5, 0, chest_name + ".scalePivot", chest_name + ".rotatePivot", relative=True)
            basic_ctrl_grp.append(chest_name)

        # head
        def crv_head(head_name):
            chest_core(head_name)
            pm.scale(head_name, 0.52, 0.1, 0.4)
            pm.move(head_name, 9.1, 0, 0, relative=True)
            pm.move(-9.1, 0, 0, head_name + ".scalePivot", head_name + ".rotatePivot", relative=True)
            basic_ctrl_grp.append(head_name)

        # spine a/b
        def crv_spineB(spineB_name):
            non_object_check(spineB_name)
            pm.circle(name=spineB_name)
            pm.scale(spineB_name, 20.3, 20.3, 17.6)
            pm.rotate(spineB_name, 0, 90, 0)
            recolor(spineB_name, 17)
            basic_ctrl_grp.append(spineB_name)

        def crv_spineC(spineC_name):
            non_object_check(spineC_name)
            pm.circle(name=spineC_name)
            pm.scale(spineC_name, 22.9, 22.9, 20.3)
            pm.rotate(spineC_name, 0, 90, 0)
            # rotZ -73.350
            recolor(spineC_name, 17)
            basic_ctrl_grp.append(spineC_name)

        '''
        Function:
            iterate through r_/l_fingers to create scaled crv_basic for each joint
        Result:
            size adjusted FK finger ctrls
        '''

        def crv_fingers():
            # create right finger ctrls
            for rf in r_fingers:
                non_object_check("ctrl_" + rf)
                if rf.endswith("_a"):
                    crv_basic(("ctrl_" + rf), 2.2, 6)
                else:
                    crv_basic(("ctrl_" + rf), 1.6, 6)
            # create left finger ctrls
            for lf in l_fingers:
                non_object_check("ctrl_" + lf)
                if lf.endswith("_a"):
                    crv_basic(("ctrl_" + lf), 2.2, 13)
                else:
                    crv_basic(("ctrl_" + lf), 1.6, 13)
                    # size adjustments for first 2 thumb ctrls
            pm.xform("ctrl_" + names[16], "ctrl_" + names[17], "ctrl_" + names[42], "ctrl_" + names[43],
                     scale=[1.5, 1.5, 1.5])

        '''
        Function:
            create named offset group for to be grouped controller
            parent controller to group
            position and orient group to to be controlled object 
            group controller in "grp_controls"
            append group to null_grp
        Var:
            pref - prefix | "ik_", "loc_"
            g_ctrl - to be grouped controller
            ctrls_grp - offset group for controller
            ctrl_jnt - to be controlled object
        Result:
            correctly positioned and oriented offset group with controller inside, controller stays zeroed out
            ctrl_jnt - used for c_jnt in feet_ctrl_position()
        '''

        # control grouping funktion mit ctrl_jnt aus gabe für pivot nutzung
        def ctrl_grp_prep(pref, g_ctrl):
            object_check(g_ctrl)
            pm.select(clear=True)
            ctrls_grp = pm.group(name=("grp_null_" + g_ctrl))
            ctrl_suf = g_ctrl.split("ctrl_")
            ctrl_jnt = (pref + ctrl_suf[1])
            pm.parent(g_ctrl, ctrls_grp)
            pm.delete(pm.parentConstraint(ctrl_jnt, ctrls_grp))
            pm.parent(ctrls_grp, "grp_controls")
            null_grp.append(ctrls_grp)
            return ctrl_jnt

        '''
        Function:
            iterate through basic_ctrl_grp
            position these controller groups with ctrl_grp_prep()
        '''

        # basic contoller positioning with grouping
        def basic_ctrl_position():
            for ctrl in basic_ctrl_grp:
                ctrl_grp_prep("ik_", ctrl)
                freezeDelHistory(ctrl)

        '''
        Function:
            feet controller position
            create, parent, position, orient group to c_jnt
            rotate group to y zero to be parallel to ground
            get c_jnt position, set ctrl translation yz to 0 > centered on ground beneath ik joint
            set ctrl pivot to c_jnt translation
            freezeDelHistory() to zero out transforms
        Vars:
            f_ctrl - controller name
            gx rot - group x rotation for mirrored parallel transforms
            gz rot - group z rotation for mirrored parallel transforms
            f_rot_corr - z rotation correction for left controller (180)
            c_jnt - ctrl_grp_prep() -> corresponding ik joint
            jnt_pvt - query c_jnt -> returned ctrl_jnt (to be controlled object)
        Result:
            foot controller inside an offset group at yz 0, beneath the corresponding ik joint
        '''

        def feet_ctrl_position(f_ctrl, gx_rot, gz_rot, f_rot_corr):
            object_check(f_ctrl)
            # prepare group
            c_jnt = ctrl_grp_prep("ik_", f_ctrl)
            pm.rotate(("grp_null_" + f_ctrl), gx_rot, 0, gz_rot)
            # move ctrl and pivot
            jnt_pvt = pm.joint(c_jnt, query=True, position=True)
            pm.xform(f_ctrl, worldSpace=True, translation=[jnt_pvt[0], 0, 0], rotation=[0, 0, f_rot_corr])
            pm.xform(f_ctrl, pivots=jnt_pvt, worldSpace=True)
            pm.parent(f_ctrl, ("grp_null_" + f_ctrl))
            freezeDelHistory(f_ctrl)

        '''
        Function:
            shoulderblade controller position
            create, parent, position, orient group to ik joint
            x rotate correction (90/-90) for proper shape orientation
            move shape back, rotate it to align it parallel to back
            move pivot back to group
            freezeDelHistory() to zero out transforms
        Vars:
            s_ctrl - shoulderblade controller
            s_rot_corr - x rotate correction (90/-90)
            rrev - reverse rotation (-1/1) adjustment for mirrored pivot sides -> parallel alignment
        Result:
            parallely to back aligned shoulderblade wing controller
        '''

        def shoulder_ctrl_position(s_ctrl, s_rot_corr, rrev):
            object_check(s_ctrl)
            ctrl_grp_prep("ik_", s_ctrl)
            pm.rotate(s_ctrl, s_rot_corr, 0, 0)
            pm.select((s_ctrl + "Shape"), replace=True)
            pm.move((rrev * 7), -7, -17, worldSpace=True, relative=True)
            pm.rotate((rrev * -7), 0, (rrev * -18.8), worldSpace=True, relative=True)
            pm.move((rrev * -7), 7, 17, s_ctrl + ".scalePivot", s_ctrl + ".rotatePivot", relative=True)
            freezeDelHistory(s_ctrl)

        '''
        Function:
            knee and elbow controller position
            create, parent, position, orient group to PV locator
            rotate pyramid shape point towards elbow/knee
            freezeDelHistory() to zero out transforms
        Vars:
            ke_ctrl - controller
            rotX_corr - rotate x correction (90,0)
            rotZ_corr - rotate z correction (0,180)
        Result:
            pointing pyramid shape at PV position
        '''

        # kneel und spineB/C müssen jeweils mit locator und cluster verbunden werden
        def kneel_ctrl_position(ke_ctrl, rotX_corr, rotZ_corr):
            object_check(ke_ctrl)
            ctrl_grp_prep("loc_", ke_ctrl)
            pm.rotate(ke_ctrl, rotX_corr, 0, rotZ_corr, relative=True)
            freezeDelHistory(ke_ctrl)

        '''
        Function:
            create "grp_controls" to parent controllers to it
            parent it to "grp_control_rig"
            executing controller creation
            executing grouping and positioning for controllers
            rotate y to 0 on all spine and head groups, excluding neck
            rotate z adjustment on neck controller to align it more with mesh-neck
            freezeDelHistory() on neck controller
        Vars:
            null_grp - indices for controller groups
            names - indices for controller names
        Result:
            unconnected controller setup, keeping bipedal balance in mind
        '''

        def nurbs_controller():
            pm.parent(pm.group(name="grp_controls", empty=True), "grp_control_rig")
            # curve creation
            # basic / on joints
            crv_root("ctrl_" + names[0])
            crv_centerOfMass("ctrl_" + names[1])
            crv_spineB("ctrl_" + names[2])
            crv_spineC("ctrl_" + names[3])
            crv_chest("ctrl_" + names[4])
            crv_basic(("ctrl_" + names[5]), 10, 17)  # neck
            crv_head("ctrl_" + names[6])
            crv_hands("ctrl_" + names[15], 13)
            crv_hands("ctrl_" + names[41], 6)
            crv_fingers()

            # different parent knee/elbow locator
            crv_kneel("ctrl_PV_" + names[8], 13)
            crv_kneel("ctrl_PV_" + names[34], 6)
            crv_kneel("ctrl_PV_" + names[14], 13)
            crv_kneel("ctrl_PV_" + names[40], 6)

            # different parenting style clavicles/feet
            crv_shoulder("ctrl_" + names[12], 13)
            crv_shoulder("ctrl_" + names[38], 6)
            crv_feet("ctrl_" + names[9], 13)
            crv_feet("ctrl_" + names[35], 6)

            print("!!! Operation: Controller Creation successful.")

            # group positioning - fill null_grp
            basic_ctrl_position()

            shoulder_ctrl_position("ctrl_" + names[12], 90, 1)
            shoulder_ctrl_position("ctrl_" + names[38], -90, -1)
            feet_ctrl_position("ctrl_" + names[9], 90, -90, 180)
            feet_ctrl_position("ctrl_" + names[35], -90, -90, 0)

            kneel_ctrl_position("ctrl_PV_" + names[14], 90, 0)
            kneel_ctrl_position("ctrl_PV_" + names[40], 90, 0)
            kneel_ctrl_position("ctrl_PV_" + names[8], 0, 0)
            kneel_ctrl_position("ctrl_PV_" + names[34], 0, 180)

            # controller adjustments
            # center of mass ctrl muss auf rotate Y ausgenullt werden, damit es parallel zum Boden läuft
            pm.rotate(null_grp[1], 0, rotateY=True, absolute=True)
            pm.rotate(null_grp[2], 0, rotateY=True, absolute=True)
            pm.rotate(null_grp[3], 0, rotateY=True, absolute=True)
            pm.rotate(null_grp[4], 0, rotateY=True, absolute=True)
            pm.rotate(null_grp[6], 0, rotateY=True, absolute=True)
            # adjust neck controller to visually line up with neck
            pm.rotate("ctrl_" + names[5], 12, rotateZ=True)
            freezeDelHistory("ctrl_" + names[5])

            print("!!! Operation: Controller Positioning successful.")

        '''
        Function:
            orient, point and parent constrain joints, handles and controls to respective controlling parts
        Vars:
            finger_names - combination of r_fingers and l_fingers
            full_ctrl_grp - indices for controller
        Result:
            functional controllers that can be moved individually
        '''

        def ctrl_functionality():
            # constrain controller to rig system
            # Pole Vector
            pm.pointConstraint(full_ctrl_grp[46], "grp_null_PV_" + names[34])
            pm.pointConstraint(full_ctrl_grp[45], "grp_null_PV_" + names[8])
            pm.pointConstraint(full_ctrl_grp[44], "grp_null_PV_" + names[40])
            pm.pointConstraint(full_ctrl_grp[43], "grp_null_PV_" + names[14])
            pm.hide("grp_null_PV_" + names[34], "grp_null_PV_" + names[8], "grp_null_PV_" + names[40],
                    "grp_null_PV_" + names[14])

            # Arms
            pm.pointConstraint(full_ctrl_grp[7], "hdl_" + names[15])
            pm.pointConstraint(full_ctrl_grp[8], "hdl_" + names[41])
            pm.orientConstraint(full_ctrl_grp[7], "ik_" + names[15])
            pm.orientConstraint(full_ctrl_grp[8], "ik_" + names[41])

            # Root
            pm.parentConstraint(full_ctrl_grp[0], "ik_" + names[0])

            # legs - heel
            pm.parentConstraint(full_ctrl_grp[1], "ik_" + names[7], maintainOffset=True)
            pm.parentConstraint(full_ctrl_grp[1], "ik_" + names[33], maintainOffset=True)
            pm.parentConstraint(full_ctrl_grp[41], "grp_null_" + names[32], maintainOffset=True)
            pm.parentConstraint(full_ctrl_grp[42], "grp_null_" + names[58], maintainOffset=True)

            # spine
            pm.parentConstraint(full_ctrl_grp[1], "ikh_" + names[1], maintainOffset=True)
            pm.orientConstraint("ikh_" + names[1], "ik_" + names[1], maintainOffset=True)
            pm.pointConstraint(full_ctrl_grp[2], "ikh_" + names[2], maintainOffset=True)
            pm.pointConstraint(full_ctrl_grp[3], "ikh_" + names[3], maintainOffset=True)
            pm.parentConstraint(full_ctrl_grp[4], "ikh_" + names[4], maintainOffset=True)
            pm.orientConstraint(full_ctrl_grp[4], "ik_" + names[4], maintainOffset=True)
            pm.orientConstraint(full_ctrl_grp[5], "ik_" + names[5], maintainOffset=True)
            pm.orientConstraint(full_ctrl_grp[6], "ik_" + names[6], maintainOffset=True)

            # shoulders
            pm.orientConstraint(full_ctrl_grp[39], "ik_" + names[12], maintainOffset=True)
            pm.orientConstraint(full_ctrl_grp[40], "ik_" + names[38], maintainOffset=True)

            finger_names = l_fingers + r_fingers
            for fn in finger_names:
                pm.orientConstraint("ctrl_" + fn, "ik_" + fn)

            print("!!! Operation: Controller Functionality successful.")

        '''
        Function:
            iterate through finger_array to divide it into triplets
            append triplets to single_fingers
        Vars:
            finger_array - r_fingers / l_fingers
            single_fingers - array for separate finger lists
        Result:
            2D array with separate finger lists for controller group parenting
        '''

        def finger_triplets(finger_array):
            single_fingers = []
            # get finger triplets
            for sf in range(0, len(finger_array), 3):
                single = finger_array[sf:sf + 3]
                single_fingers.append(single)
            return single_fingers

        '''
        Function:
            parenting ctrl groups to ctrls into a hierarchy for compound movement
            hip ctrl- grps: spine_b
            root ctrl - grps: hip, chest, l/r hands, l/r feet, knee PVs, elbow PVs
            chest ctrl - grps: spine_c, shoulderblades, neck
            neck ctrl - grps: head
            l_hand ctrl - grps: l_thumb_a, l_pointer_a, l_middle_a, l_ring_a, l_pinkie_a
            r_hand ctrl - grps: r_thumb_a, r_pointer_a, r_middle_a, r_ring_a, r_pinkie_a

            2D arrays for compound finger ctrls and grps
            parent current element of grps to previous element of ctrls to create hierarchy
        Vars:
            all_finger_grps - 
            all_finger_ctrls
        Result:
            compound usable controller hierarchy, which moves in relation to another
        '''

        def ctrl_hierarchy():
            # parenting controls together
            # spine / torso
            pm.parent(null_grp[2], full_ctrl_grp[1])
            pm.parent(null_grp[7:9], null_grp[41:43], null_grp[1], null_grp[4], null_grp[45:47], null_grp[43:45],
                      full_ctrl_grp[0])
            pm.parent(null_grp[39:41], null_grp[3], null_grp[5], full_ctrl_grp[4])
            pm.parent(null_grp[6], full_ctrl_grp[5])
            # hands
            pm.parent(null_grp[24], null_grp[27], null_grp[30], null_grp[33], null_grp[36], full_ctrl_grp[7])
            pm.parent(null_grp[9], null_grp[12], null_grp[15], null_grp[18], null_grp[21], full_ctrl_grp[8])

            # arrays for finger grps and ctrls
            all_finger_grps = null_grp[9:24] + null_grp[24:39]
            all_finger_ctrls = full_ctrl_grp[9:24] + full_ctrl_grp[24:39]

            # similar to parenting(), arrays of fingers in one
            finger_grps = finger_triplets(all_finger_grps)
            finger_ctrls = finger_triplets(all_finger_ctrls)
            # iterate through both arrays, use 1. as reference point
            # parent current element of grps to previous element of ctrls
            for (f_grp, f_ctrl) in zip(finger_grps, finger_ctrls):
                finger_len = len(f_grp)
                for fp in range(1, finger_len):
                    pm.parent(f_grp[fp], f_ctrl[fp - 1])

            print("!!! Operation: Controller Hierarchy successful.")

        '''
        Function:
            add toe, ball, heel float attributes to foot with max and min values
            connect custom attributes to respective rotate x attributes of reverse rig locator
        Result:
            toe, ball, heel attributes for foot roll possibility on foot
        '''

        def addFeetAttr(foot_ctrl, side):
            object_check(foot_ctrl)
            pm.addAttr(foot_ctrl, shortName="tip", longName="Tip", defaultValue=0, minValue=0, maxValue=160,
                       keyable=True)
            pm.addAttr(foot_ctrl, shortName="ball", longName="Ball", defaultValue=0, minValue=0, maxValue=70,
                       keyable=True)
            pm.addAttr(foot_ctrl, shortName="heel", longName="Heel", defaultValue=0, minValue=-90, maxValue=50,
                       keyable=True)

            pm.connectAttr(foot_ctrl + ".tip", "ik_loc_" + side + "_tip.rotateX")
            pm.connectAttr(foot_ctrl + ".ball", "ik_loc_" + side + "_ball.rotateX")
            pm.connectAttr(foot_ctrl + ".heel", "ik_loc_" + side + "_heel.rotateX")

            print("!!! Operation: Foot Attribute Setup successful.")

        '''
        Function:
            reset IK control related arrays
            complete IK control rig
            create ik skeleton
            IK + PV integration
            connect jnt skeleton to ik skeleton
            create IK spline handle
            create 4 ikh (long: ik handle) joints, position them at their ik counter parts
            bind IK spline to ikh joints
            setup advanced twist control attributes for twistable spine
            connect spline ends to corresponding ikh joints
            setup reverse feet rig
            create controller
            fill compound array for controllers
            add controller functionality
            create controller hierarchy
            add feet attributes
            lock groups and controller attributes through controller array
            > lock: all ctrls scale, FK translate, PV + spine b/c rotate
        Vars:
            spine_jnts - array of IK handle joints (ikh) to bind to IK spline
        Result: 
            ready to use control rig
        '''

        def ctrl_creation(*args):
            # create ik control rig
            pm.currentUnit(linear="cm")

            # reset arrays
            ik_jnts_check.clear()
            basic_ctrl_grp.clear()
            null_grp.clear()
            full_ctrl_grp.clear()

            create_control_rig()

            # individual ik solver for limbs
            create_ik(ik_jnts_check[47], "rp")
            create_ik(ik_jnts_check[48], "sc")
            create_ik(ik_jnts_check[49], "sc")

            create_ik(ik_jnts_check[52], "rp")
            create_ik(ik_jnts_check[53], "sc")
            create_ik(ik_jnts_check[54], "sc")

            create_ik(ik_jnts_check[10], "rp")
            create_ik(ik_jnts_check[29], "rp")

            # PVs for arms/legs
            setupPV(ik_jnts_check[9], "hdl_" + names[15], [0, 0, 35])
            setupPV(ik_jnts_check[28], "hdl_" + names[41], [0, 0, 35])
            setupPV(ik_jnts_check[46], "hdl_" + names[9], [0, 35, 0])
            setupPV(ik_jnts_check[51], "hdl_" + names[35], [0, -35, 0])

            print("!!! Operation: IK Limb Setup successful.")

            connect_rig()

            # ikSplineHandle - auto-create curve (default), adjusted twist Type for more realistic movement
            pm.ikHandle(name="hdl_c_spine", solver="ikSplineSolver", twistType="easeIn",
                        startJoint=ik_jnts_check[1], endEffector=ik_jnts_check[4])

            # rename curve, parent curve and handle to grp_rig_system
            spine_crv = pm.listRelatives(ik_jnts_check[0], allDescendents=True)[-1]
            pm.rename(spine_crv, "crv_c_spine")
            pm.parent(spine_crv, "hdl_c_spine", "grp_rig_system")

            # create, position ikh joints and bind spline to it
            spine_jnts = ["ikh_c_hips", "ikh_c_spine_b", "ikh_c_spine_c", "ikh_c_chest"]

            for spine_jnt in spine_jnts:
                non_object_check(spine_jnt)
                pm.select(clear=True)
                pm.joint(name=spine_jnt)

            pm.delete(pm.parentConstraint(ik_jnts_check[1], spine_jnts[0]))
            pm.delete(pm.parentConstraint(ik_jnts_check[2], spine_jnts[1]))
            pm.delete(pm.parentConstraint(ik_jnts_check[3], spine_jnts[2]))
            pm.delete(pm.parentConstraint(ik_jnts_check[4], spine_jnts[3]))
            pm.skinCluster(spine_jnts[0], spine_jnts[1], spine_jnts[2], spine_jnts[3], "crv_c_spine",
                           maximumInfluences=3)

            pm.parent(spine_jnts[0:4], "grp_rig_system")

            # when root ctrl gets added, spine would move with root and inheritance (meaning x2 transformation)
            # Setup Advanced Twist Controls to give ability to rotate spine around itself
            ikc = pm.PyNode("hdl_c_spine")
            ikc.inheritsTransform.set(0)
            ikc.dTwistControlEnable.set(1)
            ikc.dWorldUpType.set(4)  # objectRotationUp(start/end)
            ikc.dForwardAxis.set(0)  # +x
            ikc.dWorldUpAxis.set(0)  # +y - goes for base (hip) joint

            # can't connect through variable, needs to be called by string
            pm.connectAttr("ikh_c_hips.worldMatrix[0]", "hdl_c_spine.dWorldUpMatrix", force=True)
            pm.connectAttr("ikh_c_chest.worldMatrix[0]", "hdl_c_spine.dWorldUpMatrixEnd", force=True)

            print("!!! Operation: IK Spine Setup successful.")

            reverseFoot()

            lock_attr("grp_rig_system", [1, 1, 1], 1, 1)

            # create visual controls
            nurbs_controller()

            # create array for ctrls
            for ngc in null_grp:
                full_ctrl_grp.append(ngc.getChildren())

            ctrl_functionality()

            ctrl_hierarchy()

            addFeetAttr("ctrl_l_foot", "l")
            addFeetAttr("ctrl_r_foot", "r")

            pm.hide("grp_ik_rig", "grp_rig_system")

            # lock groups and controls
            # groups
            for null_l in null_grp:
                lock_attr(null_l, [1, 1, 1], 1, 1)

            # all controls scale
            for ctrl_l in full_ctrl_grp:
                for clock in ctrl_l:
                    lock_attr(clock, [0, 0, 1], 1, 1)
            # FK
            for rot_ctrl_l in full_ctrl_grp[5:7] + full_ctrl_grp[9:41]:
                for rclock in rot_ctrl_l:
                    lock_attr(rclock, [1, 0, 1], 1, 1)

            # PV und Spine
            for pos_ctrl_l in full_ctrl_grp[43:47] + full_ctrl_grp[2:4]:
                for pclock in pos_ctrl_l:
                    lock_attr(pclock, [0, 1, 1], 1, 1)

            print("!!! Operation: Controller Lock successful.")

            pm.select(clear=True)

        '''
        Function:
            reset progress to locator stage
            clear arrays for joints and controllers
            delete groups in outliner
            show grp_loc_rig
        '''

        def reset_locs(*args):
            # wipe all global lists since joint creation
            jnts.clear()
            basic_ctrl_grp.clear()
            null_grp.clear()
            full_ctrl_grp.clear()

            # enable locator buttons
            pm.button("b_l_mirror", edit=True, enable=True)
            pm.button("b_r_mirror", edit=True, enable=True)

            # delete joint and control groups
            pm.showHidden("grp_loc_rig")
            if pm.objExists("grp_bind_rig"):
                pm.delete("grp_bind_rig")
            if pm.objExists("grp_control_rig"):
                pm.delete("grp_control_rig")

            print("!!! Operation: Reset to Locator successful.")

        '''
        Function:
            reset progress to joint stage
            clear arrays for controllers
            delete grp_control_rig in outliner
            show grp_bind_rig
        '''

        def reset_jnts(*args):
            # wipe all global lists since joint creation
            basic_ctrl_grp.clear()
            null_grp.clear()
            full_ctrl_grp.clear()

            # delete joint and control groups
            pm.showHidden("grp_bind_rig")
            if pm.objExists("grp_control_rig"):
                pm.delete("grp_control_rig")

            # zero out joints aferwards
            jnt_names = names[0:31] + names[33:57]
            for zero_jnt in jnt_names:
                pm.xform("jnt_" + zero_jnt, objectSpace=True, rotation=[0, 0, 0])
            pm.xform("jnt_" + names[0], translation=og_root_pos[0], absolute=True)
            pm.xform("jnt_" + names[1], translation=og_root_pos[1], absolute=True)
            print("!!! Operation: Reset to Skeleton successful.")

        '''
        Function:
            select all visible objects in viewport
            toggle local rotation axis
        '''

        def toggleTransforms(*args):
            pm.select(all=True, hierarchy=True, visible=True)
            pm.toggle(localAxis=True)
            pm.select(clear=True)

        '''
        Transfer Vars:
            bone - root bone of hierarchy (skinRoot)
            mesh - to be bound mesh (skinMesh)
        Input Vars:
            sR - text from textfield
            sM - text from textfield
            check_sR - validate sR
            check_sM - validate sM
        Function: 
            see, if texts are correlating to an object in the scene with the same name, otherwise invalidate input
            if input valid, skin the correlating mesh to the correlating joint hierarchy
        Result: 
            skinCluster on root bone and Mesh
        '''

        def skinning(bone, mesh, *args):
            sR = pm.textField(bone, query=True, text=True)
            sM = pm.textField(mesh, query=True, text=True)
            check_sR = True
            check_sM = True
            try:
                pm.select(sR, replace=True)
            except TypeError:
                print(f"!!! TYPE ERROR: Transform '{sR}' does not exist")
                pm.select(clear=True)
                check_sR = False

            try:
                pm.select(sM, add=True)
            except TypeError:
                print(f"!!! TYPE ERROR: Geometry '{sM}' does not exist")
                pm.select(clear=True)
                check_sM = False

            if check_sR and check_sM:
                try:
                    pm.skinCluster(bindMethod=1, skinMethod=1, normalizeWeights=1, weightDistribution=1,
                                   maximumInfluences=5, obeyMaxInfluences=True, dropoffRate=4,
                                   removeUnusedInfluence=True)
                    print(f"!!! OPERATION: Objects '{sR}' and '{sM}' were successfully connected through a skinCluster")
                except RuntimeError:
                    print(f"!!! RUNTIME ERROR: Geometry '{sM}' is already connected to a skinCluster")

        '''
        Transfer Vars:
            mesh - to be unbound mesh (skinMesh)
        Input Vars:
            bM - text from textfield
        Function: 
            unbind skin from mesh
            raise error when mesh name doesn't exist or mesh is not connected to skinCluster
        Result: 
            skinCluster on root bone and Mesh
        '''

        # Transfer Variable: b_mesh - bound Mesh to be unbound
        def unbindSkin(b_mesh, *args):
            bM = pm.textField(b_mesh, query=True, text=True)
            try:
                pm.select(bM, replace=True)
                pm.skinCluster(edit=True, unbind=True)
                print(f"!!! OPERATION: SkinCluster from geometry '{bM}' was removed successfully")
            except TypeError:
                pm.select(clear=True)
                print(f"!!! TYPE ERROR: Geometry '{bM}' does not exist")
            except RuntimeError:
                pm.select(clear=True)
                print(f"!!! RUNTIME ERROR: Geometry '{bM}' is not connected to a skinCluster")

        '''
        Function:
            "About" window
            window and text for tool and author descriptions
            - what this tool is and what it is made with
            - project and redistribution
            - author, update, version
        Var:
            about_win - about GUI window
        '''

        def aboutUI(*args):
            print("--------------------------")
            if cmds.window("sk_about", exists=True):
                cmds.deleteUI("sk_about")
            about_win = cmds.window("sk_about", title="Function Help")

            cmds.columnLayout(adjustableColumn=True, columnAlign="left", columnAttach=["both", 7], enable=True,
                              columnOffset=["left", 20])

            cmds.separator(style="none", height=15)

            cmds.text(
                label="This plug-in tool is designed to help rig a bipedal creature for\ngame animation purposes inside Autedesk Maya 2023+. It operates\nwith PyMel and the Maya Python API 1.0.")
            cmds.separator(style="none", height=12)
            cmds.text(
                label="This program was built within a bachelors project. As this plug-in\nhandles itself as a custom script for Autodesk Maya, it is marked\nas free softwar: You can redistribute and/or modify it.")
            cmds.text(
                label="This program is distributed in the hope that it will be useful,\nbut without any warranty.")

            cmds.separator(style="none", height=12)
            cmds.text(label="Author: Suzanne Knoop")
            cmds.text(label="E-Mail: suzanne.tamara@gmail.com")
            cmds.text(label="Last Update: 01/29/2024")
            cmds.text(label="Version: 0.0.2")
            cmds.separator(style="none", height=15)

            cmds.text(label="Known Issues:", font="boldLabelFont")
            cmds.text(label="* 'Reset to Skeleton' doesn't reset the hip translation attributes\n   after restart")
            cmds.separator(style="none", height=17)

            cmds.showWindow(about_win)

        '''
        Function:
            "Help" window
            window and text for individual function descriptions
            - detailed descriptions on what each button and input does
        Vars:
            help_win - help GUI window
        '''

        def helpUI(*args):
            print("--------------------------")
            if cmds.window("sk_help", exists=True):
                cmds.deleteUI("sk_help")
            help_win = cmds.window("sk_help", title="Function Help")

            cmds.columnLayout(adjustableColumn=True, columnAlign="left", columnAttach=["both", 5], enable=True,
                              columnOffset=["left", 20])
            # header
            cmds.separator(style="none", height=5)
            cmds.text(label="Functions Rundown", font="boldLabelFont", height=20)
            # locators
            pm.separator(style="in", height=10)
            cmds.text(label="Pose Dropdown Menu:", font="boldLabelFont")
            pose_txt = cmds.text(
                label="Preset for the to be created locators.\nA-Pose is adjusted to the UE5 Male Mannequin.")
            pm.separator(style="none", height=10)
            cmds.text(label="Hierarchy Dropdown Menu:", font="boldLabelFont")
            hierarchy_txt = cmds.text(
                label="Acts as preset and interactive function.\n'Locators in Hierarchy' puts locators in hierachial order.\n'Locators Solo' sets locators as unrelated objects.")
            cmds.separator(style="none", height=10)
            cmds.text(label="Create Locators Button:", font="boldLabelFont")
            loc_txt = cmds.text(
                label="Creates Locators with given presets.\nLocators follow a bipedal structure.\nThe structure is aimed to be optimized for game development.")
            cmds.separator(style="none", height=10)
            cmds.text(label="Mirror Buttons:", font="boldLabelFont")
            miror_txt = cmds.text(
                label="Mirrors locator translation and rotation to the other side.\nEvery locator from one side will be mirrored to the other.\nThey can be mirrored from left and right, respectively.")
            # middle part
            pm.separator(style="single", height=15)
            cmds.text(label="Create Skeleton Button:", font="boldLabelFont")
            skel_txt = cmds.text(
                label="Creates a joint hierarchy based on the preexisting locator positions.\n* Basic XYZ orientations with mostly mirrored behaviour\n* Thumb X rotations usually need to be adjusted")
            cmds.separator(style="none", height=10)
            cmds.text(label="Create IK Controls Button:", font="boldLabelFont")
            ctrls_txt = cmds.text(
                label="Creates a separate, to be manipuleted IK joint skeleton.\nCreates respective spine, arm and leg IK controller.\n* Additional FK controls for neck, head and fingers\n* Tip, ball and heel attributes for foot controls\n* Advanced twist controls, adjust if spine is twisted")
            cmds.separator(style="none", height=10)
            cmds.text(label="Local Rotation Axes Toggle:", font="boldLabelFont")
            lra_txt = cmds.text(label="Toggles the Local Rotation Axes display on all visible objects.")
            cmds.separator(style="none", height=10)
            cmds.text(label="Reset to Locators Button:", font="boldLabelFont")
            reset_loc_txt = cmds.text(
                label="Deletes everything the tool created, except the locator group.\n*Locator positions won't reset.")
            cmds.separator(style="none", height=10)
            cmds.text(label="Reset to Skeleton Button:", font="boldLabelFont")
            reset_loc_txt = cmds.text(
                label="Deletes the controls unter grp_control_rig, returning to the base skeleton.\n*Any animations and controller movements will be reversed.")
            # skinning
            cmds.separator(style="single", height=10)
            cmds.separator(style="single", height=10)
            cmds.text(label="Root Bone Textfield:", font="boldLabelFont")
            root_txt = cmds.text(label="Field to write the name of the first joint of the to be bound hierarchy.")
            cmds.separator(style="none", height=10)
            cmds.text(label="Mesh Textfield:", font="boldLabelFont")
            mesh_txt = cmds.text(label="Field to write the name of the to be skinned mesh.")
            cmds.separator(style="none", height=10)
            cmds.text(label="Bind Skin Button:", font="boldLabelFont")
            skin_txt = cmds.text(
                label="Skin mesh to hierarchy from the texfields.\n*Bind Method - Closest in Hierarchy\n*Skinning Method - Dual-Quaternion\n*Max Influences - 5")
            cmds.separator(style="none", height=10)
            cmds.text(label="Unbind Skin Button:", font="boldLabelFont")
            unbind_txt = cmds.text(
                label="Deletes the skinCluster of the written mesh.\n*Also deletes the skin wheights.")
            cmds.separator(style="none", height=10)

            cmds.showWindow(help_win)

        '''
        Function:
            window, buttons, descriptive texts, text fields, separators
            command separation according to GUI rows
        Vars: 
            sk_win - GUI window
            sk_art - SuzanneKnoop_Auto_Rigging_Toolkit
            skinRoot - to be selected joint hierarchy from text
            skinMesh - to be selected mesh from text
        Result:
            create functional GUI upon execution
        '''

        def artUI():
            print("--------------------------")
            if cmds.window("sk_art", exists=True):
                cmds.deleteUI("sk_art")
            sk_win = cmds.window("sk_art", title="Bipedal Rigging Tool", menuBar=True)
            pm.rowColumnLayout(numberOfColumns=2, columnSpacing=[(1, 1), (2, 7)],
                               columnOffset=[(1, "both", 22), (2, "left", 22)], columnWidth=[(1, 100), (2, 200)],
                               rowSpacing=(1, 22), columnAlign=[(1, "left"), (2, "left")])

            # help menu
            pm.menu("help_menu", label="Help", helpMenu=True, enable=True)
            pm.menuItem("about_item", label="About", command=aboutUI)
            pm.menuItem("func_item", label="Function Overview", command=helpUI)

            # Locator section
            pm.text(label="    < 1. Locator >    ", enable=True, width=200)
            pm.separator(style="single", height=2, width=160)

            # pose and hierarchy
            pm.optionMenu("pose_option", backgroundColor=[0.22, 0.22, 0.22], width=100, height=23)
            pm.menuItem(label="A-Pose")
            pm.menuItem(label="T-Pose")

            pm.optionMenu("hierarchy_option", changeCommand=loc_solo_hierarchy_button, width=157, height=23)
            pm.menuItem(label="Move as Hierarchy")
            pm.menuItem(label="Move as Solo")

            # locators
            pm.button("bt_locs", label="Create Locators", width=100, height=30, enable=True,
                      command=partial(create_locator_hierarchy), backgroundColor=[0.45, 0.45, 0.45],
                      annotation="Create a Locator Hierarchy which can be customized upon creation, to fit the desired skeletal Proportion")
            pm.text(label=" Place where your joints are", enable=False)

            # mirror
            cmds.button("b_l_mirror", label="Mirror L > R", width=100, height=30, enable=True,
                        command=partial(loc_mirror, "l"))
            cmds.button("b_r_mirror", label="Mirror R > L", width=103, height=30, enable=True,
                        command=partial(loc_mirror, "r"))

            # Skeleton section
            pm.text(label="    < 2. Skeleton >    ", enable=True, width=200)
            pm.separator(style="single", height=1, width=160)

            # skeleton
            pm.button("bt_bones", label="Create Skeleton", width=100, height=30, enable=True,
                      command=create_joint_hierarchy, backgroundColor=[0.45, 0.45, 0.45],
                      annotation="Create a Joint Hierarchy according to the Locator Positions with basic XYZ Joint Orientations, WITHOUT single corrections")
            pm.text(label=" Check orientations afterwards", enable=False)

            # controls
            pm.button("bt_ctrls", label="Create IK Controls", enable=True, command=ctrl_creation, width=100,
                      height=30, backgroundColor=[0.45, 0.45, 0.45],
                      annotation="Create IK Controls for Arms/Fingers, Legs/Feet, Head and Spine (IK Spline)")
            pm.separator(style="none", height=2)

            # toggle
            pm.checkBox(label=" Toggle Local Rotation Axes", changeCommand=toggleTransforms, width=200,
                        annotation="Toggles the 'Display Local Rotation Axes'-control on all visible objects")
            pm.text(label="")

            # resets
            pm.button("bt_resetLocs", label="Reset to Locators", enable=True, command=reset_locs, width=100, height=30,
                      backgroundColor=[0.4, 0.3, 0.3],
                      annotation="Deletes everything the tool created, except the Locator Hierarchy to make further placement adjustments")
            pm.text(label="Delete Joint Hierarchy", enable=False)

            pm.button("bt_resetJnts", label="Reset to Skeleton", enable=True, command=reset_jnts, width=100, height=30,
                      backgroundColor=[0.4, 0.3, 0.3],
                      annotation="Deletes the Control Rig to make furthere adjustments to the base skeleton")
            pm.text(label="Delete Control Rig", enable=False)

            pm.separator(style="none", height=1)
            pm.separator(style="none", height=1)

            # Skinning
            pm.text(label="    < Skinning >    ", enable=True, width=200)
            pm.separator(style="single", height=2, width=160)

            # text fields
            pm.text(label="Root Bone", annotation="Name of the First Joint in the to be bound Joint Hierarchy")
            skinRoot = cmds.textField(placeholderText="Name of First Bone", width=160)

            pm.text(label="Mesh", annotation="Name of the Mesh that will be skinned to the Joint Hierarchy above")
            skinMesh = cmds.textField(placeholderText="Mesh Name", width=160)

            # (unbind) skin
            pm.button("bt_skin", label="Bind Skin", width=100, height=30, enable=True,
                      command=partial(skinning, skinRoot, skinMesh), backgroundColor=[0.45, 0.45, 0.45],
                      annotation="Bind to: Joint Hierarchy, Bind Method: Closest in Hierarchy, Skinning Method: Dual-Quaternion")
            pm.text(label=" Wheight Paint afterwards", enable=False)

            pm.button("bt_unbindSkin", label="Unbind Skin", enable=True, width=100, height=30,
                      command=partial(unbindSkin, skinMesh), backgroundColor=[0.4, 0.3, 0.3],
                      annotation="Unbinds the Skinning of the 2 named objects above")
            pm.text(label="Reset Skinning", enable=False)

            pm.separator(style="none", height=5)
            pm.showWindow(sk_win)

        # execute upon executing cmds.sk_biped_RiggingTool()
        artUI()

# Plug-in Components
# class instance Pointer
def cmdCreator():
    return omx.asMPxPtr(SK_RT())


# initialize the script plug-in
def initializePlugin(mobject):
    pluginFn = omx.MFnPlugin(mobject)
    try:
        pluginFn.registerCommand(kPluginCmdName, SK_RT)
    except:
        sys.stderr.write("Failed to register command: " + kPluginCmdName)


# uninitialize the script plug-in
def uninitializePlugin(mobject):
    pluginFn = omx.MFnPlugin(mobject)
    try:
        pluginFn.deregisterCommand(kPluginCmdName)
    except:
        sys.stderr.write("Failed to unregister command: " + kPluginCmdName)

