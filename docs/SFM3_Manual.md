# Open Rails Shape File Manager 3.0.2 User Manual

Distribution kit manual for SFM3

## 1. Overview

Open Rails Shape File Manager 3.0.2, also called SFM3, is a Windows desktop utility for working with Open Rails shape files.

SFM3 is a Python/Tkinter continuation of the older SFM25 HTA utility. Version 3.0.2 replaces the obsolete HTA, ActiveX, and FFEDITC_UNICODE workflow with a normal desktop application and an ORZIP backend for shape-file compression and uncompression.

The application is intended for local/offline work on Open Rails `.S` shape files and their related `.SD` shape data files. It is a convenience tool for model builders who already understand the Open Rails file layout; it is not a replacement for a dedicated 3D modelling program.

## 2. Distribution kit contents

A typical SFM3 distribution kit contains:

- `SFM3.exe` - the packaged Windows application.
- `orzip.exe` - ORZIP helper executable when distributed beside the application, or bundled into the packaged EXE build.
- `README.md` - project overview and build notes.
- `LICENSE.md` - Creative Commons Attribution-ShareAlike 4.0 International licence definition.
- `SFM3.ico` - application icon, either embedded in the EXE or present in the source `assets` folder.
- `SFM3_Manual.pdf` - this user manual.

Source distributions may also contain:

- `SFM30.py` - Python/Tkinter source application.
- `Run_SFM3.bat` - source launcher.
- `build_exe.bat` - PyInstaller build script.
- `build_manual.bat` - PDF manual build script.
- `SFM3.spec` - PyInstaller build specification.
- `assets/SFM3.ico` - icon file used by the source app and packaged EXE.
- `tools/build_icon.py` - script used to regenerate the application icon artwork.
- `docs/SFM3_Manual.md` - Markdown source for this manual.
- `sfm25.help.md` - historical SFM25 help text used as a reference while documenting SFM3.

## 3. System requirements

For the packaged executable:

- Windows.
- No separate Python installation is required.
- ORZIP is bundled into the single-file EXE build, and the ORZIP command remains configurable from Settings.

For running from source:

- Windows.
- Python 3.11 or newer recommended.
- Tkinter, included with most standard Python for Windows installations.
- ORZIP available either as `orzip.exe` in the application folder or on `PATH`.

## 4. Recommended working practice

Shape files are important route and rolling-stock assets. A damaged shape file can prevent an object, consist, activity, or route tile from loading correctly.

Use this workflow:

- Work on copies in a temporary working folder, not directly inside a route, trainset, or production installation.
- Keep a separate secure backup of the original model before using geometry-changing operations.
- Check the result in Shape Viewer or Open Rails before replacing a working asset.
- Be especially cautious with complex animated stock, locomotives, and files that already have unusual or incomplete animation data.
- Leave confirmation prompts enabled unless you are deliberately processing known-good copies.

SFM3 creates operation-specific `.Pre...` backups, but those backups are not a substitute for your own project backup.

## 5. Starting SFM3

### Packaged distribution

Double-click `SFM3.exe`.

### Source distribution

Double-click `Run_SFM3.bat`, or run this command from the project folder:

```bat
python SFM30.py
```

## 6. Main window

The SFM3 main window is divided into navigation and file-management areas.

The left side behaves much like a simple Windows Explorer folder browser:

- The drive buttons select available Windows drives.
- The Current Directory area shows the active folder.
- The Up One Folder button moves to the folder that contains the current folder.
- The Sub Directories list lets you browse into child folders.

The right side lists `.S` shape files in the current directory. The list shows:

- File name.
- Relative folder, shown as `.` for files in the current folder.
- File size.
- Detected status: Compressed, Uncompressed, or Unknown Format.

The Search Shape Files box filters by partial filename. For example, entering `bridge` shows `.S` files whose names contain `bridge`. Include Subfolders is enabled by default, so a non-empty search extends below the current folder and recursive results show the relative folder for each match. Turn Include Subfolders off to search only the current folder. The Clear button removes the filter and returns to the normal current-folder file list.

The Shape Files list has a vertical scrollbar on its left edge so it remains reachable when the window is narrow.

Double-click or right-click a `.S` shape file to open the action menu for that file. The available actions depend on the detected file status.

By default, SFM3 displays up to 600 shape files in one folder. This keeps navigation responsive in very large folders. The limit can be disabled in Settings, but it is usually better to copy the files you intend to work on into a smaller working folder.

## 7. Shape file status

SFM3 classifies shape files as:

- Compressed - a compressed Open Rails shape file that must be uncompressed before direct text/geometry editing.
- Uncompressed - a text/Unicode shape file that SFM3 can edit directly.
- Unknown Format - a file that SFM3 cannot confidently classify.

The status is used only to decide which menu actions are safe to offer. If a file appears as Unknown Format, do not force geometry operations on it; check that it is really an Open Rails `.S` file and that it is not damaged.

## 8. Actions for compressed files

For compressed `.S` files, SFM3 can:

- Uncompress the shape file using ORZIP, if ORZIP is configured or found.
- Edit or create the related `.SD` file.

Uncompression is required before SFM3 can perform direct distance-level, MIP-map, texture-mode, and geometry operations.

SFM25 used `FFEDITC_UNICODE.EXE` for this step. SFM3 uses ORZIP instead, so the FFEDITC/ActiveX workflow is no longer required.

## 9. Actions for uncompressed files

For uncompressed `.S` files, SFM3 can:

- Compress the shape file using ORZIP.
- Edit Distance Levels.
- Edit MIP Map Levels.
- Reverse geometry.
- Rotate geometry 90 degrees counter-clockwise.
- Rotate geometry 90 degrees clockwise.
- Scale geometry.
- Shift geometry.
- Edit Texture Modes.
- Edit the `.S` file with the configured Unicode editor.
- Edit or create the related `.SD` file.

Most editing operations modify text/Unicode shape files directly. When you need to return the shape to a compressed form for distribution or simulator use, use Compress after checking the edited file.

## 10. Distance Levels

Distance Levels lets you review and change `DLEVEL_SELECTION` values found in an uncompressed shape file.

The dialog lists each detected distance level with its associated polygon count. Enter the desired distance value and press OK to apply the update.

Reducing distance values can improve frame rate by preventing a shape from being loaded or drawn at excessive distances. The maximum useful distance is usually related to the size and importance of the object. Small scenery details normally do not need to remain visible as far away as large buildings, bridges, or landmark structures.

Before writing changes, SFM3 creates a backup with the suffix `.PreDistance`.

## 11. MIP Map Levels

MIP Map Levels lets you change detected texture MIP settings.

Available choices are:

- MIP 0
- MIP-1
- MIP-2
- MIP-3

Changing MIP map levels may improve the appearance of some textures and reduce apparent blurriness. Lowering MIP levels can also increase aliasing or moire effects, so check the shape in the simulator or a viewer after changing this setting.

Before writing changes, SFM3 creates a backup with the suffix `.PreMIPlevel`.

## 12. Texture Modes

Texture Modes lets you change detected vertex-state texture rendering modes.

Available choices are:

- Normal
- DarkShd
- HalfBrt
- LoShine
- HiShine
- CrcForm
- Bright

This option is useful for adjusting how grouped parts of the shape are rendered. The dialog labels entries from matrix names when those names are available. If the original matrices were not named clearly, choosing the right entry can require trial and error.

Texture Mode also applies the same specular-highlight style adjustment used by the older SFM workflow for shiny textures.

Before writing changes, SFM3 creates a backup with the suffix `.PreTexture`.

## 13. Geometry operations

Geometry operations alter shape coordinates and related values in the text shape file. When a matching `.SD` file exists, SFM3 also adjusts supported shape-data bounding values for Reverse, Rotate, Scale, and Shift.

### Reverse

Reverse turns an object 180 degrees about the vertical Y axis by adjusting supported points, vectors, sort vectors, matrices, and animation key values.

Backup suffix: `.PreReverse`.

### Rotate 90 degrees

Rotate 90 degrees counter-clockwise and Rotate 90 degrees clockwise rotate supported point, vector, sphere, matrix, and animation key values about the vertical Y axis when viewed from above.

Backup suffix: `.PreRotate`.

### Scale

Scale changes shape dimensions. You may scale all directions equally or provide separate X, Y, and Z scale factors.

SFM3 uses the Open Rails shape coordinate convention in its prompts:

- X - width.
- Y - height.
- Z - length.

Scale factors must be positive nonzero numbers. For example, `2` doubles a dimension and `0.5` halves it.

Non-uniform scaling can require recalculated surface normals. This can introduce visual errors in some shape files, especially animated rolling stock or files with unusual geometry. Check the result carefully.

Backup suffix: `.PreScale`.

### Shift

Shift moves supported shape coordinates relative to the model origin or pivot point.

SFM3 prompts for movement in metres:

- Shift X - width direction.
- Shift Y - height direction.
- Shift Z - length direction.

For example, `0.05` moves a value by five centimetres. Positive Y values move upward.

Backup suffix: `.PreShift`.

## 14. Editing `.S` and `.SD` files

SFM3 opens `.S` and `.SD` files with the configured Unicode editor. The default editor is `notepad.exe`.

When editing `.SD` files, SFM3 looks for the related `.SD` file by appending `d` to the `.S` file path. For example, `example.s` uses `example.sd`.

If the `.SD` file does not exist, SFM3 can create a basic `.SD` file and then open it in the editor.

Manual editing is powerful but risky. Preserve the Unicode/text structure of the file and keep backups before making manual changes.

## 15. Backups and safety

Shape files are complex. Work on copies and keep secure backups of original models before modifying them.

SFM3 creates operation-specific backup files before geometry-changing and index-changing operations:

- `.PreScale`
- `.PreShift`
- `.PreReverse`
- `.PreRotate`
- `.PreDistance`
- `.PreTexture`
- `.PreMIPlevel`

These backups are created beside the original shape file. Related `.SD` files may also receive matching backup suffixes when the operation adjusts shape-data values.

Important cautions:

- SFM3 is designed for relatively simple changes to Open Rails shape files.
- Very complex shapes, animated shapes, and defective or incomplete animation definitions may not transform correctly.
- Non-uniform scaling can introduce normal-vector errors that affect lighting or display.
- If a result is not correct, restore the relevant `.Pre...` backup or return to your separate original backup.

## 16. Settings

Open Settings from the main window to configure:

- ORZIP command - path or command name used for shape compression and uncompression.
- Unicode editor - editor command used for `.S` and `.SD` file editing.
- Confirm ALL operations - when enabled, SFM3 asks for confirmation before operations.
- Limit File List - when enabled, SFM3 limits the displayed shape-file list to 600 names.

Settings are stored in the user's roaming application data folder under:

```text
ShapeFileManager3/settings.ini
```

If a saved ORZIP path becomes stale, SFM3 falls back to the default ORZIP lookup path.

### ORZIP command

Enter the full path to `orzip.exe`, or enter `orzip.exe` if it is on the Windows `PATH`. If the field is empty or stale, SFM3 tries its default lookup locations.

### Unicode editor

Enter the editor command used for text `.S` and `.SD` files. The default is `notepad.exe`. You may use another Unicode-capable editor if it is installed and available by full path or on `PATH`.

### Confirm ALL operations

When enabled, SFM3 asks before performing operations such as compress, uncompress, reverse, rotate, scale, shift, and indexed edits.

Disabling confirmation can speed up repeated work on known-good copies, but it increases the risk of changing the wrong file.

### Limit File List

When enabled, SFM3 displays a maximum of 600 shape files in the current folder.

Disabling the limit can make large folders slow to display. Prefer a smaller working folder when editing route or trainset assets.

## 17. ORZIP notes

SFM3 uses ORZIP for shape-file compression and uncompression. It does not reimplement the ORZIP compression algorithm.

SFM3 looks for ORZIP in these places:

- The application folder.
- The PyInstaller bundled extraction folder when running as a packaged EXE.
- The Windows `PATH`.
- The fallback application-folder path `orzip.exe`.

If compression or uncompression is unavailable, check the ORZIP command in Settings or place `orzip.exe` beside the application.

## 18. Differences from SFM25

SFM3 keeps the practical file-management workflow of SFM25 but modernizes the runtime and backend.

Major differences:

- SFM3 is a Python/Tkinter desktop application, not an HTA/ActiveX application.
- SFM3 uses ORZIP for compression and uncompression instead of `FFEDITC_UNICODE.EXE`.
- The packaged `SFM3.exe` can bundle ORZIP for simpler distribution.
- Settings are stored under `ShapeFileManager3/settings.ini`.
- The user interface uses double-click or right-click on the shape-file list instead of the old per-row Options button.
- The default Unicode editor is `notepad.exe`.

The old SFM25 help warned that FFEDITC compression and uncompression might fail on some animated locomotives unless patched grammar files were installed. SFM3 no longer depends on FFEDITC, but complex animated shapes still deserve careful backup and verification after any geometry operation.

## 19. Self-test

The application includes a self-test for core shape-file logic.

For the packaged executable:

```bat
SFM3.exe --self-test
```

For source checkout builds:

```bat
python SFM30.py --self-test
```

A passing self-test prints:

```text
self-tests passed
```

## 20. Troubleshooting

### ORZIP not found

Open Settings and confirm that the ORZIP command points to a valid `orzip.exe`, or place `orzip.exe` beside the application.

### Compress or Uncompress fails

Confirm that the selected file is a valid Open Rails `.S` shape file and that ORZIP can run from the configured location. Try the operation on a copy in a simple working folder path.

### Editor does not open

Open Settings and confirm that the Unicode editor command is valid. `notepad.exe` is the default.

### File list is incomplete

If the folder contains more than 600 `.S` files and Limit File List is enabled, SFM3 displays only the first 600 sorted names. Either disable the limit in Settings or copy the files you want to edit into a smaller working folder.

### File shows Unknown Format

The file may not be a supported Open Rails `.S` shape file, or it may be damaged. Work from a known-good backup.

### No editable records were found

The selected shape may not contain the section needed by the chosen operation, or the file structure may differ from the layouts SFM3 currently edits. Check the file manually before assuming it is safe to modify.

### Output is not as expected

Restore the operation-specific `.Pre...` backup file or return to a separate backup copy of the model. Then repeat the operation on a fresh copy with confirmation enabled.

## 21. Licence

Unless otherwise noted, SFM3 is licensed under the Creative Commons Attribution-ShareAlike 4.0 International licence.

Short name: CC BY-SA 4.0

SPDX identifier: CC-BY-SA-4.0

Official licence URL: https://creativecommons.org/licenses/by-sa/4.0/

Third-party tools, binaries, or assets included with or used by the distribution kit may have their own separate licence terms.
