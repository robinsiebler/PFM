# ------------------------------------------
# Name:     pfm.pyw (GUI)
# Purpose:  Python File Manager (PFM) is my first attempt at creating a GUI
#           file manager in Python
#
# Author:   Robin Siebler
# Created:  4/17/16
# ------------------------------------------

import os
import utils  # Helper functions
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio

# TODO: Implement threads
# TODO: Write out ini settings

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


class MainWindow:
	"""Create the application window."""

	def __init__(self):
		# get directories for panes:
		self.l_dir, self.r_dir = utils.get_pane_dirs()

		# get window and controls
		builder = Gtk.Builder()
		builder.add_from_file('ui\pfm.glade')
		builder.connect_signals(Handler())
		window = builder.get_object('window1')

		# get drives, volumes and mounts
		self.volumes, self.mounts, self.drives = utils.get_drives()

		# set up left drive bar
		self.l_drive_letter = os.path.splitdrive(self.l_dir)[0].upper()[:1]
		self.l_drive_combo = builder.get_object('l_drive_combo')
		self.l_drive_list_store = builder.get_object('l_drive_list_store')

		(COL_PIXBUF, COL_STRING) = range(2)
		cell = Gtk.CellRendererText()
		pixbuf = Gtk.CellRendererPixbuf()

		self.l_drive_combo.pack_start(pixbuf, expand=False)
		self.l_drive_combo.add_attribute(pixbuf, 'pixbuf', COL_PIXBUF)
		self.l_drive_combo.pack_start(cell, True)
		self.l_drive_combo.add_attribute(cell, 'text', COL_STRING)
		self.populate_drive_combo(self.mounts, self.l_drive_list_store)
		self.l_drive_combo.set_active_id(self.l_drive_letter)

		# set up the left disk space label
		self.l_drive_space = builder.get_object('l_drive_space_lbl')
		self.l_drive_space.set_text(utils.popuplate_drive_label(self.mounts, self.l_drive_letter))

		# get left pane components
		self.l_store = builder.get_object('treestore1')
		self.l_sorted_model = builder.get_object('treemodelsort1')
		self.l_drive_space.text = utils.get_disk_space(self.l_dir)
		# self.l_store.set_sort_func(1, utils.sort_files, None)
		self.l_sorted_model.set_sort_column_id(1, Gtk.SortType.DESCENDING)
		self.l_pane = builder.get_object('l_pane')

		(COL_PIXBUF, COL_STRING) = range(2)
		cell = Gtk.CellRendererText()
		pixbuf = Gtk.CellRendererPixbuf()

		# name column
		left_f_name = Gtk.TreeViewColumn()
		left_f_name.set_title('Name')
		left_f_name.pack_start(pixbuf, expand=False)
		left_f_name.add_attribute(pixbuf, 'pixbuf', COL_PIXBUF)
		left_f_name.pack_start(cell, True)
		left_f_name.add_attribute(cell, 'text', COL_STRING)
		left_f_name.set_resizable(True)
		left_f_name.set_sort_column_id(1)

		# ext column
		left_f_ext = Gtk.TreeViewColumn()
		left_f_ext.set_title('Ext')
		left_f_ext.pack_start(cell, True)
		left_f_ext.add_attribute(cell, 'text', 2)
		left_f_ext.set_resizable(True)
		left_f_ext.set_sort_column_id(2)

		# size column
		left_f_size = Gtk.TreeViewColumn()
		left_f_size.set_title('Size')
		left_f_size.pack_start(cell, True)
		left_f_size.add_attribute(cell, 'text', 3)
		left_f_size.set_resizable(True)
		left_f_size.set_sort_column_id(6)

		# date column
		left_f_date = Gtk.TreeViewColumn()
		left_f_date.set_title('Date')
		left_f_date.pack_start(cell, True)
		left_f_date.add_attribute(cell, 'text', 4)
		left_f_date.set_resizable(True)
		left_f_date.set_sort_column_id(4)

		# attributes column
		left_f_attr = Gtk.TreeViewColumn()
		left_f_attr.set_title('Attr')
		left_f_attr.pack_start(cell, True)
		left_f_attr.add_attribute(cell, 'text', 5)
		left_f_attr.set_resizable(True)

		# set up left pane
		self.l_pane.append_column(left_f_name)
		self.l_pane.append_column(left_f_ext)
		self.l_pane.append_column(left_f_size)
		self.l_pane.append_column(left_f_date)
		self.l_pane.append_column(left_f_attr)
		self.l_pane.set_model(self.l_store)
		self.populate_tree_store(self.l_dir, self.l_store)



		self.l_pane.get_selection().set_select_function(self.select_function)
		self.l_pane_selection = self.l_pane.get_selection()
		self.l_pane.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
		self.l_pane_selection.get_selected_rows()
		self.l_pane.connect("row-activated", self.on_tree_row_activated, self.l_dir)
		self.l_pane.connect("key-press-event", self.on_treeview_key_press_event)

		cell = Gtk.CellRendererText()
		pixbuf = Gtk.CellRendererPixbuf()

		# set up right drive bar
		self.r_drive_letter = os.path.splitdrive(self.r_dir)[0].upper()[:1]
		self.r_drive_combo = builder.get_object('r_drive_combo')
		self.r_drive_list_store = builder.get_object('r_drive_list_store')

		(COL_PIXBUF, COL_STRING) = range(2)
		cell = Gtk.CellRendererText()
		pixbuf = Gtk.CellRendererPixbuf()

		self.r_drive_combo.pack_start(pixbuf, expand=False)
		self.r_drive_combo.add_attribute(pixbuf, 'pixbuf', COL_PIXBUF)
		self.r_drive_combo.pack_start(cell, True)
		self.r_drive_combo.add_attribute(cell, 'text', COL_STRING)
		self.populate_drive_combo(self.mounts, self.r_drive_list_store)
		self.r_drive_combo.set_active_id(self.r_drive_letter)

		# set up the right disk space label
		self.r_drive_space = builder.get_object('r_drive_space_lbl')
		self.r_drive_space.set_text(utils.popuplate_drive_label(self.mounts, self.r_drive_letter))

		# get right pane components
		self.r_store = builder.get_object('treestore2')
		self.r_sorted_model = builder.get_object('treemodelsort2')
		self.r_sorted_model.set_sort_column_id(1, Gtk.SortType.DESCENDING)
		self.r_pane = builder.get_object('r_pane')

		# name column
		right_f_name = Gtk.TreeViewColumn()
		right_f_name.set_title('Name')
		right_f_name.pack_start(pixbuf, expand=False)
		right_f_name.add_attribute(pixbuf, 'pixbuf', COL_PIXBUF)
		right_f_name.pack_start(cell, True)
		right_f_name.add_attribute(cell, 'text', COL_STRING)
		right_f_name.set_resizable(True)
		right_f_name.set_sort_column_id(1)

		# ext column
		right_f_ext = Gtk.TreeViewColumn()
		right_f_ext.set_title('Ext')
		right_f_ext.pack_start(cell, True)
		right_f_ext.add_attribute(cell, 'text', 2)
		right_f_ext.set_resizable(True)
		right_f_name.set_sort_column_id(2)

		# size column
		right_f_size = Gtk.TreeViewColumn()
		right_f_size.set_title('Size')
		right_f_size.pack_start(cell, True)
		right_f_size.add_attribute(cell, 'text', 3)
		right_f_size.set_resizable(True)
		right_f_name.set_sort_column_id(6)

		# date column
		right_f_date = Gtk.TreeViewColumn()
		right_f_date.set_title('Date')
		right_f_date.pack_start(cell, True)
		right_f_date.add_attribute(cell, 'text', 4)
		right_f_date.set_resizable(True)
		right_f_date.set_sort_column_id(4)

		# attributes column
		right_f_attr = Gtk.TreeViewColumn()
		right_f_attr.set_title('Attr')
		right_f_attr.pack_start(cell, True)
		right_f_attr.add_attribute(cell, 'text', 5)
		right_f_attr.set_resizable(True)

		# set up right pane
		self.r_pane.append_column(right_f_name)
		self.r_pane.append_column(right_f_ext)
		self.r_pane.append_column(right_f_size)
		self.r_pane.append_column(right_f_date)
		self.r_pane.append_column(right_f_attr)
		self.r_pane.set_model(self.r_store)
		self.populate_tree_store(self.r_dir, self.r_store)

		window.set_position(Gtk.WindowPosition.CENTER)
		window.show_all()

	def on_tree_row_activated(self, treeview, path, view_column, dir):
		model = treeview.get_model()
		iter = model.get_iter(path)
		filename = os.path.join(dir, model.get_value(iter, 1))
		print 'You selected ' + filename
		# treeview.row_activated(Gtk.TreePath(row), view_column)
		selected = []
		treeview.get_selection().selected_foreach(self.foreach, selected)
		print 'And the winners are...', selected

	def foreach(self, model, path, iter, selected):
		selected.append(model.get_value(iter, 1))

	def on_treeview_key_press_event(self, treeview, event):
		key = Gdk.keyval_name(event.keyval)
		if key == 'space':
			self.l_pane.get_selection()

	@staticmethod
	def populate_drive_combo(mounts, store):
		"""Add the drives and drive names to the ListStore.

		:param dict mounts:         The dictionary of mount points
		:param Gtk.ListStore store: The ListStore to populate
		"""

		for key, value in mounts.iteritems():
			store.append([mounts[key][1], key, mounts[key][0]])
			# store.append([mounts['C'][1], 'C', mounts['C'][0]])

	@staticmethod
	def populate_tree_store(path, store, parent=None):
		"""Add the directories and then files to the TreeStore.

		:param str path:            The path from which to retrieve the list
		:param Gtk.TreeStore store: The TreeStore to populate
		"""

		dir_list, file_list = utils.dirwalk(path)
		# Append the item to the TreeStore
		for item in dir_list:
			store.append(parent, item)

		for item in file_list:
			store.append(parent, item)

	@staticmethod
	def select_function(treeselection, model, path, current):
		state = True

		if treeselection.count_selected_rows() < 2:
			state = True

		return state


def main():
	MainWindow()
	Gtk.main()


if __name__ == '__main__':
	main()
