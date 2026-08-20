# Open Rails Shape File Manager 3.0.4

Open Rails Shape File Manager 3.0.4 is a Python/Tkinter continuation of the older SFM25 HTA utility. It replaces the obsolete HTA/ActiveX and FFEDITC_UNICODE workflow with a normal desktop UI and an ORZIP backend for Open Rails shape-file compression tasks.

## Contents

- `SFM30.py` - the Python/Tkinter application.
- `Run_SFM3.bat` - Windows launcher that starts the application from this folder.
- `build_exe.bat` - Windows build script for creating `dist/SFM3.exe` with PyInstaller.
- `build_manual.bat` - Windows build script for creating `docs/SFM3_Manual.pdf`.
- `assets/SFM3.ico` - application/window icon used by the source app and packaged EXE.
- `docs/SFM3_Manual.md` - source for the distribution kit user manual.
- `tools/build_icon.py` - regenerates the PNG/ICO application icon artwork.
- `orzip.exe` - ORZIP backend used for shape-file compression and uncompression when available/configured.
- `LICENSE.md` - Creative Commons Attribution-ShareAlike 4.0 International licence definition for this project, unless a file states otherwise.

## Requirements for running from source

- Windows.
- Python 3.11 or newer recommended.
- Tkinter, included with most standard Python for Windows installs.
- ORZIP available either as `orzip.exe` in this folder or on `PATH`.

The packaged `SFM3.exe` does not require a separate Python installation. ORZIP is bundled into the EXE build and is also still configurable from Settings.

## Quick start

1. Clone or copy this folder to a local working location.
2. Double-click `Run_SFM3.bat`, or run:

   ```bat
   python SFM30.py
   ```

3. Use the folder list and drive buttons to navigate to Open Rails `.S` shape files.
4. Use Search Shape Files to filter the current folder by partial filename when needed.
5. Double-click or right-click a shape file to view the available actions.

## Main features

Compressed shape files:

- Uncompress using ORZIP, if configured or found on `PATH`.
- Edit or create the matching `.SD` file.

Uncompressed shape files:

- Compress using ORZIP.
- Edit distance levels.
- Edit MIP map levels.
- Reverse geometry.
- Rotate 90 degrees clockwise or counter-clockwise.
- Scale geometry.
- Shift geometry.
- Edit texture modes.
- Edit `.S` and `.SD` files with the configured Unicode editor.

Navigation:

- Up One Folder moves from the current directory to the folder above it.
- Search Shape Files filters the current folder's `.S` file list by partial filename.
- Include Subfolders is enabled by default; it extends a non-empty search below the current folder and shows each match's relative folder.
- The Shape Files list includes a Folder column for search results and a left-side vertical scrollbar for long lists.
- Clear removes the filter and shows the normal current-folder list again.

## Backups and caution

Geometry-changing operations create backup files using the same suffixes inherited from earlier Shape File Manager versions:

- `.PreScale`
- `.PreShift`
- `.PreReverse`
- `.PreRotate`
- `.PreDistance`
- `.PreTexture`
- `.PreMIPlevel`

Shape files are complex and can be difficult to repair manually. Work on copies and keep secure backups of original models before modifying them.

## Configuration

Application settings are stored in the user's roaming application data folder under `ShapeFileManager3/settings.ini`.

From the application, open Settings to configure:

- ORZIP command/path.
- Unicode editor command/path.
- Confirmation prompts.
- File list limiting.

## Self-test

Run the built-in self-test with:

```bat
python SFM30.py --self-test
```

For the packaged executable, run:

```bat
dist\SFM3.exe --self-test
```

## Building the EXE

PyInstaller is used to build a single-file Windows GUI executable:

```bat
build_exe.bat
```

The generated executable is written to `dist/SFM3.exe`.

The build uses `assets/SFM3.ico` for the EXE and window icon.

## Building the PDF manual

The distribution kit manual source is `docs/SFM3_Manual.md`. Build the PDF with:

```bat
build_manual.bat
```

The generated PDF is written to `docs/SFM3_Manual.pdf`.

## Licence

Unless otherwise noted, this project is licensed under the Creative Commons Attribution-ShareAlike 4.0 International licence. See `LICENSE.md` for the licence definition and official licence URL.

Third-party tools, binaries, or assets included with or used by this project may have their own licensing terms.
