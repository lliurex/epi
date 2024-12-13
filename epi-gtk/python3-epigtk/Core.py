#!/usr/bin/env python3

import sys

from . import EpiGuiManager
from . import UninstallStack
from . import InstallStack
from . import PackageStack
from . import MainStack

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

	
		self.epiGuiManager=EpiGuiManager.EpiGuiManager()
		self.uninstallStack=UninstallStack.UninstallStack()
		self.installStack=InstallStack.InstallStack()
		self.packageStack=PackageStack.Bridge()
		self.mainStack=MainStack.Bridge()
		
		self.mainStack.initBridge()
	
		
	#def init

	def dprint(self,msg):
		
		if Core.DEBUG:
			
			print("[CORE] %s"%msg)
	
	#def  dprint
