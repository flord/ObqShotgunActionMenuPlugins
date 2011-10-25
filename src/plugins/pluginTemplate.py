#!python

import sys
import win32clipboard
from shotgun_api3 import Shotgun
SERVER_PATH = "https://oblique.shotgunstudio.com" #your server path here
SCRIPT_USER = '' #your script name
SCRIPT_KEY =  '' #your key here
sg = Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)

# Install menu in Shotgun.
def installMenu():

	data = {
	  "title":"", # Menu name
	  "url": "", #obq://<pluginName>/[<arg1>]/[<arg2>]
	  "list_order": 50, # Menu order
	  "entity_type": "Version", # Entity
	  "selection_required": True, # will create problems on pages with lots of entities when set to False.
	}

	#Create the menu item
	menu_item = sg.create("ActionMenuItem", data)


# Define execution function.
def pluginExecute(lArgs, sa):
	''' This is the function that gets called when the plugin is fired.
	lArgs is a list of arguments passed from the url defined earlier.
	sa is an instance of ShotgunAction and contains all the info needed to process the call.

	dir(sa):
	 'action',
	 'column_display_names',  # Internal column names currently displayed on the page
	 'columns',               # Human readable names of the columns currently displayed on the page
	 'entity_type',           # entity type that the page was displaying
	 'ids',                   # All ids of the entities returned by the query (not just those visible on the page)
	 'ids_filter',            # All ids of the entities returned by the query in filter format ready to use in a find() query
	 'params',                # contains the dict will all the values. Details following.
	 'project',               # Project info (if the ActionMenuItem was launched from a page not belonging to a Project (Global Page, My Page, etc.), this will be blank
	 'protocol',
	 'selected_ids',          # ids of entities that were currently selected
	 'selected_ids_filter',   # All selected ids of the entities returned by the query in filter format ready to use in a find() query
	 'title',                 # title of the page
	 'url',                   # The original URL passed to the script.
	 'user'                   # user info who launched the ActionMenuItem

	sa.params=
	{'cols': ['code',
			  'image',
			  'sg_qt],
	 'column_display_names': ['Version Name',
							  'Thumbnail',
							  'QT'],
	 'entity_type': 'Version',
	 'grouping_column': 'created_at',
	 'grouping_direction': 'desc',
	 'grouping_method': 'day',
	 'ids': '7754,7738,7739,7740',
	 'project_id': '84',
	 'project_name': 'SOURCE_CODE',
	 'selected_ids': '7754,7738,7739,7740',
	 'sort_column': 'code',
	 'sort_direction': 'asc',
	 'title': 'Versions',
	 'user_id': '39',
	 'user_login': 'flord'}

	'''
	print("Copying versions to clipboard.")

	lSequencesToProcess = []
	for sId_Filter in sa.selected_ids_filter:
		sgVersion = sg.find_one("Version", [sId_Filter], ['sg_path_to_frames', 'sg_first_frame', 'sg_last_frame'])

	# Continue code

	# In case of error, just raise an exception. It will be trapped in the obqProtocolHandler and the window will stay open for a little while.
	print "done."





if __name__ == '__main__':
    sys.exit(installMenu())
