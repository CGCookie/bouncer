# Blender Market Bouncer

This repository contains a Blender Add-on for doing basic automated testing of Blender Market product submissions.

Note: success across all of these tests does not mean the product is ready to be accepted on the Blender Market, nor does failure in any test mean it must be rejected.
These tests only help facilitate the product reviewers in their workflow.

## Installing and Running

To run,

1. Install as regular Blender Add-on
2. Open the .blend file needing to be tested
3. Click the button in the top bar with the Python script icon.  It will be just to the left of the Blender logo button.
4. A new Blender window with text editor will appear.
5. The results of running Bouncer against the open .blend file will be shown in the editor.


## Understanding the results

To read and understand the results,

1. The first column shows test success or failure.
    - `XXX` indicates failure
    - ` + ` indicates success
2. The second column show which test was performed.
3. the third column will contain either
    - `...(nothing found)...` if no data was found that failed the test, or
    - a list of data that caused test failure

Here are the tests performed:

- unpacked images: checks that each image is either packed or exists as external file
- orphaned images: checks for orphaned images (an image with no user)
- missing libraries: checks that all linked libraries exist
- object names: checks `bpy.data.objects` for avoided names (standard Blender names, duplicates, etc.---should have a unique, descriptive name) or misspellings
- material names: checks `bpy.data.materials` for avoided names or misspellings
- single image BSDF: checks for special case where Principled BSDF Node has exactly one image input (generally, this means the node set up can be improved)

