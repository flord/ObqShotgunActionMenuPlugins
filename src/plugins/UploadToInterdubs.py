#!python

import sys
import datetime
import os
import subprocess
from fuzzLib.managerClient import Api

# Shotgun API
from shotgun_api3 import Shotgun
SERVER_PATH = "" #your server path here
SCRIPT_USER = 'UploadToInterdubs' #your script name
SCRIPT_KEY =  '' #your key here
sg = Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)

# Interdubs API
from interdubs_api import Interdubs
IDX_PATH = 'http://www.interdubs.com/api/'
IDX_KEY  = 'GA7BzxYKwcBE3dm7CGH9d'
idx = Interdubs(IDX_PATH, IDX_KEY)


# Install menu in Shotgun.
def installMenu():

	data = {
	  "title":"Upload to Interdubs", # Menu name
	  "url": "obq://UploadToInterdubs", #obq://<pluginName>/[<arg1>]/[<arg2>]
	  "list_order": 50, # Menu order
	  "entity_type": "Playlist", # Entity
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
	print("Uploading playlist to INTERDUBS.")

	lSequencesToProcess = []
	for sId_Filter in sa.selected_ids_filter:
		lPlaylists = sg.find("Playlist", [sId_Filter], ['versions', 'code', 'description', 'updated_at'])
		for sgPlaylist in lPlaylists:
			sInterdubsPath = "/" + sa.params['project_name'] + "/" + sgPlaylist['code']
			iInterdubsPathID = idx.chkmkpath(sInterdubsPath)
			if sgPlaylist['description']:
				idx.add_node_note(iInterdubsPathID, sgPlaylist['description'])
			for sgVersion in sgPlaylist['versions']:
				sgVersion = sg.find_one('Version', [['id', 'is', sgVersion['id']]], ['sg_path_to_movie', 'code', 'sg_description_for_client'])
				# check if version exists on Interdubs and skip it.
				if idx.node_exists(os.path.basename(sgVersion['sg_path_to_movie']), iInterdubsPathID):
					print("\n Version %s exists in Interdubs, skipping.\n" % os.path.basename(sgVersion['sg_path_to_movie']))
					continue

				# Recompress
				sFilename = sgVersion['sg_path_to_movie']
				try:
					bzApi = Api(bzhost='projectmanager')
				except:
					raise IOError, "An instance of the ProjectManager API cannot be obtained.\n" \
						  +"This is most probably because there is a problem with the projectmanager machine."\
						  +"(yes there's a machine with that name)"

				oRootProject = bzApi.getProjectFromPath(sFilename).currentRootProject()

				# find the approval directory
				dirnodes = oRootProject.getTemplate().searchNodes(attributes={"path":"CLIENT_APPROVAL"})
				if not dirnodes:
					dirnodes = oRootProject.getTemplate().searchNodes(attributes={"path":"APPROVAL"})
				if len(dirnodes) != 1:
					raise IOError, "Cannot find approval directory in root project"

				# create the approval dir if it doesn't exist
				apprNode = dirnodes[0]
				if not apprNode.exists():
					apprNode.create()
					if not apprNode.exists():
						raise IOError, "Cannot create CLIENT_APPROVAL directory"

				sTargetDir = "%s/%s" % (apprNode.getAbsPathOnline(),datetime.date.today().isoformat())
				if not os.path.exists(sTargetDir):
					os.mkdir(sTargetDir)

				sCompressedFilename = "%s/%s" % (sTargetDir, os.path.basename(sFilename))

				if sFilename.endswith('.mov') or sFilename.endswith('.mp4'):
					# Get info from Project Manager
					dOutRes = oRootProject.getOutputResolution()
					sGoodFrameRate = str(dOutRes['frameRate'])
					iBitRate = 2000 # Kb/s
					sCommand = "//online1/software/ffmpeg/ffmpeg.exe -y -i %s -vcodec libx264 -b %dK -acodec libfaac -ab 128k -threads 0 %s"\
								% (sFilename, iBitRate, sCompressedFilename)

					print("Recompressing movie in H.264 using ffmpeg.")

					oProcess = subprocess.Popen(sCommand,
												shell=True,
												stdin=subprocess.PIPE,
												stdout=subprocess.PIPE,
												stderr=subprocess.PIPE,
												universal_newlines=True)
					sOUT, sERR = oProcess.communicate()
					print(sOUT)
					print(sERR)
					if oProcess.returncode:
						raise IOError, "Error processing with ffmpeg."

					subprocess.call("//online1/software/MP4Box/MP4Box.exe -hint %s" % (sCompressedFilename))

				else:
					print("Copying %s in CLIENT_APPROVAL." %(sFilename))
					shutil.copy(sFilename, sCompressedFilename)


				# Upload Version
				print("\n\nUploading version %s" % (sgVersion['code']))
				note=None
				if sgVersion['sg_description_for_client']:
					idx.uploadfile_into_path(sCompressedFilename , sInterdubsPath, note=sgVersion['sg_description_for_client'])
				else:
					idx.uploadfile_into_path(sCompressedFilename , sInterdubsPath)



	# Continue code

	# In case of error, just raise an exception. It will be trapped in the obqProtocolHandler and the window will stay open for a little while.
	print "done."





if __name__ == '__main__':
    sys.exit(installMenu())
