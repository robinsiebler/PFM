# ------------------------------------------
# Name:     utils.py
# Purpose:  Utility functions for pfm
#
# Author:   Robin Siebler
# Created:  4/17/16
# ------------------------------------------

import gi
import humanfriendly
import os
import psutil

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GdkPixbuf

from ConfigParser import ConfigParser
from datetime import datetime
from scandir import scandir


def dirwalk(directory):
	"""Walk a directory and return the directories, files and file info.

	:param str directory:   The path to walk
	:return:                The directories and files
	:rtype: tuple
	"""
	dir_list = []
	file_list = []
	# Iterate over the contents of the specified path
	for filename in scandir(directory):
		# Get the absolute path of the item
		fullname = filename.path
		f_size = filename.stat().st_size
		f_name = os.path.splitext(filename.name)[0]
		if filename.is_dir():
			f_ext = ''
			size = '<DIR>'
			dir_list.append([load_file_icon(fullname), '[' + f_name + ']', f_ext, size, get_creation_time(fullname),
			                 get_file_attributes(fullname), 0])
		else:
			f_ext = os.path.splitext(filename.name)[1][1:]
			file_list.append([load_file_icon(fullname), f_name, f_ext, humanfriendly.format_size(f_size),
			                  get_creation_time(fullname), get_file_attributes(fullname), f_size])

	# add parent dir (for navigation purposes)
	possible_parent = os.path.split(os.path.abspath(directory))[0]
	if possible_parent != directory:
		dir_list.insert(0, [load_file_icon(directory), '[..]', '', '<DIR>', get_creation_time(directory),
		                    get_file_attributes(directory), 00])

	return dir_list, file_list

def get_creation_time(f_name):
	"""Return the creation time for a file.

	:param str f_name:  The name of the file
	:return:            The creation time
	:rtype: str
	"""

	t = os.path.getmtime(f_name)
	date = datetime.fromtimestamp(t)
	return date.strftime('%m/%d/%Y %I:%M %p')


def get_disk_space(path):
	"""Returns disk usage stats for the path the drive is on.

	:param str path:    A path on the drive to check
	:return:            Disk usage numbers (tuple of longs) - total, used and free space
	:rtype: tuple
	"""
	return psutil.disk_usage(path)


def get_drives():
	"""Return a list of the drives, mounts and volumes. Volumes and drives
	are currently unhandled. Mounts is a dictionary in the form of
	{drive letter: [drive name, drive icon]}

	:return:        The volumes, mounts and drives, in that order
	:rtype: tuple
	"""
	vm = Gio.VolumeMonitor.get()
	volumes = vm.get_volumes()
	drives = vm.get_connected_drives()
	mounts = vm.get_mounts()

	drive_dict = mount_dict = volume_dict = {}

	for volume in volumes:
		if volume:
			print 'We have a volume! Write code to handle it!'

	for drive in drives:
		if drive:
			print 'We have a drive! Write code to handle it!'

	for mount in mounts:
		if mount:
			name = mount.get_name()
			drive_letter = name[-3:-2]
			label = name[:-5]
			icon = load_drive_icon(mount.get_icon())
			drive = mount.get_root().get_path()
			mount_dict[drive_letter] = [label, icon, drive, mount]

	return volume_dict, drive_dict, sorted(mount_dict)


def get_file_attributes(filename):
	"""Return the attributes for a file

	:param str filename:    The name of the file
	:return:                The file attributes
	:rtype: str
	"""

	ro = ar = hi = sys = '-'
	# get Gio File object
	file_ = Gio.File.new_for_commandline_arg(filename)
	# file attributes
	file_attributes = [Gio.FILE_ATTRIBUTE_DOS_IS_ARCHIVE,
	                   Gio.FILE_ATTRIBUTE_DOS_IS_SYSTEM,
	                   Gio.FILE_ATTRIBUTE_ACCESS_CAN_WRITE,
	                   Gio.FILE_ATTRIBUTE_STANDARD_IS_HIDDEN]
	# convert file attributes to a comma separated string
	file_attributes = ','.join(file_attributes)
	# retrieve file attributes
	info = file_.query_info(file_attributes, 0, None)
	if not info.get_attribute_as_string(Gio.FILE_ATTRIBUTE_ACCESS_CAN_WRITE):
		ro = 'r'
	if info.get_attribute_as_string(Gio.FILE_ATTRIBUTE_DOS_IS_ARCHIVE):
		ar = 'a'
	if info.get_attribute_as_string(Gio.FILE_ATTRIBUTE_STANDARD_IS_HIDDEN):
		hi = 'h'
	if info.get_attribute_as_string(Gio.FILE_ATTRIBUTE_DOS_IS_SYSTEM):
		sys = 's'

	return ''.join([ro, ar, hi, sys])


def get_folder_size(path):
	"""Return total size of files in given path and subdirs."""
	total = 0
	for entry in scandir(path):
		if entry.is_dir(follow_symlinks=False):
			total += get_folder_size(entry.path)
		else:
			total += entry.stat(follow_symlinks=False).st_size
	return total


def get_pane_dirs():
	"""Check the ini file, if it exists, for the directories.
	In case of error set to the System Drive.

	:return:    The directory for each pane
	:rtype: tuple
	"""

	config_file = os.path.join(os.getcwd(), 'pfm.ini')
	if os.path.exists(config_file):
		l_dir = get_settings('Paths', config_file)['left_pane']
		if l_dir is None or not os.path.exists(l_dir):
			l_dir = os.environ['SYSTEMDRIVE']
		r_dir = get_settings('Paths', config_file)['right_pane']
		if r_dir is None or not os.path.exists(r_dir):
			r_dir = os.environ['SYSTEMDRIVE']
	else:
		l_dir = os.environ['SYSTEMDRIVE']
		r_dir = os.environ['SYSTEMDRIVE']

	return l_dir, r_dir


def get_settings(section, config_file):
	"""Read a given section from a config file and return it.

	:param str section:         The section to read
	:param str  config_file:    The file to read from
	:return:                    A dictionary of settings
	:rtype: dict
	"""

	config = ConfigParser()
	config.read(config_file)

	dict1 = {}
	options = config.options(section)
	for option in options:
		try:
			dict1[option] = config.get(section, option)
			if dict1[option] == -1:
				print("skip: %s" % option)
		except:
			print("exception on %s!" % option)
			dict1[option] = None
	return dict1


def load_drive_icon(drive_icon):
	"""Return the icon for a drive as a Pixbuf

	:param Gtk.Icon drive_icon: The icon for the drive
	:return: The Pixbuf
	:rtype: Gsk.Pixbuf
	"""

	try:
		if isinstance(drive_icon, Gio.ThemedIcon):
			theme = Gtk.IconTheme.get_default()
			return theme.choose_icon(drive_icon.get_names(), 16, 0).load_icon()
		elif isinstance(drive_icon, Gio.FileIcon):
			iconpath = drive_icon.get_file().get_path()
			return GdkPixbuf.Pixbuf.new_from_file(iconpath)
	except:
		return


def load_file_icon(filename):
	"""Find the icon of the given filename as as
	   gtk.gdk.Pixbuf. return None if the icon can't
	   be found.
	"""

	# TODO: Figure out how to retrieve missing icons

	file_ = Gio.File.new_for_commandline_arg(filename)
	try:
		info = file_.query_info('standard::icon', 0, None)
		icon = info.get_icon()
		if isinstance(icon, Gio.ThemedIcon):
			theme = Gtk.IconTheme.get_default()
			return theme.choose_icon(icon.get_names(), 16, 0).load_icon()
		elif isinstance(icon, Gio.FileIcon):
			iconpath = icon.get_file().get_path()
			return GdkPixbuf.Pixbuf.new_from_file(iconpath)
	except:
		return

	# This is supposed to be the better way, but it doesn't return correct icon for folders.
	# content_type, val = Gio.content_type_guess(filename=filename, data=None)
	# icon = Gio.content_type_get_icon(content_type)
	# try:
	# 	if isinstance(icon, Gio.ThemedIcon):
	# 		theme = Gtk.IconTheme.get_default()
	# 		return theme.choose_icon(icon.get_names(), 16, 0).load_icon()
	# 	elif isinstance(icon, Gio.FileIcon):
	# 		iconpath = icon.get_file().get_path()
	# 		return GdkPixbuf.Pixbuf.new_from_file(iconpath)
	# except:
	# 	return


def popuplate_drive_label(mounts, drive_letter):
	""" Return the free and total space for a drive.

	:param mounts:          A dictionary containing the mount points
	:param drive_letter:    The drive to query
	:return:                The volume name, free and total space
	:rtype: str
	"""

	drive_letter = mounts[drive_letter][2]
	total, used, free, percentage = get_disk_space(drive_letter)

	return humanfriendly.format_size(free) + ' of ' + humanfriendly.format_size(total) + ' free'

def sort_files(model, row1, row2, data):
	pass
