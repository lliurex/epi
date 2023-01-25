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

class UnlockProcess(QThread):

	def __init__(self,*args):

		QThread.__init__(self)

	#def __init__
		
	def run(self,*args):
		
		self.ret=EpiGui.epiGuiManager.execUnlockProcess()

	#def run

#def UnlockProcess

class EpiGui(QObject):

	epiGuiManager=EpiGuiManager.EpiGuiManager()
	MSG_LOADING_INFO=0
	MSG_LOADING_WAIT=1
	MSG_LOADING_UNLOCK=2

	def __init__(self):

		QObject.__init__(self)
		self.initBridge()

	#def __init__

	def initBridge(self):

		self._packagesModel=PackagesModel.PackagesModel()
		self._closeGui=False
		self._closePopUp=True
		self._loadMsgCode=EpiGui.MSG_LOADING_INFO
		self._loadErrorCode=""
		self._showStatusMessage=[False,"","Success"]
		self._currentStack=0
		self._currentOptionsStack=0
		self._currentPkgOption=0
		self._uncheckAll=True
		self._selectPkg=False
		self._showRemoveBtn=False
		self._isProcessRunning=False
		self._enableActionBtn=False
		self._showDialog=False
		self._endProcess=True
		self._endCurrentCommand=False
		self._currentCommand=""
		self.moveToStack=""
		self.waitMaxRetry=1
		self.waitRetryCount=0
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
			self._showInfo()
		else:
			if self.gatherInfo.ret[2]=="End":
				self.loadErrorCode=self.gatherInfo.ret[1]
				self.currentStack=1
			elif self.gatherInfo.ret[2]=="Wait":
				self.loadMsgCode=EpiGui.MSG_LOADING_WAIT
				self.waitUnlockTimer=QTimer()
				self.waitUnlockTimer.timeout.connect(self._getLockInfo)
				self.waitUnlockTimer.start(5000)
			elif self.gatherInfo.ret[2]=="Lock":
				self.showDialog=True

	#def _loadInfo

	def _showInfo(self):

		self._updatePackagesModel()
		self.uncheckAll=EpiGui.epiGuiManager.uncheckAll
		self.selectPkg=EpiGui.epiGuiManager.selectPkg
		self.showRemoveBtn=EpiGui.epiGuiManager.showRemoveBtn
		if len(EpiGui.epiGuiManager.epiManager.packages_selected)>0:
			self.enableActionBtn=True
		self.currentStack=2

	#def _showInfo

	def _getLockInfo(self):

		EpiGui.epiGuiManager.checkLockInfo()
		ret=EpiGui.epiGuiManager.getLockInfo()

		if self.waitRetryCount<self.waitMaxRetry:
			if not ret[0]:
				self.waitRetryCount+=1
			else:
				self.waitUnlockTimer.stop()
				self._showInfo()
		else:
			self.waitUnlockTimer.stop()
			if ret[0]:
				self._showInfo()
			else:
				self.loadErrorCode=ret[1]
				self.currentStack=1

	#def _getLockInfo

	def _getLoadMsgCode(self):

		return self._loadMsgCode

	#def _getLoadMsgCode

	def _setLoadMsgCode(self,loadMsgCode):

		if self._loadMsgCode!=loadMsgCode:
			self._loadMsgCode=loadMsgCode
			self.on_loadMsgCode.emit()

	#def _setLoadMsgCode

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

	def _getCurrentPkgOption(self):

		return self._currentPkgOption

	#def _getCurrentPkgOption

	def _setCurrentPkgOption(self,currentPkgOption):

		if self._currentPkgOption!=currentPkgOption:
			self._currentPkgOption=currentPkgOption
			self.on_currentPkgOption.emit()

	#def _setCurrentPkgOption

	def _getLoadErrorCode(self):

		return self._loadErrorCode

	#def _getLoadErrorCode

	def _setLoadErrorCode(self,loadErrorCode):

		if self._loadErrorCode!=loadErrorCode:
			self._loadErrorCode=loadErrorCode
			self.on_loadErrorCode.emit()

	#def _setLoadErrorCode

	def _getUncheckAll(self):

		return self._uncheckAll

	#def _getUncheckAll

	def _setUncheckAll(self,uncheckAll):

		if self._uncheckAll!=uncheckAll:
			self._uncheckAll=uncheckAll
			self.on_uncheckAll.emit()

	#def _setUncheckAll 

	def _getSelectPkg(self):

		return self._selectPkg

	#def _getSelectPkg

	def _setSelectPkg(self,selectPkg):

		if self._selectPkg!=selectPkg:
			self._selectPkg=selectPkg
			self.on_selectPkg.emit()

	#def _setSelectPkg 

	def _getEnableActionBtn(self):

		return self._enableActionBtn

	#def _getEnableActionBtn

	def _setEnableActionBtn(self,enableActionBtn):

		if self._enableActionBtn!=enableActionBtn:
			self._enableActionBtn=enableActionBtn
			self.on_enableActionBtn.emit()

	#def _setEnableActionBtn

	def _getShowRemoveBtn(self):

		return self._showRemoveBtn

	#def _getShowRemoveBtn

	def _setShowRemoveBtn(self,showRemoveBtn):

		if self._showRemoveBtn!=showRemoveBtn:
			self._showRemoveBtn=showRemoveBtn
			self.on_showRemoveBtn.emit()

	#def _setShowRemoveBtn

	def _getIsProcessRunning(self):

		return self._isProcessRunning

	#def _getIsProcessRunning

	def _setIsProcessRunning(self, isProcessRunning):

		if self._isProcessRunning!=isProcessRunning:
			self._isProcessRunning=isProcessRunning
			self.on_isProcessRunning.emit()

	#def _setIsProcessRunning

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

	@Slot()
	def launchUnlockProcess(self):

		self.showDialog=False
		self.loadMsgCode=EpiGui.MSG_LOADING_UNLOCK
		self.unlockProcessT=UnlockProcess()
		self.unlockProcessT.start()
		self.unlockProcessT.finished.connect(self._unlockProcessT)

	#def launchUnlockProcess

	def _unlockProcessT(self):

		if self.unlockProcessT.ret[0]:
			self._showInfo()
		else:
			self.loadErrorCode=self.unlockProcessT.ret[1]
			self.currentStack=1

	#def _unlockProcessT	

	@Slot(int)
	def manageTransitions(self,stack):

		if self.currentOptionsStack!=stack:
			self.currentOptionsStack=stack
			self.moveToStack=""
	
	#def manageTransitions

	@Slot('QVariantList')
	def onCheckPkg(self,info):

		EpiGui.epiGuiManager.onCheckedPackages(info[0],info[1])
		self._refreshInfo()

	#def onCheckPkg

	@Slot()
	def selectAll(self):

		EpiGui.epiGuiManager.selectAll()
		self._refreshInfo()
		
	#def selectAll

	def _refreshInfo(self):

		self._updatePackagesModelInfo("isChecked")
		self.uncheckAll=EpiGui.epiGuiManager.uncheckAll
		if len(EpiGui.epiGuiManager.epiManager.packages_selected)>0:
			self.enableActionBtn=True
		else:
			self.enableActionBtn=False

	#def _refreshInfo

	@Slot()
	def installPkg(self):

		self.isProcessRunning=True
		if EpiGui.epiGuiManager.noCheck:
			EpiGui.epiGuiManager.checkInternetConnection()
			self.checkConnectionTimer=QTimer()
			self.checkConnectionTimer.timeout.connect(self._checkConnectionInfo)
			self.checkConnectionTimer.start(1000)
	
	#def installPkg

	def _checkConnectionInfo(self):

		if EpiGui.epiGuiManager.endCheck:
			self.checkConnectionTimer.stop()
			if not EpiGui.epiGuiManager.retConnection[0]:

	#def _checkConnectionInfo

	@Slot()
	def uninstallPkg(self):

		if not self.isProcessRunning:
			self.isProcessRunning=True
		else:
			self.isProcessRunning=False

	#def uninstallPkg

	def _updatePackagesModelInfo(self,param):

		updatedInfo=EpiGui.epiGuiManager.packagesData

		if len(updatedInfo)>0:
			for i in range(len(updatedInfo)):
				index=self._packagesModel.index(i)
				self._packagesModel.setData(index,param,updatedInfo[i][param])
	
	#def _updatePackagesModelInfo

	@Slot()
	def closeApplication(self):

		self.closeGui=True

	#def closeApplication
	
	on_loadMsgCode=Signal()
	loadMsgCode=Property(int,_getLoadMsgCode,_setLoadMsgCode,notify=on_loadMsgCode)
	
	on_currentStack=Signal()
	currentStack=Property(int,_getCurrentStack,_setCurrentStack, notify=on_currentStack)
	
	on_currentOptionsStack=Signal()
	currentOptionsStack=Property(int,_getCurrentOptionsStack,_setCurrentOptionsStack, notify=on_currentOptionsStack)

	on_currentPkgOption=Signal()
	currentPkgOption=Property(int,_getCurrentPkgOption,_setCurrentPkgOption,notify=on_currentPkgOption)
	
	on_loadErrorCode=Signal()
	loadErrorCode=Property(int,_getLoadErrorCode,_setLoadErrorCode,notify=on_loadErrorCode)
	
	on_uncheckAll=Signal()
	uncheckAll=Property(bool,_getUncheckAll,_setUncheckAll,notify=on_uncheckAll)

	on_selectPkg=Signal()
	selectPkg=Property(bool,_getSelectPkg,_setSelectPkg,notify=on_selectPkg)

	on_enableActionBtn=Signal()
	enableActionBtn=Property(bool,_getEnableActionBtn,_setEnableActionBtn,notify=on_enableActionBtn)

	on_showRemoveBtn=Signal()
	showRemoveBtn=Property(bool,_getShowRemoveBtn,_setShowRemoveBtn,notify=on_showRemoveBtn)

	on_isProcessRunning=Signal()
	isProcessRunning=Property(bool,_getIsProcessRunning,_setIsProcessRunning,notify=on_isProcessRunning)

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

