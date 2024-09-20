import glfw
import keyboard
import random
import string
import time

import OpenGL.GL as gl

import imgui
from imgui.integrations.glfw import GlfwRenderer

import utils

from logger import logger

from .shapes import *

def main():
    imgui.create_context()
    window = impl_glfw_init()
    impl = GlfwRenderer(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        imgui.new_frame()

        x, y, w, h = utils.get_window_rect()

        # set window config
        glfw.set_window_pos(window, x, y)
        imgui.set_next_window_size(w, h)
        imgui.set_next_window_position(0, 0)

        imgui.begin("Overlay", False, 
            imgui.WINDOW_NO_DECORATION 
            | imgui.WINDOW_NO_BACKGROUND 
            | imgui.WINDOW_NO_BRING_TO_FRONT_ON_FOCUS
            | imgui.WINDOW_NO_MOVE 
            | imgui.WINDOW_NO_INPUTS 
       #     | imgui.WINDOW_NO_COLLAPSE
            | imgui.WINDOW_NO_RESIZE
            | imgui.WINDOW_NO_SCROLL_WITH_MOUSE
            | imgui.WINDOW_NO_TITLE_BAR
            | imgui.WINDOW_NO_SCROLLBAR
        )
        
        # remove borders
        imgui.text('xoxo')

        draw_list = imgui.get_window_draw_list()

        shapes.draw(draw_list)

        imgui.end()

        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()


def impl_glfw_init():
    width, height = 1920, 1080
    window_name = "xoxo ui"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        exit(1)

    logger.info(f"GLFW Version: {glfw.get_version_string()}")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER,glfw.TRUE)
    glfw.window_hint(glfw.FLOATING, glfw.TRUE) 
    glfw.window_hint(glfw.MAXIMIZED, glfw.TRUE)
    glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)

    glfw.window_hint(glfw.MOUSE_PASSTHROUGH, glfw.TRUE)

    window = glfw.create_window(
        width, height, window_name, None, None
    )
    
    glfw.set_window_attrib(window, glfw.DECORATED, glfw.FALSE)

    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        exit(1)

    return window

if __name__ == "__main__":
    main()