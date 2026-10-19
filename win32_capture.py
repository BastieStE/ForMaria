import ctypes
from ctypes import wintypes
import sys
import threading
import time
from typing import Callable

from config import HOTKEY_OPTIONS, SAVE_FILE, WINDOW_TITLES

# =====================================================================
# Win32 Constants & Structures
# =====================================================================

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

HOTKEY_ID = 1
WM_CLOSE = 0x0010
WM_HOTKEY = 0x0312
WM_RELOAD_HOTKEY = 0x0401
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002

VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12
VK_C = 0x43

ULONG_PTR = wintypes.WPARAM
LRESULT = wintypes.LPARAM


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("union", INPUT_UNION)]


# Win32 Function Signatures (64-bit safe)
user32.OpenClipboard.argtypes = [wintypes.HWND]
user32.OpenClipboard.restype = wintypes.BOOL
user32.CloseClipboard.argtypes = []
user32.CloseClipboard.restype = wintypes.BOOL
user32.EmptyClipboard.argtypes = []
user32.EmptyClipboard.restype = wintypes.BOOL
user32.GetClipboardData.argtypes = [wintypes.UINT]
user32.GetClipboardData.restype = wintypes.HANDLE
user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
user32.SetClipboardData.restype = wintypes.HANDLE
user32.GetClipboardSequenceNumber.argtypes = []
user32.GetClipboardSequenceNumber.restype = wintypes.DWORD

kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalUnlock.restype = wintypes.BOOL
kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
kernel32.GetCurrentThreadId.argtypes = []
kernel32.GetCurrentThreadId.restype = wintypes.DWORD

user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype = wintypes.UINT
user32.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
user32.RegisterHotKey.restype = wintypes.BOOL
user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
user32.UnregisterHotKey.restype = wintypes.BOOL
user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.GetMessageW.restype = wintypes.BOOL
user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PostThreadMessageW.restype = wintypes.BOOL
user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
user32.FindWindowW.restype = wintypes.HWND
user32.GetParent.argtypes = [wintypes.HWND]
user32.GetParent.restype = wintypes.HWND
user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.SendMessageW.restype = LRESULT


# =====================================================================
# OS Helpers & Clipboard Capture
# =====================================================================

def enable_high_dpi() -> None:
    """Enable crisp High-DPI rendering on Windows."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


def set_window_titlebar_theme(window_id: int, is_dark: bool) -> None:
    """Sync the native Windows 10/11 title bar with the app's Dark or Light theme."""
    try:
        hwnd = user32.GetParent(window_id) or window_id
        value = ctypes.c_int(1 if is_dark else 0)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 20, ctypes.byref(value), ctypes.sizeof(value)
        )
    except Exception:
        pass


def close_existing_instance() -> None:
    """Close any previous instance of the window so the global hotkey is freed."""
    for title in WINDOW_TITLES:
        old_hwnd = user32.FindWindowW(None, title)
        if old_hwnd:
            user32.SendMessageW(old_hwnd, WM_CLOSE, 0, 0)
            time.sleep(0.15)


def get_clipboard_text() -> str | None:
    """Safely read Unicode text from the Windows clipboard."""
    for _ in range(5):
        if user32.OpenClipboard(None):
            try:
                handle = user32.GetClipboardData(CF_UNICODETEXT)
                if not handle:
                    return None
                ptr = kernel32.GlobalLock(handle)
                if not ptr:
                    return None
                try:
                    return ctypes.wstring_at(ptr)
                finally:
                    kernel32.GlobalUnlock(handle)
            finally:
                user32.CloseClipboard()
        time.sleep(0.01)
    return None


def set_clipboard_text(text: str) -> None:
    """Safely restore Unicode text to the Windows clipboard."""
    for _ in range(5):
        if user32.OpenClipboard(None):
            try:
                user32.EmptyClipboard()
                encoded = (text + "\0").encode("utf-16-le")
                h_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(encoded))
                if not h_mem:
                    return
                ptr = kernel32.GlobalLock(h_mem)
                if not ptr:
                    return
                ctypes.memmove(ptr, encoded, len(encoded))
                kernel32.GlobalUnlock(h_mem)
                user32.SetClipboardData(CF_UNICODETEXT, h_mem)
                return
            finally:
                user32.CloseClipboard()
        time.sleep(0.01)


def send_ctrl_c(trigger_vk: int) -> None:
    """Release hotkey keys and simulate a clean Ctrl+C keystroke."""
    inputs = (INPUT * 7)()

    inputs[0].type = INPUT_KEYBOARD
    inputs[0].union.ki.wVk = trigger_vk
    inputs[0].union.ki.dwFlags = KEYEVENTF_KEYUP

    inputs[1].type = INPUT_KEYBOARD
    inputs[1].union.ki.wVk = VK_MENU
    inputs[1].union.ki.dwFlags = KEYEVENTF_KEYUP

    inputs[2].type = INPUT_KEYBOARD
    inputs[2].union.ki.wVk = VK_SHIFT
    inputs[2].union.ki.dwFlags = KEYEVENTF_KEYUP

    inputs[3].type = INPUT_KEYBOARD
    inputs[3].union.ki.wVk = VK_CONTROL

    inputs[4].type = INPUT_KEYBOARD
    inputs[4].union.ki.wVk = VK_C

    inputs[5].type = INPUT_KEYBOARD
    inputs[5].union.ki.wVk = VK_C
    inputs[5].union.ki.dwFlags = KEYEVENTF_KEYUP

    inputs[6].type = INPUT_KEYBOARD
    inputs[6].union.ki.wVk = VK_CONTROL
    inputs[6].union.ki.dwFlags = KEYEVENTF_KEYUP

    user32.SendInput(7, inputs, ctypes.sizeof(INPUT))


def capture_selected_text(trigger_vk: int) -> str | None:
    """Copy highlighted text from the active window and restore previous clipboard."""
    old_text = get_clipboard_text()
    seq_before = user32.GetClipboardSequenceNumber()

    send_ctrl_c(trigger_vk)

    copied_text = None
    for _ in range(30):
        time.sleep(0.01)
        if user32.GetClipboardSequenceNumber() != seq_before:
            copied_text = get_clipboard_text()
            break

    if copied_text is not None and old_text is not None and copied_text != old_text:
        set_clipboard_text(old_text)

    return copied_text


# =====================================================================
# Global Hotkey Listener Thread
# =====================================================================

class HotkeyListener:
    def __init__(self, get_hotkey_name: Callable[[], str], on_text_captured: Callable[[str], None]):
        self.get_hotkey_name = get_hotkey_name
        self.on_text_captured = on_text_captured
        self.thread_id: int | None = None

    def start(self) -> None:
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()

    def reload_hotkey(self) -> None:
        if self.thread_id is not None:
            user32.PostThreadMessageW(self.thread_id, WM_RELOAD_HOTKEY, 0, 0)

    def _register(self) -> int:
        hotkey_name = self.get_hotkey_name()
        modifiers, vk = HOTKEY_OPTIONS.get(hotkey_name, HOTKEY_OPTIONS["Ctrl + Q"])
        user32.UnregisterHotKey(None, HOTKEY_ID)
        if not user32.RegisterHotKey(None, HOTKEY_ID, modifiers, vk):
            err = ctypes.get_last_error()
            print(f"Failed to register hotkey {hotkey_name} (Error {err}).", file=sys.stderr)
        else:
            print(f"Listening for {hotkey_name}... (Saving to {SAVE_FILE.name})")
        return vk

    def _loop(self) -> None:
        self.thread_id = kernel32.GetCurrentThreadId()
        current_vk = self._register()

        msg = wintypes.MSG()
        try:
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
                if msg.message == WM_RELOAD_HOTKEY:
                    current_vk = self._register()
                elif msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                    raw_text = capture_selected_text(current_vk)
                    if raw_text:
                        cleaned = " ".join(raw_text.split())
                        if cleaned:
                            self.on_text_captured(cleaned)
        finally:
            user32.UnregisterHotKey(None, HOTKEY_ID)

