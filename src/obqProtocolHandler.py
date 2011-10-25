#!python
try:
	import sys
	import cgi
	import os
	import imp
	import types
	import traceback
	import time
	from pprint import pformat, pprint

	if 'useDev' in os.environ:
		PLUGIN_SEARCH_PATH = 'C:/obliqueDev/obqProtocolHandler/src/plugins'
		if 'C:\\oblique\\libs\\python' in sys.path:
			sys.path.remove('C:\\oblique\\libs\\python')
		sys.path.extend(['C:\\obliqueDev\\fuzzLib\\src', 'C:\\oblique\\libs\\python'])
	else:
		PLUGIN_SEARCH_PATH = 'C:/oblique/software/obqProtocolHandler/plugins'
		if not 'C:\\oblique\\libs\\python' in sys.path:
			sys.path.extend(['C:\\oblique\\libs\\python'])
	os.environ['bzApiHost'] = 'projectmanager'

	from shotgun_action import ShotgunAction # from https://support.shotgunsoftware.com/entries/162750-example-handling-shotgunactionmenu-item-calls

	if len(sys.argv) == 1:
		sys.argv.append('obq://CopyForNuke/?user_id=39&user_login=flord&title=Versions&entity_type=Version&project_name=SOURCE_CODE&project_id=84&ids=7754%2C7738%2C7739%2C7740%2C7741%2C7752%2C7742%2C7753%2C7743%2C7744%2C7745%2C7746%2C7749%2C7728%2C7750%2C7747&selected_ids=7754%2C7738%2C7739%2C7740%2C7741%2C7752%2C7742%2C7753%2C7743%2C7744%2C7745%2C7746%2C7749%2C7728%2C7750%2C7747&cols=code&cols=image&cols=sg_qt&cols=entity&cols=user&cols=created_at&cols=description&cols=sg_status_list&cols=sg_client_status&cols=open_notes_count&column_display_names=Version%20Name&column_display_names=Thumbnail&column_display_names=QT&column_display_names=Link&column_display_names=Artist&column_display_names=Date%20Created&column_display_names=Description&column_display_names=Internal%20Status&column_display_names=Client%20Status&column_display_names=Open%20Notes%20Count&sort_column=code&sort_direction=asc&grouping_column=created_at&grouping_method=day&grouping_direction=desc')

except BaseException, ex:
	import time
	print traceback.format_exc(ex)
	time.sleep(10)
	raise

# Declare Module class, our plugin structure.
class Module(object):
	def __init__(self, path, args):
		self._moduleName = None
		self._path = path
		self._args = args
		self.load()

	def load(self):
		_, basename = os.path.split(self._path)
		self._moduleName = os.path.splitext(basename)[0]

		self._load(self._moduleName, 'Loading module at %s' % self._path)

	def _load(self, moduleName, message):
		print(message)
		self._callbacks = []

		module = imp.load_source(moduleName, self._path)

		pluginFunc = getattr(module, 'pluginExecute', None)
		if not isinstance(pluginFunc, types.FunctionType):
			raise AttributeError, 'Did not find a pluginExecute() function in module at %s.' % (self._path)

		self.pluginExecute = module.pluginExecute

	def __str__(self):
		return self._moduleName

def main():
	try:
		## Decode URL and reformat data to be easily ingestible by plugins
		sa = ShotgunAction(sys.argv[1])
		sPluginArgs = sa.action
		sPluginName = sPluginArgs.split('/', 1)[0] # First arg is the name of the plugin we will launch.
		lPluginArgs = sPluginArgs.split('/')[1:] # We pass the other args to the plugin.

		#####
		# Plugin load and execute
		#####

		sPluginPath = PLUGIN_SEARCH_PATH + '/' + sPluginName + '.py'
		module = Module(sPluginPath, lPluginArgs)
		module.pluginExecute(lPluginArgs, sa)

	except BaseException, ex:
		print traceback.format_exc(ex)
		time.sleep(10)
		raise

if __name__ == '__main__':
    main()
