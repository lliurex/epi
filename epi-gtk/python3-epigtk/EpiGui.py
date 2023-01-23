#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys

from . import EpiGuiManager
from . import PackagesModel

signal.signal(signal.SIGINT, signal.SIG_DFL)

class GatherInfo(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.epiFile=args[0]
		self.noCheck=args[1]
		self.debug=args[2]
	
	#def __init__
		
	def run(self,*args):
		
		self.ret=EpiGui.epiGuiManager.initProcess(self.epiFile,self.noCheck,self.debug)

	#def run

#class GatherInfo

class EpiGui(QObject):

	epiGuiManager=EpiGuiManager.EpiGuiManager()

	def __init__(self):

		QObject.__init__(self)
		self.initBridge()

	#def __init__

	def initBridge(self):

		self._packagesModel=PackagesModel.PackagesModel()
		self._closeGui=False
		self._closePopUp=True
		self._loadErrorCode=""
		self._showStatusMessage=[True,"","Success"]
		self._currentStack=0
		self._currentOptionsStack=0
		self._showDialog=False
		self._endProcess=True
		self._endCurrentCommand=False
		self._currentCommand=""
		self.moveToStack=""
		debug=False
		noCheck=False
		epiFile=""

		for item in sys.argv:
			if item=="-d" or item=="--debug":
				debug=True
			if item=="-nc" or item=="--no-check":
				noCheck=True
			if ".epi" in item:
				epiFile=item

		if epiFile!=None:
			if epiFile!="error":
				self.gatherInfo=GatherInfo(epiFile,noCheck,debug)
				self.gatherInfo.start()
				self.gatherInfo.finished.connect(self._loadInfo)

	#def initBridge

	def _loadInfo(self):

		if 	self.gatherInfo.ret[0]:
			self._updatePackagesModel()
			self.currentStack=2
		else:
			self.loadErrorCode=self.gatherInfo.ret[1]
			self.currentStack=1

	#def _loadInfo

	#def _loadConfig

	def _getCurrentStack(self):

		return self._currentStack

	#def _getCurrentStack

	def _setCurrentStack(self,currentStack):

		if self._currentStack!=currentStack:
			self._currentStack=currentStack
			self.on_currentStack.emit()

	#def _setCurrentStack

	def _getCurrentOptionsStack(self):

		return self._currentOptionsStack

	#def _getCurrentOptionsStack

	def _setCurrentOptionsStack(self,currentOptionsStack):

		if self._currentOptionsStack!=currentOptionsStack:
			self._currentOptionsStack=currentOptionsStack
			self.on_currentOptionsStack.emit()

	#def _setCurrentOptionsStack

	def _getLoadErrorCode(self):

		return self._loadErrorCode

	#def _getLoadErrorCode

	def _setLoadErrorCode(self,loadErrorCode):

		if self._loadErrorCode!=loadErrorCode:
			self._loadErrorCode=loadErrorCode
			self.on_loadErrorCode.emit()

	#def _setLoadErrorCode

	def _getPackagesModel(self):

		return self._packagesModel

	#def _getPackagesModel

	def _updatePackagesModel(self):

		ret=self._packagesModel.clear()
		packagesEntries=EpiGui.epiGuiManager.packagesData
		for item in packagesEntries:
			if item["pkgId"]!="":
				self._packagesModel.appendRow(item["pkgId"],item["showCb"],item["isChecked"],item["customName"],item["pkgIcon"],item["status"],item["isVisible"],item["isRunning"],item["resultProcess"],item["order"])

	#def _updatePackagesModel

	def _getShowStatusMessage(self):

		return self._showStatusMessage

	#def _getShowStatusMessage

	def _setShowStatusMessage(self,showStatusMessage):

		if self._showStatusMessage!=showStatusMessage:
			self._showStatusMessage=showStatusMessage
			self.on_showStatusMessage.emit()

	#def _setShowStatusMessage

	def _getShowDialog(self):

		return self._showDialog

	#def _getShowDialog

	def _setShowDialog(self,showDialog):

		if self._showDialog!=showDialog:
			self._showDialog=showDialog
			self.on_showDialog.emit()
	
	#def _setShowDialog

	def _getEndProcess(self):

		return self._endProcess

	#def _getEndProcess	

	def _setEndProcess(self,endProcess):
		
		if self._endProcess!=endProcess:
			self._endProcess=endProcess		
			self.on_endProcess.emit()

	#def _setEndProcess

	def _getEndCurrentCommand(self):

		return self._endCurrentCommand

	#def _getEndCurrentCommand

	def _setEndCurrentCommand(self,endCurrentCommand):
		
		if self._endCurrentCommand!=endCurrentCommand:
			self._endCurrentCommand=endCurrentCommand		
			self.on_endCurrentCommand.emit()

	#def _setEndCurrentCommand

	def _getCurrentCommand(self):

		return self._currentCommand

	#def _getCurrentCommand

	def _setCurrentCommand(self,currentCommand):
		
		if self._currentCommand!=currentCommand:
			self._currentCommand=currentCommand		
			self.on_currentCommand.emit()

	#def _setCurrentCommand

	def _getCloseGui(self):

		return self._closeGui

	#def _getCloseGui	

	def _setCloseGui(self,closeGui):
		
		if self._closeGui!=closeGui:
			self._closeGui=closeGui		
			self.on_closeGui.emit()

	#def _setCloseGui	

	@Slot(int)
	def manageTransitions(self,stack):

		if self.currentOptionsStack!=stack:
			self.currentOptionsStack=stack
			self.moveToStack=""
	
	#def manageTransitions

	@Slot()
	def closeApplication(self):

		self.closeGui=True

	#def closeApplication
	
	on_currentStack=Signal()
	currentStack=Property(int,_getCurrentStack,_setCurrentStack, notify=on_currentStack)
	
	on_currentOptionsStack=Signal()
	currentOptionsStack=Property(int,_getCurrentOptionsStack,_setCurrentOptionsStack, notify=on_currentOptionsStack)

	on_loadErrorCode=Signal()
	loadErrorCode=Property(int,_getLoadErrorCode,_setLoadErrorCode,notify=on_loadErrorCode)
	
	on_showStatusMessage=Signal()
	showStatusMessage=Property('QVariantList',_getShowStatusMessage,_setShowStatusMessage,notify=on_showStatusMessage)

	on_showDialog=Signal()
	showDialog=Property(bool,_getShowDialog,_setShowDialog,notify=on_showDialog)
	
	on_endProcess=Signal()
	endProcess=Property(bool,_getEndProcess,_setEndProcess, notify=on_endProcess)

	on_endCurrentCommand=Signal()
	endCurrentCommand=Property(bool,_getEndCurrentCommand,_setEndCurrentCommand, notify=on_endCurrentCommand)

	on_currentCommand=Signal()
	currentCommand=Property('QString',_getCurrentCommand,_setCurrentCommand, notify=on_currentCommand)

	on_closeGui=Signal()
	closeGui=Property(bool,_getCloseGui,_setCloseGui, notify=on_closeGui)

	packagesModel=Property(QObject,_getPackagesModel,constant=True)

#class EpiGui

