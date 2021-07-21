"""
CSC110 Course Project: Air Pollution and Forestry
=========================================================
main.py
=========================================================
@author: Tu Anh Pham
"""
from bokeh.server.server import Server
from presentation import bk_app


if __name__ == '__main__':
    # Set the bokeh application for the bokeh server to run.
    # This enable interactive plotting.
    server = Server({'/': bk_app}, num_procs=1)
    server.start()

    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()
