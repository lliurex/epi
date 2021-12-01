#!/usr/bin/env python3

import sys
import epi.epimanager as EpiManager

from . import IconsManager
from . import MainWindow
from . import ChooserBox
from . import LoadingBox
from . import DependsBox
from . import EpiBox
from . import InfoBox
from . import EulaBox
from . import TerminalBox
from . import settings

class Core:
	
	singleton=None
	DEBUG=False
	
	@classmethod
	def get_core(self):
		
		if Core.singleton==None:
			Core.singleton=Core()
			Core.singleton.init()

		return Core.singleton
		
	
	def __init__(self,args=None):
		
		self.dprint("Init...")
		
	#def __init__
	
	def init(self):

		self.rsrc_dir= settings.RSRC_DIR + "/"
		self.ui_path= settings.RSRC_DIR + "/epi-gtk.ui"
		#self.get_icons=IconsManager.IconsManager()
		debug=False
		noCheck=False
		if len(sys.argv)>2:
			for item in sys.argv:
				if item=="-d" or item=="--debug":
					debug=True
				if item=="-nc" or item=="--no-check":
					noCheck=True

		self.iconsManager=IconsManager.IconsManager()
		self.epiManager=EpiManager.EpiManager(debug)

		self.chooserBox=ChooserBox.ChooserBox()
		self.loadingBox=LoadingBox.LoadingBox()
		self.dependsBox=DependsBox.DependsBox()
		self.epiBox=EpiBox.EpiBox()
		self.infoBox=InfoBox.InfoBox()
		self.eulaBox=EulaBox.EulaBox()
		self.terminalBox=TerminalBox.TerminalBox()
				
			
			# Main window must be the last one
		if len(sys.argv)>1:
			epi_file=sys.argv[1]
		else:
			epi_file=None		
		self.mainWindow=MainWindow.MainWindow(noCheck,epi_file)
			
		self.mainWindow.load_gui()
		self.mainWindow.start_gui()
			
		
		
	#def init
	
	
	
	def dprint(self,msg):
		
		if Core.DEBUG:
			
			print("[CORE] %s"%msg)
	
	#def  dprint
