#!python

import logging
import sys
import win32clipboard
from shotgun_api3 import Shotgun
SERVER_PATH = "" #your server path here
SCRIPT_USER = 'CopyForNuke' #your script name
SCRIPT_KEY =  '' #your key here
sg = Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)

# Install menu in Shotgun.
def installMenu():
	from shotgun_api3 import Shotgun
	from pprint import pprint

	data = {
	  "title":"Copy for Nuke",
	  "url": "obq://CopyForNuke",
	  "list_order": 50,
	  "entity_type": "Version",
	  "selection_required": True,
	}

	#Create the menu item
	menu_item = sg.create("ActionMenuItem", data)


# Define execution function.
def pluginExecute(lArgs, sa):
	logging.info("Executing plugin xyz.")
	print("Copying versions to clipboard.")

	lSequencesToCopy = []
	for sId_filter in sa.selected_ids_filter:
		sgVersion = sg.find_one("Version", [sId_filter], ['sg_path_to_frames', 'sg_first_frame', 'sg_last_frame'])
		lSequencesToCopy.append(sgVersion['sg_path_to_frames'].replace('@@@@', '####') +
								" %d-%d"%(sgVersion['sg_first_frame'], sgVersion['sg_last_frame']))

	win32clipboard.OpenClipboard()
	win32clipboard.EmptyClipboard()
	win32clipboard.SetClipboardText("\n".join(lSequencesToCopy))
	win32clipboard.CloseClipboard()

	print "done."


	# Data comes in this form
	#{'cols': ['code',
	#          'image',
	#          'sg_qt'],
	# 'column_display_names': ['Version Name',
	#                          'Thumbnail',
	#                          'QT'],
	# 'entity_type': 'Version',
	# 'grouping_column': 'created_at',
	# 'grouping_direction': 'desc',
	# 'grouping_method': 'day',
	# 'ids': [7754,
	#         7738,
	#         7739],
	# 'project_id': 84,
	# 'project_name': 'SOURCE_CODE',
	# 'selected_ids': [7754,
	#                  7738,
	#                  7739],
	# 'sg_ids': [{'id': '7754', 'type': 'Version'},
	#            {'id': '7738', 'type': 'Version'},
	#            {'id': '7739', 'type': 'Version'}],
	# 'sg_project_id': {'id': 84, 'type': 'Project'},
	# 'sg_selected_ids': [{'id': '7754', 'type': 'Version'},
	#                     {'id': '7738', 'type': 'Version'},
	#                     {'id': '7739', 'type': 'Version'},],
	# 'sg_user_id': {'id': 39, 'type': 'HumanUser'},
	# 'sort_column': 'code',
	# 'sort_direction': 'asc',
	# 'title': 'Versions',
	# 'user_id': 39,
	# 'user_login': 'flord'}




if __name__ == '__main__':
    sys.exit(installMenu())
