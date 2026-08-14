Open Rails Shape File Manager Version 2.5 - Legacy Help

** This utility is intended to help Open Rails model builders manage shape files. Use
of this tool by someone unfamiliar with the file management requirements of Open Rails may
result in routes being unable to load. **

The main form behaves much like the Windows Explorer - the left side shows the
current folder with a button to navigate up one level to the parent.

Below the current folders is a list of sub-folders. Selecting one of these makes
it the current folder.  The Buttons across the top allow navigating to another drive.

On the right side is a list of shape files contained in the folder including size and
compression information.  The default is to display a maximum of 600 shape file names.
The file list is limited because on some systems and under some conditions SFM25 will
display an error message if there are too many shape files in a folder. This limit can
be disabled in the SFM25 "Settings" dialog. In any case, it is better to run SFM25 on
shape files in a working folder and not directly on a route installation. 

Click on the "Options" button to the right of the shape file name to display the menu of
options (actions) that are available for the highlighted target file.


Options for COMPRESSED files:

Uncompress - Call FFEDITC_UNICODE.EXE to uncompress the shape file - may not work on
locomotives with animations unless you have the patched NEWSHAPE.BNF file on your system.

Edit .SD File - Edit the .SD file with the configured Unicode editor. If the .SD file does
not exist it will be created.


Options for UNCOMPRESSED files:

Compress - Call FFEDITC_UNICODE.EXE to compress the shape file - may not work on
locomotives with animations unless you have the patched NEWSHAPE.BSF file on your system.

Distance Levels - Allows changes to the shapes distance levels of detail. Reducing values
here help to improve frame rates by not loading the shape at distances over the values
entered (where there is only one level). Basically the maximum viewable distance should be
proportional to the object size. A backup of the shape file is made with a ".PreDistance"
file extension.

MIP Map Levels - Allows changes to the shapes MIP Map levels for textures. Reducing values
here may help to improve the appearance of textures and decrease "blurriness" at the
expense of increased aliasing and moire. A backup of the shape file is made with a
".PreTexture" file extension.

Reverse - Reverse an object (rotate 180 degrees about the Y axis) by altering the
vol_sphere, points, vectors, sort_vectors, matrices and animations sections of the file.
Backups of the .S and .SD files are made with a ".PreReverse" file extension.

Rotate CCW - Rotate an object 90 degrees counterclockwise about the Y axis (looking down)
by altering the vol_sphere, points, vectors, sort_vectors, matrices and animations
sections of the file. Backups of the .S and .SD files are made with a ".PreRotate" file
extension.

Rotate CW - Rotate an object 90 degrees clockwise about the Y axis(looking down). Backups
of the .S and .SD files are made with a ".PreRotate" file extension.

Scale - Resize an object by altering the vol_sphere, points, vectors, sort_vectors,
matrices and animations sections of the file. Backups of the .S and .SD files are made with
a ".PreScale" file extension.

Shift - Adjust an objects position relative to its origin (pivot point). The 3 prompts
are for the distance moved in metres i.e. 0.05 = 5cm  - positive Y values are up. Backups
of the .S and .SD files are made with a  ".PreShift" file extension.

Texture Mode - Allows the user to change the texture mode of the matrices (groups) of
objects in a shape file. This option also applies the specular highlight fix for shiny
textures. Unless the matrices have been well named, this process can be a bit hit and
miss. Backups of the .S and .SD files are made with a ".PreTexture" file extension.

Edit .S File - Edit the .S file with the configured Unicode editor.

Edit .SD File - Edit the .SD file with the configured Unicode editor. If the .SD file does
not exist it will be created.

Note: If a shape data (.SD) file exists, it will be automatically adjusted as part of the
Reverse, Rotate, Scale and Shift options.


SETTINGS:

The following SFM25 options can be configured in the "Settings" dialog:

     FFEDITC_UNICODE.EXE: Enter the full path to FFEDITC_UNICODE.EXE (with or without
                          the trailing backslash). If no path for FFEDITC_UNICODE.EXE
                          has been configured, SFM25 will try and locate it in the
                          SFM25 folder or the installation folder for Open Rails.  

          Unicode Editor: By default, SFM25 will use WORDPAD.EXE to edit Unicode files.
                          The user can configure an alternate Unicode editor by entering
                          the fully qualified pathname. The path name is not required if
                          the alternate Unicode editor is on the user's PATH.
                          
  Confirm ALL Operations: By default, SFM25 will ask for confirmation before performing
                          any operation. If this option is "unchecked", SFM25 will
                          immediately COMPRESS, UNCOMPRESS, REVERSE or ROTATE a shape
                          file without confirmation. Disabling confirmation may speed up
                          multiple operations but increases the risk of a mistake. 

         Limit File List: By default, SFM25 will limit the file list to a maximum of 600
                          names.  If this option is "unchecked", SFM25 will not limit the
                          file list. Disabling "Limit File List" may result in very slow
                          execution and warning or error messages. Your computer may
                          become unresponsive or crash completely. It is better to run
                          SFM25 on shape files in a working folder and not directly on a
                          route installation.


CAUTIONS:
========

Shape File Manager is a simple program designed to make relatively simple changes to Open Rails
shape files.  It is NOT a substitute for dedicated 3D modeling software.

Shape files are very complicated entities and may be corrupted and rendered unusable by
SFM25. Although SFM25 will normally function properly on "simple" shape files; complicated
shape files, especially those involving animation, may cause it to fail.  Some shape files
have defective or incomplete animation specifications and will not ROTATE or REVERSE
correctly.

SFM25 must recalculate the surface normals when scaling a shape file using different scale
factors for X, Y and Z.  This may introduce errors into the shape file that will cause it
to display incorrectly.  Shape files with animations, particularly rolling stock, are
especially susceptible to this problem.

The user is cautioned to ALWAYS make secure backups. 