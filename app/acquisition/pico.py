from __future__ import annotations

import os
import sys
from ctypes import byref, c_int16, create_string_buffer, WinDLL
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple


def _add_windows_dll_dirs() -> list[str]:
    if os.name != "nt":
        return []
    # Common install locations for Pico drivers
    pf = Path(os.environ.get("PROGRAMFILES", r"C:\\Program Files"))
    candidates = [
        pf / "Pico Technology" / "SDK" / "lib",
        pf / "Pico Technology" / "SDK" / "lib" / "x64",
        pf / "Pico Technology" / "SDK" / "lib" / "64",
        pf / "Pico Technology" / "SDK" / "lib" / "ps4000",
        pf / "Pico Technology" / "SDK" / "lib" / "ps4000a",
        pf / "Pico Technology" / "PicoScope 7" / "lib",
        pf / "Pico Technology" / "PicoScope 7 T&M" / "lib",
        pf / "Pico Technology" / "PicoScope 6" / "System",
        pf / "Pico Technology",
    ]
    added: list[str] = []
    for path in candidates:
        if path.exists():
            try:
                # Ensure both loader search path and PATH env var include the directory
                if hasattr(os, "add_dll_directory"):
                    os.add_dll_directory(str(path))  # type: ignore[attr-defined]
                os.environ["PATH"] = f"{path};{os.environ['PATH']}"
                added.append(str(path))
            except Exception:
                pass
    # Additionally, scan Pico Technology folder for ps4000/ps4000a DLLs
    root = pf / "Pico Technology"
    targets = {"ps4000.dll", "ps4000a.dll", "ps4000wrap.dll", "ps4000awrap.dll"}
    if root.exists():
        try:
            for dirpath, _dirnames, filenames in os.walk(root):
                names = set(name.lower() for name in filenames)
                if targets & names:
                    if hasattr(os, "add_dll_directory"):
                        os.add_dll_directory(dirpath)  # type: ignore[attr-defined]
                    os.environ["PATH"] = f"{dirpath};{os.environ['PATH']}"
                    added.append(dirpath)
        except Exception:
            pass
    return added


def _preload_sdk_dlls() -> list[str]:
    """Attempt to early-load ps4000/ps4000a and picoipp DLLs by absolute path.

    Returns list of successfully loaded DLL paths for diagnostics.
    """
    if os.name != "nt":
        return []
    loaded: list[str] = []
    pf = Path(os.environ.get("PROGRAMFILES", r"C:\\Program Files"))
    root = pf / "Pico Technology"
    wanted = ["ps4000.dll", "ps4000a.dll", "picoipp.dll"]
    try:
        for dirpath, _dirnames, filenames in os.walk(root):
            for name in wanted:
                if name in filenames:
                    full = str(Path(dirpath) / name)
                    try:
                        WinDLL(full)
                        loaded.append(full)
                    except Exception:
                        pass
    except Exception:
        pass
    return loaded


@dataclass
class PicoDeviceInfo:
    api: str  # "ps4000" or "ps4000a"
    model: str
    handle: Optional[int] = None


def detect_picoscope() -> tuple[Optional[PicoDeviceInfo], str]:
    """Try to detect an attached PicoScope using ps4000/ps4000a.

    Returns PicoDeviceInfo on success, or None if not found.
    """
    added_dirs = _add_windows_dll_dirs()
    preloaded = _preload_sdk_dlls()
    diagnostics: list[str] = []
    if added_dirs:
        diagnostics.append(f"DLL search dirs: {', '.join(added_dirs)}")
    if preloaded:
        diagnostics.append(f"preloaded: {', '.join(preloaded)}")

    # Try ps4000 first (covers 4262), then ps6000a (covers 6824E)
    for api_name in ("ps4000", "ps4000a", "ps6000a"):
        try:
            if api_name == "ps4000":
                # Attempt via Python wrapper first
                try:
                    from picosdk.ps4000 import ps4000 as ps
                    chandle = c_int16()
                    status = ps.ps4000OpenUnit(byref(chandle))
                    if status == 0:
                        buffer = create_string_buffer(256)
                        required_len = c_int16()
                        ps.ps4000GetUnitInfo(chandle, byref(buffer), c_int16(len(buffer)), byref(required_len), 3)
                        model = buffer.value.decode(errors="ignore")
                        ps.ps4000CloseUnit(chandle)
                        return PicoDeviceInfo(api="ps4000", model=model), ""
                    diagnostics.append(f"ps4000OpenUnit status={status}")
                except Exception as ex:
                    diagnostics.append(f"ps4000 python wrapper failed: {ex}")

                # Fallback: load DLL directly
                dll_candidates = [
                    str(Path(os.environ.get("PROGRAMFILES", r"C:\\Program Files")) / "Pico Technology" / "SDK" / "lib" / "ps4000.dll"),
                    str(Path(os.environ.get("PROGRAMFILES", r"C:\\Program Files")) / "Pico Technology" / "PicoScope 7 T&M Stable" / "ps4000.dll"),
                ]
                for full in dll_candidates:
                    if not Path(full).exists():
                        continue
                    try:
                        lib = WinDLL(full)
                        # Signatures
                        from ctypes import POINTER, c_char_p
                        lib.ps4000OpenUnit.argtypes = [POINTER(c_int16)]
                        lib.ps4000OpenUnit.restype = c_int16
                        lib.ps4000GetUnitInfo.argtypes = [c_int16, c_char_p, c_int16, POINTER(c_int16), c_int16]
                        lib.ps4000GetUnitInfo.restype = c_int16
                        lib.ps4000CloseUnit.argtypes = [c_int16]
                        lib.ps4000CloseUnit.restype = c_int16

                        ch = c_int16()
                        st = lib.ps4000OpenUnit(byref(ch))
                        if st != 0:
                            diagnostics.append(f"ps4000 DLL open status={st}")
                            continue
                        buf = create_string_buffer(256)
                        req = c_int16()
                        lib.ps4000GetUnitInfo(ch, buf, c_int16(len(buf)), byref(req), c_int16(3))
                        model = buf.value.decode(errors="ignore")
                        lib.ps4000CloseUnit(ch)
                        return PicoDeviceInfo(api="ps4000", model=model), ""
                    except Exception as ex2:
                        diagnostics.append(f"ps4000 DLL load failed: {ex2}")
                        continue
            elif api_name == "ps4000a":
                from picosdk.ps4000a import ps4000a as ps
                chandle = c_int16()
                status = ps.ps4000aOpenUnit(byref(chandle), None)
                if status != 0:
                    diagnostics.append(f"ps4000aOpenUnit status={status}")
                    continue
                buffer = create_string_buffer(256)
                required_len = c_int16()
                ps.ps4000aGetUnitInfo(chandle, byref(buffer), c_int16(len(buffer)), byref(required_len), 3)
                model = buffer.value.decode(errors="ignore")
                ps.ps4000aCloseUnit(chandle)
                return PicoDeviceInfo(api="ps4000a", model=model), ""
            elif api_name == "ps6000a":
                from picosdk.ps6000a import ps6000a as ps
                chandle = c_int16()
                status = ps.ps6000aOpenUnit(byref(chandle), None, 1)
                if status != 0:
                    diagnostics.append(f"ps6000aOpenUnit status={status}")
                    continue
                buffer = create_string_buffer(256)
                required_len = c_int16()
                ps.ps6000aGetUnitInfo(chandle, buffer, c_int16(len(buffer)), byref(required_len), 3)
                model = buffer.value.decode(errors="ignore")
                ps.ps6000aCloseUnit(chandle)
                return PicoDeviceInfo(api="ps6000a", model=model), ""
        except Exception as ex:
            diagnostics.append(f"{api_name} import/open failed: {ex}")
            continue

    return None, "; ".join(diagnostics)



