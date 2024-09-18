# EasyRig_BipedAutoRiggingTool
Free auto rigging script for Maya 2023 using PyMel

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

***Installation Guides***

Plugin Verison:
---------------------------------------------------------------------
Installation methods:
1) Through Maya GUI - Windows > Settings/Preferences > Plug-in Manager > Browse > your filepath > load
2) Through Python Script Editor - cmds.loadPlugin("your filepath")
Loading will take a bit as it imports PyMel core.

Execution code:
cmds.sk_biped_EasyRig()
---------------------------------------------------------------------
Script Version:

Copy paste the script into the Python Script Editor and excecute Code
