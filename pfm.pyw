# ------------------------------------------
# Name:     pfm.pyw (GUI)
# Purpose:  Python File Manager (PFM) is my first attempt at creating a GUI
#           file manager in Python
#
# Author:   Robin Siebler
# Created:  4/17/16
# ------------------------------------------

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from main_window import MainWindow

# TODO: Implement threads
# TODO: Write out ini settings
# TODO: Monitor drives (in case USB Drive is ejected

__author__ = 'Robin Siebler'
__date__ = '4/17/16'

__appname__ = 'pfm'
__module__ = 'main'
__version__ = '0.1'
__rel_date__ = '4/17/16'


class Handler:
	@staticmethod
	def on_window1_destroy(*args):
		Gtk.main_quit(*args)


def main():
	MainWindow()
	Gtk.main()


if __name__ == '__main__':
	main()
