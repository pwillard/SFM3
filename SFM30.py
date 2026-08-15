#!/usr/bin/env python
"""Shape File Manager 3.0.2.

This is a Python/Tkinter continuation of the old SFM25 HTA
utility.  Version 3.0.2 replaces the obsolete HTA/ActiveX and FFEDITC_UNICODE
conversion dependencies with a normal desktop UI and ORZIP backend.
"""
from __future__ import annotations

import configparser
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, VERTICAL, X, Y, Button, Checkbutton, Entry, Frame, Label, LabelFrame, Listbox, Menu, StringVar, Tk, Toplevel, BooleanVar, messagebox, simpledialog, ttk
from tkinter.scrolledtext import ScrolledText

APP_NAME = "Open Rails Shape File Manager"
APP_VERSION = "3.0.2"
UNCOMPRESSED_MAGIC = "SIMISA@@@@@@@@@@JINX0s1t"
CONFIG_DIR = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "ShapeFileManager3"
CONFIG_FILE = CONFIG_DIR / "settings.ini"

TEXTURE_MODES = [
    ("Normal", "-5"),
    ("DarkShd", "-12"),
    ("HalfBrt", "-11"),
    ("LoShine", "-7"),
    ("HiShine", "-6"),
    ("CrcForm", "-9"),
    ("Bright", "-8"),
]
MIP_LEVELS = [("MIP 0", "0"), ("MIP-1", "-1"), ("MIP-2", "-2"), ("MIP-3", "-3")]


def app_dir() -> Path:
    """Return the folder containing Shape File Manager.

    When running as a script, this is the directory containing this .py file.
    When packaged as an EXE, this is the directory containing the EXE.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def bundled_dir() -> Path:
    """Return the PyInstaller extraction folder, or the app folder when not bundled."""
    return Path(getattr(sys, "_MEIPASS", app_dir())).resolve()


def app_icon_path() -> Path:
    """Return the preferred application icon path for source and bundled runs."""
    for base in (bundled_dir(), app_dir()):
        candidate = base / "assets" / "SFM3.ico"
        if candidate.exists():
            return candidate
    return app_dir() / "assets" / "SFM3.ico"


@dataclass
class ParsedLine:
    text: str
    command: str = ""
    name: str = ""
    ctext: str = ""
    args: list[str] = field(default_factory=list)


def win_path(path: Path | str) -> str:
    return str(Path(path))


def read_shape_lines(path: Path) -> list[str]:
    data = path.read_bytes()
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        return data.decode("utf-16").splitlines()
    try:
        return data.decode("utf-16").splitlines()
    except UnicodeError:
        return data.decode("utf-8", errors="replace").splitlines()


def write_shape_lines(path: Path, lines: list[str]) -> None:
    text = "\r\n".join(lines) + "\r\n"
    path.write_text(text, encoding="utf-16")


def is_uncompressed_shape(path: Path) -> bool:
    data = path.read_bytes()[:64]
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        try:
            return data.decode("utf-16", errors="ignore")[:24] == UNCOMPRESSED_MAGIC
        except UnicodeError:
            return False
    try:
        return data.decode("ascii", errors="ignore")[:24] == UNCOMPRESSED_MAGIC
    except Exception:
        return False


def is_compressed_shape(path: Path) -> bool:
    data = path.read_bytes()[:32]
    if is_uncompressed_shape(path):
        return False
    # The original HTA opened files as Unicode and treated 18771/21321 as
    # compressed markers.  Little-endian bytes 'SI' produce 18771, which is
    # how binary Open Rails compressed files in this folder identify here.
    if len(data) >= 2:
        val = int.from_bytes(data[:2], "little")
        if val in (18771, 21321):
            return True
    return path.suffix.lower() == ".s" and not is_uncompressed_shape(path)


def shape_status(path: Path) -> str:
    if is_uncompressed_shape(path):
        return "Uncompressed"
    if is_compressed_shape(path):
        return "Compressed"
    return "Unknown Format"


def fn_round(x: float) -> str:
    y = round(x, 6)
    if y == int(y):
        return str(int(y))
    return ("%.6f" % y).rstrip("0").rstrip(".")


def parse_line_from(lines: list[str], index: int) -> tuple[ParsedLine, int]:
    s_ln = lines[index]
    original = s_ln
    s_head = ""
    z1 = next((i for i, ch in enumerate(s_ln) if not ch.isspace()), -1)
    if z1 > 0:
        s_head = s_ln[:z1]
        s_ln = " ".join(s_ln[z1:].split())
    else:
        s_ln = " ".join(s_ln.split())
    o = ParsedLine(text=original)
    z1 = s_ln.find("(")
    if z1 > -1:
        s_cmd = s_ln[:z1].rstrip()
        o.ctext = s_head + s_cmd
        z2 = s_cmd.find(" ")
        s_name = ""
        if z2 != -1 and s_cmd:
            s_name = s_cmd[z2:]
            s_cmd = s_cmd[:z2]
        o.command = s_cmd.lstrip().upper().replace(" ", "")
        o.name = s_name
        st = s_ln[z1 + 1 :].lstrip()
        if o.command in {"ESD_BOUNDING_BOX", "ESD_COMPLEX_BOX"}:
            j = index
            while ")" not in st and j + 1 < len(lines):
                j += 1
                extra = " ".join(lines[j].split())
                if extra:
                    st += " " + extra
                index = j
        o.args = st.split() if st else []
    return o, index + 1


def transform_file(path: Path, backup_suffix: str, transform) -> None:
    backup = Path(str(path) + backup_suffix)
    shutil.copy2(path, backup)
    lines = read_shape_lines(backup)
    out: list[str] = []
    i = 0
    state: dict[str, object] = {}
    while i < len(lines):
        o, i = parse_line_from(lines, i)
        new_text = transform(o, state)
        out.append(new_text if new_text is not None else o.text)
    write_shape_lines(path, out)


def transform_sd_file(path: Path, backup_suffix: str, transform) -> None:
    if not path.exists():
        return
    transform_file(path, backup_suffix, transform)


def update_sd_reverse(path: Path, scx: float, scy: float, scz: float, backup_suffix: str) -> None:
    def t(o: ParsedLine, state: dict[str, object]) -> str | None:
        if o.command == "ESD_BOUNDING_BOX" and len(o.args) > 5:
            vals = [float(o.args[i]) for i in range(6)]
            vals = [fn_round(vals[0] * scx), fn_round(vals[1] * scy), fn_round(vals[2] * scz), fn_round(vals[3] * scx), fn_round(vals[4] * scy), fn_round(vals[5] * scz)]
            return f"{o.ctext} ( {min(vals[0], vals[3])} {min(vals[1], vals[4])} {min(vals[2], vals[5])} {max(vals[0], vals[3])} {max(vals[1], vals[4])} {max(vals[2], vals[5])} )"
        if o.command == "ESD_COMPLEX_BOX" and len(o.args) > 11:
            vals = [float(o.args[i]) for i in range(12)]
            for i, sc in enumerate([scx, scy, scz] * 4):
                vals[i] = float(fn_round(vals[i] * sc))
            return f"{o.ctext} ( {fn_round(vals[0])} {fn_round(vals[1])} {fn_round(vals[2])} {fn_round(vals[3])} {fn_round(vals[4])} {fn_round(vals[5])} {fn_round(min(vals[6], vals[9]))} {fn_round(min(vals[7], vals[10]))} {fn_round(min(vals[8], vals[11]))} {fn_round(max(vals[6], vals[9]))} {fn_round(max(vals[7], vals[10]))} {fn_round(max(vals[8], vals[11]))} )"
        return None
    transform_sd_file(path, backup_suffix, t)


def update_sd_rotate(path: Path, scx: float, scy: float, scz: float, backup_suffix: str) -> None:
    def t(o: ParsedLine, state: dict[str, object]) -> str | None:
        if o.command == "ESD_BOUNDING_BOX" and len(o.args) > 5:
            vals = [float(o.args[i]) for i in range(6)]
            vals = [fn_round(vals[0] * scz), fn_round(vals[1] * scy), fn_round(vals[2] * scx), fn_round(vals[3] * scz), fn_round(vals[4] * scy), fn_round(vals[5] * scx)]
            return f"{o.ctext} ( {min(vals[2], vals[5])} {min(vals[1], vals[4])} {min(vals[0], vals[3])} {max(vals[2], vals[5])} {max(vals[1], vals[4])} {max(vals[0], vals[3])} )"
        if o.command == "ESD_COMPLEX_BOX" and len(o.args) > 11:
            vals = [float(o.args[i]) for i in range(12)]
            for i, sc in enumerate([scz, scy, scx] * 4):
                vals[i] = float(fn_round(vals[i] * sc))
            return f"{o.ctext} ( {fn_round(vals[2])} {fn_round(vals[1])} {fn_round(vals[0])} {fn_round(vals[5])} {fn_round(vals[4])} {fn_round(vals[3])} {fn_round(min(vals[8], vals[11]))} {fn_round(min(vals[7], vals[10]))} {fn_round(min(vals[6], vals[9]))} {fn_round(max(vals[8], vals[11]))} {fn_round(max(vals[7], vals[10]))} {fn_round(max(vals[6], vals[9]))} )"
        return None
    transform_sd_file(path, backup_suffix, t)


def update_sd_scale(path: Path, scx: float, scy: float, scz: float, backup_suffix: str) -> None:
    def t(o: ParsedLine, state: dict[str, object]) -> str | None:
        if o.command == "ESD_BOUNDING_BOX" and len(o.args) > 5:
            vals = [float(o.args[i]) for i in range(6)]
            vals = [fn_round(vals[0] * scx), fn_round(vals[1] * scy), fn_round(vals[2] * scz), fn_round(vals[3] * scx), fn_round(vals[4] * scy), fn_round(vals[5] * scz)]
            return f"{o.ctext} ( {min(vals[0], vals[3])} {min(vals[1], vals[4])} {min(vals[2], vals[5])} {max(vals[0], vals[3])} {max(vals[1], vals[4])} {max(vals[2], vals[5])} )"
        if o.command == "ESD_COMPLEX_BOX" and len(o.args) > 11:
            vals = o.args[:]
            for i, sc in zip(range(3, 12), [scx, scy, scz] * 3):
                vals[i] = fn_round(float(vals[i]) * sc)
            return f"{o.ctext} ( {vals[0]} {vals[1]} {vals[2]} {vals[3]} {vals[4]} {vals[5]} {min(vals[6], vals[9])} {min(vals[7], vals[10])} {min(vals[8], vals[11])} {max(vals[6], vals[9])} {max(vals[7], vals[10])} {max(vals[8], vals[11])} )"
        return None
    transform_sd_file(path, backup_suffix, t)


def update_sd_shift(path: Path, dx: float, dy: float, dz: float, backup_suffix: str) -> None:
    def t(o: ParsedLine, state: dict[str, object]) -> str | None:
        if o.command == "ESD_BOUNDING_BOX" and len(o.args) > 5:
            return f"{o.ctext} ( {fn_round(float(o.args[0]) + dx)} {fn_round(float(o.args[1]) + dy)} {fn_round(float(o.args[2]) + dz)} {fn_round(float(o.args[3]) + dx)} {fn_round(float(o.args[4]) + dy)} {fn_round(float(o.args[5]) + dz)} )"
        if o.command == "ESD_COMPLEX_BOX" and len(o.args) > 11:
            return f"{o.ctext} ( {o.args[0]} {o.args[1]} {o.args[2]} {fn_round(float(o.args[3]) + dx)} {fn_round(float(o.args[4]) + dy)} {fn_round(float(o.args[5]) + dz)} {o.args[6]} {o.args[7]} {o.args[8]} {o.args[9]} {o.args[10]} {o.args[11]} )"
        return None
    transform_sd_file(path, backup_suffix, t)


def scale_shape(path: Path, scx: float, scy: float, scz: float, uniform: bool) -> None:
    if scx <= 0 or scy <= 0 or scz <= 0:
        raise ValueError("Scale factors must be positive nonzero numbers.")
    scmax = max(scx, scy, scz)
    def t(o: ParsedLine, state: dict[str, object]) -> str | None:
        vtype = state.get("vtype", 0)
        if o.command == "POINT" and len(o.args) > 2:
            return f"{o.ctext} ( {fn_round(float(o.args[0]) * scx)} {fn_round(float(o.args[1]) * scy)} {fn_round(float(o.args[2]) * scz)} )"
        if o.command == "VECTOR":
            if vtype == 1 and len(o.args) > 3:
                return f"{o.ctext} ( {fn_round(float(o.args[0]) * scx)} {fn_round(float(o.args[1]) * scy)} {fn_round(float(o.args[2]) * scz)} ) {fn_round(float(o.args[4]) * scmax)}"
            if vtype == 2 and not uniform and len(o.args) > 2:
                vx, vy, vz = float(o.args[0]), float(o.args[1]), float(o.args[2])
                vold = (vx * vx + vy * vy + vz * vz) ** 0.5
                if vold:
                    vx, vy, vz = vx / scx, vy / scy, vz / scz
                    vnew = (vx * vx + vy * vy + vz * vz) ** 0.5
                    return f"{o.ctext} ( {fn_round(vx * vold / vnew)} {fn_round(vy * vold / vnew)} {fn_round(vz * vold / vnew)} )"
            if vtype == 3 and len(o.args) > 2:
                return f"{o.ctext} ( {fn_round(float(o.args[0]) * scx)} {fn_round(float(o.args[1]) * scy)} {fn_round(float(o.args[2]) * scz)} )"
        if o.command == "VOL_SPHERE":
            state["vtype"] = 1
        if o.command == "NORMALS":
            state["vtype"] = 2
        if o.command == "SORT_VECTORS":
            state["vtype"] = 3
        if o.command == "LINEAR_KEY" and len(o.args) > 3:
            return f"{o.ctext} ( {o.args[0]} {fn_round(float(o.args[1]) * scx)} {fn_round(float(o.args[2]) * scy)} {fn_round(float(o.args[3]) * scz)} )"
        if o.command == "MATRIX" and len(o.args) > 11:
            return f"{o.ctext} ( {' '.join(o.args[:9])} {fn_round(float(o.args[9]) * scx)} {fn_round(float(o.args[10]) * scy)} {fn_round(float(o.args[11]) * scz)} )"
        return None
    transform_file(path, ".PreScale", t)
    update_sd_scale(Path(str(path) + "d"), scx, scy, scz, ".PreScale")


def reverse_shape(path: Path) -> None:
    scx, scy, scz = -1.0, 1.0, -1.0
    def t(o: ParsedLine, state: dict[str, object]) -> str | None:
        vtype = state.get("vtype", 0)
        if o.command == "POINT" and len(o.args) > 2:
            return f"{o.ctext} ( {fn_round(float(o.args[0]) * scx)} {fn_round(float(o.args[1]) * scy)} {fn_round(float(o.args[2]) * scz)} )"
        if o.command == "VECTOR" and len(o.args) > 2:
            if vtype == 1 and len(o.args) > 3:
                return f"{o.ctext} ( {fn_round(float(o.args[0]) * scx)} {fn_round(float(o.args[1]) * scy)} {fn_round(float(o.args[2]) * scz)} ) {o.args[4]}"
            if vtype in (2, 3):
                return f"{o.ctext} ( {fn_round(float(o.args[0]) * scx)} {fn_round(float(o.args[1]) * scy)} {fn_round(float(o.args[2]) * scz)} )"
        if o.command == "VOL_SPHERE": state["vtype"] = 1
        if o.command == "NORMALS": state["vtype"] = 2
        if o.command == "SORT_VECTORS": state["vtype"] = 3
        if o.command == "LINEAR_KEY" and len(o.args) > 3:
            return f"{o.ctext} ( {o.args[0]} {fn_round(float(o.args[1]) * scx)} {fn_round(float(o.args[2]) * scy)} {fn_round(float(o.args[3]) * scz)} )"
        if o.command == "TCB_KEY" and len(o.args) > 9:
            return f"{o.ctext} ( {o.args[0]} {fn_round(float(o.args[1]) * scx)} {o.args[2]} {fn_round(float(o.args[3]) * scz)} {' '.join(o.args[4:10])} )"
        if o.command == "MATRIX" and len(o.args) > 11:
            return f"{o.ctext} ( {o.args[0]} {fn_round(float(o.args[1]) * scx)} {o.args[2]} {fn_round(float(o.args[3]) * scx)} {o.args[4]} {fn_round(float(o.args[5]) * scz)} {o.args[6]} {fn_round(float(o.args[7]) * scz)} {o.args[8]} {fn_round(float(o.args[9]) * scx)} {fn_round(float(o.args[10]) * scy)} {fn_round(float(o.args[11]) * scz)} )"
        return None
    transform_file(path, ".PreReverse", t)
    update_sd_reverse(Path(str(path) + "d"), scx, scy, scz, ".PreReverse")


def rotate_shape(path: Path, clockwise: bool) -> None:
    scx, scy, scz = (1.0, 1.0, -1.0) if clockwise else (-1.0, 1.0, 1.0)
    def t(o: ParsedLine, state: dict[str, object]) -> str | None:
        vtype = state.get("vtype", 0)
        if o.command == "POINT" and len(o.args) > 2:
            return f"{o.ctext} ( {fn_round(float(o.args[2]) * scx)} {fn_round(float(o.args[1]) * scy)} {fn_round(float(o.args[0]) * scz)} )"
        if o.command == "VECTOR" and len(o.args) > 2:
            if vtype == 1 and len(o.args) > 3:
                return f"{o.ctext} ( {fn_round(float(o.args[2]) * scx)} {fn_round(float(o.args[1]) * scy)} {fn_round(float(o.args[0]) * scz)} ) {o.args[4]}"
            if vtype in (2, 3):
                return f"{o.ctext} ( {fn_round(float(o.args[2]) * scx)} {fn_round(float(o.args[1]) * scy)} {fn_round(float(o.args[0]) * scz)} )"
        if o.command == "VOL_SPHERE": state["vtype"] = 1
        if o.command == "NORMALS": state["vtype"] = 2
        if o.command == "SORT_VECTORS": state["vtype"] = 3
        if o.command == "LINEAR_KEY" and len(o.args) > 3:
            return f"{o.ctext} ( {o.args[0]} {fn_round(float(o.args[3]) * scx)} {fn_round(float(o.args[2]) * scy)} {fn_round(float(o.args[1]) * scz)} )"
        if o.command == "TCB_KEY" and len(o.args) > 9:
            return f"{o.ctext} ( {o.args[0]} {fn_round(float(o.args[3]) * scx)} {o.args[2]} {fn_round(float(o.args[1]) * scz)} {' '.join(o.args[4:10])} )"
        if o.command == "MATRIX" and len(o.args) > 11:
            return f"{o.ctext} ( {o.args[8]} {fn_round(float(o.args[7]) * scx)} {fn_round(float(o.args[6]) * scx * scz)} {fn_round(float(o.args[5]) * scx)} {o.args[4]} {fn_round(float(o.args[3]) * scz)} {fn_round(float(o.args[2]) * scx * scz)} {fn_round(float(o.args[1]) * scz)} {o.args[0]} {fn_round(float(o.args[11]) * scx)} {fn_round(float(o.args[10]) * scy)} {fn_round(float(o.args[9]) * scz)} )"
        return None
    transform_file(path, ".PreRotate", t)
    update_sd_rotate(Path(str(path) + "d"), scx, scy, scz, ".PreRotate")


def shift_shape(path: Path, dx: float, dy: float, dz: float) -> None:
    def t(o: ParsedLine, state: dict[str, object]) -> str | None:
        if o.command == "POINT" and len(o.args) > 2:
            return f"{o.ctext} ( {fn_round(float(o.args[0]) + dx)} {fn_round(float(o.args[1]) + dy)} {fn_round(float(o.args[2]) + dz)} )"
        if o.command == "LINEAR_KEY" and len(o.args) > 3:
            return f"{o.ctext} ( {o.args[0]} {fn_round(float(o.args[1]) + dx)} {fn_round(float(o.args[2]) + dy)} {fn_round(float(o.args[3]) + dz)} )"
        if o.command == "VOL_SPHERE":
            state["after_vol_sphere"] = True
            return None
        if state.pop("after_vol_sphere", False) and len(o.args) > 3:
            return f"{o.ctext} ( {fn_round(float(o.args[0]) + dx)} {fn_round(float(o.args[1]) + dy)} {fn_round(float(o.args[2]) + dz)} ) {o.args[4]}"
        return None
    transform_file(path, ".PreShift", t)
    update_sd_shift(Path(str(path) + "d"), dx, dy, dz, ".PreShift")


def collect_records(path: Path, section_type: str) -> list[dict[str, object]]:
    lines = read_shape_lines(path)
    i = 0
    records: list[dict[str, object]] = []
    matrices: list[str] = []
    images: list[str] = []
    current_index = 0
    polys: list[int] = []
    distances: list[str] = []
    while i < len(lines):
        o, i = parse_line_from(lines, i)
        if section_type == "tex":
            if o.command == "MATRIX": matrices.append(o.name.strip())
            if o.command == "VTX_STATES": current_index = 0
            if o.command == "VTX_STATE" and len(o.args) > 4:
                mat = matrices[int(o.args[1])] if o.args[1].isdigit() and int(o.args[1]) < len(matrices) else o.args[1]
                records.append({"index": current_index, "matrix": mat, "value": o.args[2]})
                current_index += 1
            if o.command == "LOD_CONTROLS": break
        elif section_type == "mip":
            if o.command == "IMAGE" and o.args: images.append(o.args[0])
            if o.command == "TEXTURES": current_index = 0
            if o.command == "TEXTURE" and len(o.args) > 3:
                tex = images[int(o.args[0])] if o.args[0].lstrip("-").isdigit() and int(o.args[0]) < len(images) else o.args[0]
                records.append({"index": current_index, "texture": tex, "value": o.args[2]})
                current_index += 1
            if o.command == "LOD_CONTROLS": break
        elif section_type == "dl":
            if o.command == "DLEVEL_SELECTION" and o.args:
                distances.append(o.args[0]); polys.append(0)
            if o.command == "GEOMETRY_INFO" and o.args and polys:
                try: polys[-1] += int(float(o.args[0]))
                except ValueError: pass
            if o.command == "ANIMATIONS": break
    if section_type == "dl":
        return [{"index": idx, "polygons": polys[idx], "value": distances[idx]} for idx in range(len(distances))]
    return records


def update_indexed_values(path: Path, backup_suffix: str, command: str, values: list[str]) -> None:
    idx = 0
    def t(o: ParsedLine, state: dict[str, object]) -> str | None:
        nonlocal idx
        if o.command == command and idx < len(values):
            n = values[idx]
            idx += 1
            if command == "DLEVEL_SELECTION":
                return f"{o.ctext} ( {n} )"
            if command == "VTX_STATE" and len(o.args) > 4:
                return f"{o.ctext} ( {o.args[0]} {o.args[1]} {n} {o.args[3]} {o.args[4]} )"
            if command == "TEXTURE" and len(o.args) > 3:
                return f"{o.ctext} ( {o.args[0]} {o.args[1]} {n} {o.args[3]} )"
        if command == "VTX_STATE" and o.command == "SUB_OBJECT_HEADER" and o.args and o.args[0] != "00000100":
            prefix = "00000100" if o.args[0] == "00000500" else "00000000"
            return f"{o.ctext} ( {prefix} {' '.join(o.args[1:5])}"
        return None
    transform_file(path, backup_suffix, t)


class SFMApp:
    def __init__(self, root: Tk) -> None:
        self.root = root
        root.title(f"{APP_NAME} {APP_VERSION}")
        try:
            root.iconbitmap(default=str(app_icon_path()))
        except Exception:
            pass
        root.geometry("1000x650")
        self.config = self.load_config()
        self.current_dir = Path(self.config.get("settings", "start_dir", fallback=os.getcwd()))
        if not self.current_dir.exists(): self.current_dir = Path(os.getcwd())
        self.confirm_all = BooleanVar(value=self.config.getboolean("settings", "confirm_all", fallback=True))
        self.limit_file_list = BooleanVar(value=self.config.getboolean("settings", "limit_file_list", fallback=True))
        self.orzip_cmd = StringVar(value=self.resolve_orzip_cmd(self.config.get("settings", "orzip_cmd", fallback="")))
        self.editor = StringVar(value=self.config.get("settings", "editor", fallback="notepad.exe"))
        self.search_filter = StringVar(value="")
        self.search_subfolders = BooleanVar(value=True)
        self.path_by_item: dict[str, Path] = {}
        self.build_ui()
        self.search_filter.trace_add("write", lambda *_: self.refresh_files())
        self.refresh()

    def load_config(self) -> configparser.ConfigParser:
        cp = configparser.ConfigParser()
        if CONFIG_FILE.exists(): cp.read(CONFIG_FILE)
        if not cp.has_section("settings"): cp.add_section("settings")
        return cp

    def save_config(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.config.set("settings", "start_dir", str(self.current_dir))
        self.config.set("settings", "confirm_all", str(self.confirm_all.get()))
        self.config.set("settings", "limit_file_list", str(self.limit_file_list.get()))
        self.config.set("settings", "orzip_cmd", self.orzip_cmd.get())
        self.config.set("settings", "editor", self.editor.get())
        with CONFIG_FILE.open("w", encoding="utf-8") as f: self.config.write(f)

    def default_orzip_cmd(self) -> str:
        for folder in (app_dir(), bundled_dir()):
            for name in ("orzip.exe", "orzip"):
                candidate = folder / name
                if candidate.exists():
                    return str(candidate)
        return shutil.which("orzip.exe") or shutil.which("orzip") or str(app_dir() / "orzip.exe")

    def resolve_orzip_cmd(self, configured: str) -> str:
        cmd = configured.strip()
        if not cmd:
            return self.default_orzip_cmd()
        if Path(cmd).exists() or shutil.which(cmd):
            return cmd
        return self.default_orzip_cmd()

    def build_ui(self) -> None:
        top = Frame(self.root); top.pack(fill=X, padx=6, pady=4)
        Label(top, text=f"{APP_NAME} {APP_VERSION}", font=("Segoe UI", 13, "bold")).pack(side=LEFT)
        Button(top, text="Instructions", command=self.show_help).pack(side=RIGHT, padx=2)
        Button(top, text="Settings", command=self.show_settings).pack(side=RIGHT, padx=2)
        Button(top, text="Refresh", command=self.refresh).pack(side=RIGHT, padx=2)
        drives = Frame(self.root); drives.pack(fill=X, padx=6)
        Label(drives, text="Drives:").pack(side=LEFT)
        if os.name == "nt":
            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                p = Path(f"{letter}:/")
                if p.exists(): Button(drives, text=f"{letter}:", command=lambda p=p: self.move_to(p)).pack(side=LEFT, padx=1)
        main = Frame(self.root); main.pack(fill=BOTH, expand=True, padx=6, pady=6)
        left = Frame(main); left.pack(side=LEFT, fill=Y, padx=(0,6))
        right = Frame(main); right.pack(side=RIGHT, fill=BOTH, expand=True)
        Label(left, text="Current Directory").pack(anchor="w")
        self.dir_label = Label(left, text="", wraplength=300, justify=LEFT, bg="#eeeeee"); self.dir_label.pack(fill=X)
        Button(left, text="Up One Folder", command=lambda: self.move_to(self.current_dir.parent)).pack(fill=X, pady=3)
        Label(left, text="Sub Directories").pack(anchor="w")
        self.dir_list = Listbox(left, width=42, height=28); self.dir_list.pack(fill=Y, expand=True)
        self.dir_list.bind("<Double-Button-1>", self.open_selected_dir)
        search = Frame(right); search.pack(fill=X)
        Label(search, text="Search Shape Files").pack(side=LEFT)
        Entry(search, textvariable=self.search_filter, width=32).pack(side=LEFT, fill=X, expand=True, padx=6)
        Checkbutton(search, text="Include Subfolders", variable=self.search_subfolders, command=self.refresh_files).pack(side=LEFT, padx=(0,6))
        Button(search, text="Clear", command=self.clear_search).pack(side=RIGHT)
        Label(right, text="Shape Files").pack(anchor="w")
        cols = ("name", "folder", "size", "status")
        tree_frame = Frame(right); tree_frame.pack(fill=BOTH, expand=True)
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        tree_scroll = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        for c, w in [("name", 340), ("folder", 230), ("size", 90), ("status", 140)]:
            self.tree.heading(c, text=c.title()); self.tree.column(c, width=w)
        tree_scroll.pack(side=LEFT, fill=Y)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        self.tree.bind("<Double-Button-1>", self.show_file_menu)
        self.menu = Menu(self.root, tearoff=0)
        self.tree.bind("<Button-3>", self.popup_file_menu)

    def move_to(self, path: Path) -> None:
        if path.exists() and path.is_dir():
            self.current_dir = path
            self.save_config()
            self.refresh()

    def open_selected_dir(self, _event=None) -> None:
        sel = self.dir_list.curselection()
        if sel: self.move_to(self.current_dir / self.dir_list.get(sel[0]).strip("\\/"))

    def clear_search(self) -> None:
        self.search_filter.set("")

    def refresh(self) -> None:
        self.dir_label.config(text=str(self.current_dir))
        self.dir_list.delete(0, END)
        try:
            for p in sorted([p for p in self.current_dir.iterdir() if p.is_dir()], key=lambda p: p.name.upper()):
                self.dir_list.insert(END, "\\" + p.name)
        except OSError as e:
            messagebox.showerror("Directory error", str(e)); return
        self.refresh_files()

    def refresh_files(self) -> None:
        if not hasattr(self, "tree"):
            return
        query = self.search_filter.get().strip().lower()
        recursive = bool(query and self.search_subfolders.get())
        self.path_by_item = {}
        for item in self.tree.get_children(): self.tree.delete(item)
        limit = 600 if self.limit_file_list.get() else 999999
        count = 0
        pattern = "**/*.s" if recursive else "*.s"
        try:
            paths = sorted(self.current_dir.glob(pattern), key=lambda p: str(p.relative_to(self.current_dir)).upper())
        except OSError as e:
            messagebox.showerror("Directory error", str(e)); return
        for p in paths:
            if query and query not in p.name.lower():
                continue
            if count >= limit: break
            try: size = f"{p.stat().st_size // 1024} Kb"; status = shape_status(p)
            except OSError: continue
            folder = "." if p.parent == self.current_dir else str(p.parent.relative_to(self.current_dir))
            item = self.tree.insert("", END, values=(p.name, folder, size, status))
            self.path_by_item[item] = p
            count += 1

    def selected_path(self) -> Path | None:
        sel = self.tree.selection()
        if not sel: return None
        return self.path_by_item.get(sel[0], self.current_dir / self.tree.item(sel[0], "values")[0])

    def popup_file_menu(self, event) -> None:
        row = self.tree.identify_row(event.y)
        if row:
            self.tree.selection_set(row)
            self.show_file_menu(event)

    def show_file_menu(self, event=None) -> None:
        path = self.selected_path()
        if not path: return
        self.menu.delete(0, END)
        status = shape_status(path)
        if status == "Compressed":
            if self.orzip_available(): self.menu.add_command(label="Uncompress", command=lambda: self.compress_action(path, False))
            self.menu.add_command(label="Edit .SD File", command=lambda: self.edit_sd(path))
        elif status == "Uncompressed":
            if self.orzip_available(): self.menu.add_command(label="Compress", command=lambda: self.compress_action(path, True))
            self.menu.add_command(label="Distance Levels", command=lambda: self.indexed_dialog(path, "dl"))
            self.menu.add_command(label="MIP Map Levels", command=lambda: self.indexed_dialog(path, "mip"))
            self.menu.add_command(label="Reverse", command=lambda: self.run_op(path, "Reverse", lambda: reverse_shape(path)))
            self.menu.add_command(label="Rotate 90° CCW", command=lambda: self.run_op(path, "Rotate 90° CCW", lambda: rotate_shape(path, False)))
            self.menu.add_command(label="Rotate 90° CW", command=lambda: self.run_op(path, "Rotate 90° CW", lambda: rotate_shape(path, True)))
            self.menu.add_command(label="Scale", command=lambda: self.scale_dialog(path))
            self.menu.add_command(label="Shift", command=lambda: self.shift_dialog(path))
            self.menu.add_command(label="Texture Modes", command=lambda: self.indexed_dialog(path, "tex"))
            self.menu.add_command(label="Edit .S File", command=lambda: self.edit_file(path))
            self.menu.add_command(label="Edit .SD File", command=lambda: self.edit_sd(path))
        else:
            self.menu.add_command(label="Edit .S File", command=lambda: self.edit_file(path))
        try:
            self.menu.tk_popup(event.x_root, event.y_root) if event else self.menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            self.menu.grab_release()

    def orzip_args(self, *args: str) -> list[str]:
        return [self.orzip_cmd.get(), *args]

    def orzip_available(self) -> bool:
        cmd = self.orzip_cmd.get().strip()
        if not cmd:
            return False
        if Path(cmd).exists():
            return True
        return shutil.which(cmd) is not None

    def confirm(self, path: Path, action: str) -> bool:
        return not self.confirm_all.get() or messagebox.askyesno("Confirm operation", f"SHAPEFILE: {path.name}\n\nACTION: {action}")

    def run_op(self, path: Path, action: str, fn) -> None:
        if not self.confirm(path, action): return
        try:
            fn(); self.refresh(); messagebox.showinfo("Complete", f"{action} complete.")
        except Exception as e:
            messagebox.showerror("File Error", str(e))

    def compress_action(self, path: Path, compress: bool) -> None:
        action = "Compress shape file" if compress else "Uncompress shape file"
        if not self.confirm(path, action): return
        if not self.orzip_available():
            messagebox.showerror("ORZIP not found", f"Unable to find {self.orzip_cmd.get()} on PATH or at the configured path."); return
        try:
            args = self.orzip_args("compress" if compress else "uncompress", str(path))
            result = subprocess.run(args, cwd=str(path.parent), check=True, capture_output=True, text=True, creationflags=(subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0))
            self.refresh(); messagebox.showinfo("Complete", f"{action} complete.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Compress/Uncompress failed", (e.stdout or "") + (e.stderr or str(e)))
        except Exception as e:
            messagebox.showerror("Compress/Uncompress failed", str(e))

    def edit_file(self, path: Path) -> None:
        try: subprocess.Popen([self.editor.get(), str(path)])
        except Exception as e: messagebox.showerror("Editor error", str(e))

    def edit_sd(self, s_path: Path) -> None:
        sd = Path(str(s_path) + "d")
        if not sd.exists():
            write_shape_lines(sd, ["SIMISA@@@@@@@@@@JINX0t1t______", "", f"shape ( {s_path.name}", " ESD_Detail_Level ( 1 )", " ESD_Alternative_Texture ( 0 )", " ESD_No_Visual_Obstruction ()", " ESD_Bounding_Box ()", ")"])
        self.edit_file(sd)

    def scale_dialog(self, path: Path) -> None:
        same = messagebox.askyesno("Scale", "Scale same in all directions?", parent=self.root)
        x = simpledialog.askfloat("Scale", "Scale Factor X", initialvalue=1.0, minvalue=0.000001, parent=self.root)
        if x is None: return
        if same:
            y = z = x
        else:
            y = simpledialog.askfloat("Scale", "Scale Factor Y", initialvalue=x, minvalue=0.000001, parent=self.root)
            z = simpledialog.askfloat("Scale", "Scale Factor Z", initialvalue=x, minvalue=0.000001, parent=self.root)
            if y is None or z is None: return
        self.config.set("settings", "scale_factor", str(x)); self.save_config()
        self.run_op(path, f"Scale by {x}, {y}, {z}", lambda: scale_shape(path, x, y, z, same))

    def shift_dialog(self, path: Path) -> None:
        x = simpledialog.askfloat("Shift", "Shift X (Width)", initialvalue=0.0, parent=self.root)
        if x is None: return
        y = simpledialog.askfloat("Shift", "Shift Y (Height)", initialvalue=0.0, parent=self.root)
        if y is None: return
        z = simpledialog.askfloat("Shift", "Shift Z (Length)", initialvalue=0.0, parent=self.root)
        if z is None: return
        self.run_op(path, f"Shift by {x}, {y}, {z}", lambda: shift_shape(path, x, y, z))

    def indexed_dialog(self, path: Path, kind: str) -> None:
        records = collect_records(path, kind)
        if not records:
            messagebox.showinfo("No records", "No editable records were found."); return
        win = Toplevel(self.root); win.title({"dl":"Distance Levels", "tex":"Texture Modes", "mip":"MIP Map Levels"}[kind])
        vars: list[StringVar] = []
        frame = Frame(win); frame.pack(fill=BOTH, expand=True, padx=8, pady=8)
        for rec in records:
            row = Frame(frame); row.pack(fill=X, pady=1)
            if kind == "dl":
                Label(row, text=f"Level {rec['index']+1}: {rec['polygons']} polygons", width=32, anchor="w").pack(side=LEFT)
                var = StringVar(value=str(rec["value"])); Entry(row, textvariable=var, width=12).pack(side=LEFT); vars.append(var)
            else:
                label = rec.get("matrix", rec.get("texture", ""))
                Label(row, text=f"{rec['index']}: {label}", width=36, anchor="w").pack(side=LEFT)
                var = StringVar(value=str(rec["value"])); vars.append(var)
                options = TEXTURE_MODES if kind == "tex" else MIP_LEVELS
                for name, value in options:
                    ttk.Radiobutton(row, text=name, value=value, variable=var).pack(side=LEFT)
        def apply():
            values = [v.get() for v in vars]
            cmd = {"dl":"DLEVEL_SELECTION", "tex":"VTX_STATE", "mip":"TEXTURE"}[kind]
            suffix = {"dl":".PreDistance", "tex":".PreTexture", "mip":".PreMIPlevel"}[kind]
            self.run_op(path, win.title(), lambda: update_indexed_values(path, suffix, cmd, values))
            win.destroy()
        Button(win, text="OK", command=apply).pack(side=RIGHT, padx=8, pady=8)
        Button(win, text="Cancel", command=win.destroy).pack(side=RIGHT, pady=8)

    def show_settings(self) -> None:
        win = Toplevel(self.root); win.title("Settings")
        Label(win, text="ORZIP command").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        Entry(win, textvariable=self.orzip_cmd, width=70).grid(row=0, column=1, padx=8, pady=4)
        Label(win, text="Unicode editor").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        Entry(win, textvariable=self.editor, width=70).grid(row=1, column=1, padx=8, pady=4)
        Checkbutton(win, text="Confirm ALL operations", variable=self.confirm_all).grid(row=2, column=1, sticky="w", padx=8)
        Checkbutton(win, text="Limit File List", variable=self.limit_file_list).grid(row=3, column=1, sticky="w", padx=8)
        def save(): self.save_config(); self.refresh(); win.destroy()
        def reset():
            self.orzip_cmd.set(self.default_orzip_cmd()); self.editor.set("notepad.exe"); self.confirm_all.set(True); self.limit_file_list.set(True); save()
        Button(win, text="Save", command=save).grid(row=4, column=1, sticky="e", padx=8, pady=8)
        Button(win, text="Reset", command=reset).grid(row=4, column=0, sticky="e", padx=8, pady=8)

    def show_help(self) -> None:
        win = Toplevel(self.root); win.title("Instructions")
        text = ScrolledText(win, width=100, height=35); text.pack(fill=BOTH, expand=True)
        text.insert(END, """Open Rails Shape File Manager 3.0.2

This is a Python/Tkinter continuation of the old SFM25 HTA utility.
Version 3.0.2 replaces the obsolete HTA/ActiveX runtime and uses ORZIP for
shape-file compression/uncompression.

Use the folder list and drive buttons to navigate.  Type part of a filename in Search Shape Files to filter the current folder.  Enable Include Subfolders to search below the current folder too.  Double-click or right-click a .S shape file to show available actions.

Compressed files:
  - Uncompress using ORZIP, if configured/found on PATH.
  - Edit/create the related .SD file.

Uncompressed files:
  - Compress using ORZIP, if configured/found on PATH.
  - Distance Levels, MIP Map Levels, Reverse, Rotate CW/CCW, Scale, Shift, Texture Modes.
  - Edit .S and .SD files with the configured Unicode editor.

All geometry-changing operations make the same backup suffixes inherited from earlier Shape File Manager versions:
.PreScale, .PreShift, .PreReverse, .PreRotate, .PreDistance, .PreTexture, .PreMIPlevel.

CAUTION: Shape files are complex.  Work on copies and keep secure backups.
""")
        text.config(state="disabled")


def main() -> int:
    if "--self-test" in sys.argv:
        return run_self_tests()
    root = Tk()
    SFMApp(root)
    root.mainloop()
    return 0


def run_self_tests() -> int:
    import tempfile
    sample = [
        "SIMISA@@@@@@@@@@JINX0s1t______",
        "points ( 1",
        " point ( 1 2 3 )",
        ")",
        "normals ( 1",
        " vector ( 0 1 0 )",
        ")",
        "vol_sphere (",
        " vector ( 1 2 3 ) 4",
        ")",
        "linear_key ( 0 1 2 3 )",
        "matrix m1 ( 1 0 0 0 1 0 0 0 1 1 2 3 )",
        "images ( 1",
        " image ( texture.ace )",
        ")",
        "textures ( 1",
        " texture ( 0 0 0 0 )",
        ")",
        "vtx_states ( 1",
        " vtx_state ( 0 0 -5 0 0 )",
        ")",
        "dlevel_selection ( 1000 )",
        "geometry_info ( 12 )",
        "animations (",
    ]
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "sample.s"
        sd = Path(str(p) + "d")
        write_shape_lines(p, sample)
        write_shape_lines(sd, ["SIMISA@@@@@@@@@@JINX0t1t______", "ESD_Bounding_Box ( 0 0 0 1 2 3 )"])
        assert is_uncompressed_shape(p), "uncompressed detection failed"
        assert collect_records(p, "dl")[0]["polygons"] == 12
        assert collect_records(p, "mip")[0]["texture"] == "texture.ace"
        assert collect_records(p, "tex")[0]["matrix"] == "m1"
        scale_shape(p, 2, 2, 2, True)
        assert Path(str(p) + ".PreScale").exists()
        lines = read_shape_lines(p)
        assert any("point ( 2 4 6 )" in line.lower() for line in lines), lines
        shift_shape(p, 1, 0, -1)
        assert Path(str(p) + ".PreShift").exists()
        reverse_shape(p)
        assert Path(str(p) + ".PreReverse").exists()
        rotate_shape(p, True)
        assert Path(str(p) + ".PreRotate").exists()
        update_indexed_values(p, ".PreDistance", "DLEVEL_SELECTION", ["500"])
        assert any("dlevel_selection ( 500 )" in line.lower() for line in read_shape_lines(p))
        assert SFMApp.default_orzip_cmd(object())
    print("self-tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
