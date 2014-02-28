#!python

import logging
import sys
import os
import win32clipboard
import subprocess
from fuzzLib.managerClient import Api

from shotgun_api3 import Shotgun
SERVER_PATH = "" #your server path here
SCRIPT_USER = 'GoodForEdit' #your script name
SCRIPT_KEY =  '' #your key here
sg = Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)

# Install menu in Shotgun.
def installMenu():
	from shotgun_api3 import Shotgun
	from pprint import pprint

	data = {
	  "title":"Good for Edit (Anim)", # Menu name
	  "url": "obq://GoodForEdit/Anim", #obq://<pluginName>/[<arg1>]/[<arg2>]
	  "list_order": 20, # Menu order
	  "entity_type": "Version", # Entity
	  "selection_required": True, # will create problems on pages with lots of entities when set to False.
	}
	#Create the menu item
	menu_item = sg.create("ActionMenuItem", data)

	data = {
	  "title":"Good for Edit (Comp)", # Menu name
	  "url": "obq://GoodForEdit/Comp", #obq://<pluginName>/[<arg1>]/[<arg2>]
	  "list_order": 25, # Menu order
	  "entity_type": "Version", # Entity
	  "selection_required": True, # will create problems on pages with lots of entities when set to False.
	}
	#Create the menu item
	menu_item = sg.create("ActionMenuItem", data)

	data = {
	  "title":"Good for Edit (Comp) and Play (SEARCH_AND_RESCUE only)", # Menu name
	  "url": "obq://GoodForEdit/CompPlay", #obq://<pluginName>/[<arg1>]/[<arg2>]
	  "list_order": 26, # Menu order
	  "entity_type": "Version", # Entity
	  "selection_required": True, # will create problems on pages with lots of entities when set to False.
	}
	#Create the menu item
	menu_item = sg.create("ActionMenuItem", data)


# Define execution function.
def pluginExecute(lArgs, sa):
	logging.info("Executing plugin GoodForEdit.")
	print("Copying versions to clipboard.")

	# First, get the Project from the first version
	if sa.project:
		dSGProject = sa.project
	else:
		lSGVersions = sg.find("Version", sa.ids_filter, ['project'])
		dSGProject = lSGVersions[0]['project']

	iProjectManagerID = int(sg.find_one('Project', [['id', 'is', dSGProject['id']]], ['sg_projectmanager_id'])['sg_projectmanager_id'])
	api = Api()
	oPMRootProject = api.getProjectsBySearch({'uid':iProjectManagerID})[0]

	# Then, find the DAILIES folder and checks if it exists.
	dailiesDir = oPMRootProject.getAbsPathOnline() + '/' + "DAILIES"
	if lArgs[0] == 'Comp' or lArgs[0] == 'CompPlay':
		sTargetPath = dailiesDir + '/' + "EDIT_COMP"
		sSGInEditFieldName = 'sg_in_edit_comp'
	else:
		sTargetPath = dailiesDir + '/' + "EDIT"
		sSGInEditFieldName = 'sg_in_edit_anim'

	if not os.path.exists(sTargetPath):
		os.makedirs(sTargetPath)

	for sId_Filter in sa.selected_ids_filter:
		dSGVersion = sg.find_one("Version", [sId_Filter], ['sg_path_to_movie', 'entity'])
		dSGShot = sg.find_one("Shot", [['id', 'is', dSGVersion['entity']['id']]], ['code','sg_projectmanager_id'])


		sTargetName = dSGShot['code'] + ".%04d.jpg"
		sTargetFilename = sTargetPath + '/' + sTargetName
		cmd = "//online1/software/ffmpeg/ffmpeg.exe -i %s -b 30M %s" % (dSGVersion['sg_path_to_movie'], sTargetFilename)
		print(cmd)
		subprocess.call(cmd)

		# Update version 'In Edit ...' flag in Shotgun. Unset flag on older versions in edit.
		lAllVersionsInEdit = sg.find("Version", [['entity', 'is', dSGShot], [sSGInEditFieldName, 'is', True]])
		for dVersion in lAllVersionsInEdit:
			sg.update("Version", dVersion['id'], {sSGInEditFieldName:False})
		sg.update("Version", dSGVersion['id'], {sSGInEditFieldName:True})

		# TEMP code for SEARCH and rescue. We have to make it generic for all projects some time.
		if lArgs[0] == 'CompPlay':
			oPMShot = api.getObjectByUid('Shot', None, dSGShot['sg_projectmanager_id'])
			sShotPath = oPMShot.getAbsPathOnline()
			sEditPath = sShotPath + '/REFERENCES/OFFLINE/SRPIT_%s_Edit_01a.rv' % (oPMShot.getIdentifier())
			cmd = 'C:/oblique/Software/RV/rvlink.bat %s' % (sEditPath)
			subprocess.call(cmd)




	# Continue code

	print "done."






if __name__ == '__main__':
    sys.exit(installMenu())
