#!/usr/bin/env python3
"""Fix cursor: set left_ptr on root and all child windows via ctypes Xlib."""
import ctypes, os, sys

x11 = ctypes.CDLL("libX11.so.6")
XOpenDisplay = x11.XOpenDisplay
XOpenDisplay.restype = ctypes.c_void_p
XOpenDisplay.argtypes = [ctypes.c_char_p]
XDefaultRootWindow = x11.XDefaultRootWindow
XDefaultRootWindow.restype = ctypes.c_ulong
XDefaultRootWindow.argtypes = [ctypes.c_void_p]
XCreateFontCursor = x11.XCreateFontCursor
XCreateFontCursor.restype = ctypes.c_ulong
XCreateFontCursor.argtypes = [ctypes.c_void_p, ctypes.c_uint]
XQueryTree = x11.XQueryTree
XQueryTree.restype = ctypes.c_int
XQueryTree.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong),
                       ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.POINTER(ctypes.c_ulong)),
                       ctypes.POINTER(ctypes.c_uint)]
XGetWindowAttributes = x11.XGetWindowAttributes
XGetWindowAttributes.restype = ctypes.c_int


class XWindowAttributes(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int),
                ("width", ctypes.c_int), ("height", ctypes.c_int),
                ("border_width", ctypes.c_int), ("depth", ctypes.c_int),
                ("visual", ctypes.c_void_p), ("root", ctypes.c_ulong),
                ("class_", ctypes.c_int), ("bit_gravity", ctypes.c_int),
                ("win_gravity", ctypes.c_int), ("backing_store", ctypes.c_int),
                ("backing_planes", ctypes.c_ulong), ("backing_pixel", ctypes.c_ulong),
                ("save_under", ctypes.c_int), ("colormap", ctypes.c_ulong),
                ("map_installed", ctypes.c_int), ("map_state", ctypes.c_int),
                ("all_event_masks", ctypes.c_long), ("your_event_mask", ctypes.c_long),
                ("do_not_propagate_mask", ctypes.c_long), ("override_redirect", ctypes.c_int),
                ("screen", ctypes.c_void_p)]


XDefineCursor = x11.XDefineCursor
XDefineCursor.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong]
XFree = x11.XFree
XSync = x11.XSync
XSync.argtypes = [ctypes.c_void_p, ctypes.c_int]

XC_LEFT_PTR = 68
XC_XTERM = 152  # I-beam

dpy = XOpenDisplay(os.environ.get("DISPLAY", ":99").encode())
if not dpy:
    sys.exit("no display")
root = XDefaultRootWindow(dpy)
arrow = XCreateFontCursor(dpy, XC_LEFT_PTR)
ibeam = XCreateFontCursor(dpy, XC_XTERM)

def walk(win, depth=0):
    attrs = XWindowAttributes()
    XGetWindowAttributes(dpy, win, ctypes.byref(attrs))
    # set arrow everywhere; visible windows only matter
    XDefineCursor(dpy, win, arrow)
    ret_parent = ctypes.c_ulong(); ret_children = ctypes.POINTER(ctypes.c_ulong)(); n = ctypes.c_uint()
    if XQueryTree(dpy, win, ctypes.byref(ret_parent), ctypes.byref(ret_parent), ctypes.byref(ret_children), ctypes.byref(n)):
        kids = ret_children or None
        for i in range(n.value):
            walk(kids[i], depth + 1)
        if kids: XFree(kids)

walk(root)
XSync(dpy, 0)
print("CURSOR_FIXED")
