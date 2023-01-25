from ctypes import windll
from dataclasses import dataclass
from enum import Enum
from typing import Callable


class KeyCodes(Enum):
    LeftMouseButton = 0x01
    RightMouseButton = 0x02
    ControlBreak = 0x03
    MiddleMouseButton = 0x04
    X1MouseButton = 0x05
    X2MouseButton = 0x06
    Backspace = 0x08
    Tab = 0x09
    Clear = 0x0c
    Enter = 0x0d
    Pause = 0x13
    CapsLock = 0x14
    Escape = 0x1B
    Space = 0x20
    PageUp = 0x21
    PageDown = 0x22
    End = 0x23
    Home = 0x24
    LeftArrow = 0x25
    UpArrow = 0x26
    RightArrow = 0x27
    DownArrow = 0x28
    Select = 0x29
    Print = 0x2a
    Execute = 0x2b
    PrintScreen = 0x2c
    Ins = 0x2d
    Delete = 0x2e
    Help = 0x2f
    Key0 = 0x30
    Key1 = 0x31
    Key2 = 0x32
    Key3 = 0x33
    Key4 = 0x34
    Key5 = 0x35
    Key6 = 0x36
    Key7 = 0x37
    Key8 = 0x38
    Key9 = 0x39
    A = 0x41
    B = 0x42
    C = 0x43
    D = 0x44
    E = 0x45
    F = 0x46
    G = 0x47
    H = 0x48
    I = 0x49
    J = 0x4a
    K = 0x4b
    L = 0x4c
    M = 0x4d
    N = 0x4e
    O = 0x4f
    P = 0x50
    Q = 0x51
    R = 0x52
    S = 0x53
    T = 0x54
    U = 0x55
    V = 0x56
    W = 0x57
    X = 0x58
    Y = 0x59
    LeftWindowsKey = 0x5b
    RightWindowsKey = 0x5c
    Application = 0x5d
    Sleep = 0x5f
    NumpadKey0 = 0x60
    NumpadKey1 = 0x61
    NumpadKey2 = 0x62
    NumpadKey3 = 0x63
    NumpadKey4 = 0x64
    NumpadKey5 = 0x65
    NumpadKey6 = 0x66
    NumpadKey7 = 0x67
    NumpadKey8 = 0x68
    NumpadKey9 = 0x69
    Multiply = 0x6a
    Add = 0x6b
    Separator = 0x6c
    Subtract = 0x6d
    Decimal = 0x6e
    Divide = 0x6f
    F1 = 0x70
    F2 = 0x71
    F3 = 0x72
    F4 = 0x73
    F5 = 0x74
    F6 = 0x75
    F7 = 0x76
    F8 = 0x77
    F9 = 0x78
    F10 = 0x79
    F11 = 0x7a
    F12 = 0x7b
    F13 = 0x7c
    F14 = 0x7d
    F15 = 0x7e
    F16 = 0x7f
    F17 = 0x80
    F18 = 0x81
    F19 = 0x82
    F20 = 0x83
    F21 = 0x84
    F22 = 0x85
    F23 = 0x86
    F24 = 0x87
    NumLock = 0x90
    ScrollLock = 0x91
    LeftShift = 0xa0
    RightShift = 0xa1
    LeftControl = 0xa2
    RightControl = 0xa3
    LeftMenu = 0xa4
    RightMenu = 0xa5
    BrowserBack = 0xa6
    BrowserRefresh = 0xa8
    BrowserStop = 0xa9
    BrowserSearch = 0xaa
    BrowserFavorites = 0xab
    BrowserHome = 0xac
    VolumeMute = 0xad
    VolumeDown = 0xae
    VolumeUp = 0xaf
    NextTrack = 0xb0
    PreviousTrack = 0xb1
    StopMedia = 0xb2
    PlayMedia = 0xb3
    StartMailKey = 0xb4
    SelectMedia = 0xb5


class KeyboardEvents(Enum):
    KeyDown = 1
    KeyUp = 2
    SysKeyDown = 3
    SysKeyUp = 4


GetAsyncKeyState = windll.User32.GetAsyncKeyState


@dataclass(frozen=True, eq=True)
class KeyboardEventListener:
    event: KeyboardEvents
    key: KeyCodes
    callback: Callable[[KeyboardEvents, KeyCodes], None]


class Keyboard:
    pressed: set[KeyCodes] = set()
    listeners: dict[KeyCodes, dict[KeyboardEvents,
                                   list[KeyboardEventListener]]] = dict()

    @staticmethod
    def on(event: KeyboardEvents, key: KeyCodes, callback):
        listener = KeyboardEventListener(event, key, callback)

        if key not in Keyboard.listeners:
            Keyboard.listeners[key] = dict()

        if key in Keyboard.listeners and event not in Keyboard.listeners[key]:
            Keyboard.listeners[key][event] = list()

        Keyboard.listeners[key][event].append(listener)

    @staticmethod
    def is_pressed(code: KeyCodes) -> bool:
        return code in Keyboard.pressed

    @staticmethod
    def _is_pressed(code: KeyCodes) -> bool:
        return GetAsyncKeyState(code.value) != 0

    @staticmethod
    def throw_event(code: KeyCodes, event: KeyboardEvents):
        if code in Keyboard.listeners and event in Keyboard.listeners[code]:
            for listener in Keyboard.listeners[code][event]:
                listener.callback(event, code)

    @staticmethod
    def listen():
        for code in KeyCodes:
            current_state_pressed = code in Keyboard.pressed

            if not current_state_pressed and Keyboard._is_pressed(code):
                Keyboard.pressed.add(code)
                Keyboard.throw_event(code, KeyboardEvents.KeyDown)

            elif current_state_pressed and not Keyboard._is_pressed(code):
                Keyboard.pressed.remove(code)
                Keyboard.throw_event(code, KeyboardEvents.KeyUp)
