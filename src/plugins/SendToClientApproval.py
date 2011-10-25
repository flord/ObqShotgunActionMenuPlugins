#!python

import sys
import win32clipboard
import os,time,shutil,datetime,subprocess
from fuzzLib.managerClient import Api
from shotgun_api3 import Shotgun
SERVER_PATH = "https://oblique.shotgunstudio.com" #your server path here
SCRIPT_USER = 'SendToClientApproval' #your script name
SCRIPT_KEY =  'ea59d098a178ff230640b2d8710ef179757fff85' #your key here
sg = Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)

# Install menu in Shotgun.
def installMenu():
	data = {
	  "title":"Send to CLIENT_APPROVAL (as-is)", # Menu name
	  "url": "obq://SendToClientApproval/as-is", #obq://<pluginName>/[<arg1>]/[<arg2>]
	  "list_order": 60, # Menu order
	  "entity_type": "Version", # Entity
	  "selection_required": True, # will create problems on pages with lots of entities when set to False.
	}
	#Create the menu item
	menu_item = sg.create("ActionMenuItem", data)

	data = {
	  "title":"Send to CLIENT_APPROVAL (recompress)", # Menu name
	  "url": "obq://SendToClientApproval/recompress", #obq://<pluginName>/[<arg1>]/[<arg2>]
	  "list_order": 65, # Menu order
	  "entity_type": "Version", # Entity
	  "selection_required": True, # will create problems on pages with lots of entities when set to False.
	}
	#Create the menu item
	menu_item = sg.create("ActionMenuItem", data)


# Define execution function.
def pluginExecute(lArgs, sa):
	print("Sending Versions to CLIENT_APPROVAL")

	lSequencesToProcess = []
	for sId_Filter in sa.selected_ids_filter:
		sgVersion = sg.find_one("Version", [sId_Filter], ['sg_path_to_movie', 'sg_first_frame', 'sg_last_frame'])
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

		sTargetFilename = "%s/%s" % (sTargetDir, os.path.basename(sFilename))

		if lArgs[0] == 'recompress' and (sFilename.endswith('.mov') or sFilename.endswith('.mp4')):
			# Get info from Project Manager
			dOutRes = oRootProject.getOutputResolution()
			sGoodFrameRate = str(dOutRes['frameRate'])
			iBitRate = 2000 # Kb/s
			sCommand = "//online1/software/ffmpeg/ffmpeg.exe -y -i %s -vcodec libx264 -b %dK -acodec libfaac -ab 128k -threads 0 %s"\
						% (sFilename, iBitRate, sTargetFilename)

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

			subprocess.call("//online1/software/MP4Box/MP4Box.exe -hint %s" % (sTargetFilename))

		else:
			print("Copying %s in CLIENT_APPROVAL." %(sFilename))
			shutil.copy(sFilename, sTargetFilename)

	print "done."


	#dir(sa):
	# 'action',
	# 'column_display_names',  # Internal column names currently displayed on the page
	# 'columns',               # Human readable names of the columns currently displayed on the page
	# 'entity_type',           # entity type that the page was displaying
	# 'ids',                   # All ids of the entities returned by the query (not just those visible on the page)
	# 'ids_filter',            # All ids of the entities returned by the query in filter format ready to use in a find() query
	# 'params',                # contains the dict will all the values
	# 'project',               # Project info (if the ActionMenuItem was launched from a page not belonging to a Project (Global Page, My Page, etc.), this will be blank
	# 'protocol',
	# 'selected_ids',          # ids of entities that were currently selected
	# 'selected_ids_filter',   # All selected ids of the entities returned by the query in filter format ready to use in a find() query
	# 'title',                 # title of the page
	# 'url',                   # The original URL passed to the script.
	# 'user'                   # user info who launched the ActionMenuItem
	#
	#sa.params:
	#{'cols': ['code',
	#		  'image',
	#		  'sg_qt],
	# 'column_display_names': ['Version Name',
	#						  'Thumbnail',
	#						  'QT'],
	# 'entity_type': 'Version',
	# 'grouping_column': 'created_at',
	# 'grouping_direction': 'desc',
	# 'grouping_method': 'day',
	# 'ids': '7754,7738,7739,7740,7741,7752,7742,7753,7743,7744,7745,7746,7749,7728,7750,7747',
	# 'project_id': '84',
	# 'project_name': 'SOURCE_CODE',
	# 'selected_ids': '7754,7738,7739,7740,7741,7752,7742,7753,7743,7744,7745,7746,7749,7728,7750,7747',
	# 'sort_column': 'code',
	# 'sort_direction': 'asc',
	# 'title': 'Versions',
	# 'user_id': '39',
	# 'user_login': 'flord'}



if __name__ == '__main__':
    sys.exit(installMenu())
