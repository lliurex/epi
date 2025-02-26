#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys
import pwd

signal.signal(signal.SIGINT, signal.SIG_DFL)

class GatherInfo(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.epiFile=args[0]
		self.noCheck=args[1]
		self.debug=args[2]
		self.app=args[3]
	
	#def __init__
		
	def run(self,*args):
		
		self.ret=Bridge.epiGuiManager.initProcess(self.epiFile,self.noCheck,self.debug,self.app)

	#def run

#class GatherInfo

class UnlockProcess(QThread):

	def __init__(self,*args):

		QThread.__init__(self)

	#def __init__
		
	def run(self,*args):
		
		self.ret=Bridge.epiGuiManager.execUnlockProcess()

	#def run

#def UnlockProcess

class Bridge(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.epiGuiManager=self.core.epiGuiManager
		self._closeGui=False
		self._closePopUp=True
		self._loadMsgCode=Bridge.epiGuiManager.MSG_LOADING_INFO
		self._loadErrorCode=""
		self._localDebError=""
		self._currentStack=0
		self._currentOptionsStack=0
		self._showStatusMessage=[False,"","Ok"]
		self._feedbackCode=""
		self._showRemoveBtn=False
		self._isProcessRunning=False
		self._enableApplyBtn=False
		self._enableRemoveBtn=False
		self._showDialog=False
		self._endProcess=True
		self._endCurrentCommand=False
		self._currentCommand=""
		self._enableKonsole=False
		self._launchedProcess=""
		self._isProgressBarVisible=False
		self._showCloseDialog=False
		self.moveToStack=""
		self.waitMaxRetry=1
		self.waitRetryCount=0
		self._runPkexec=Bridge.epiGuiManager.runPkexec

	#def __init__

	def initBridge(self):

		debug=False
		noCheck=False
		epiFile=""
		app=None
		indexToPop=[]
		
		sys.argv.pop(0)

		for item in range(len(sys.argv)-1,-1,-1):
			if "-d" in sys.argv[item] or "--debug" in sys.argv[item]:
				if '.epi' not in sys.argv[item]:
					debug=True
					indexToPop.append(item)
			if "-nc" in sys.argv[item] or "--no-check" in sys.argv[item]:
				if '.epi' not in sys.argv[item]:
					noCheck=True
					indexToPop.append(item)
			if ".epi" in sys.argv[item]:
				epiFile=sys.argv[item]
				indexToPop.append(item)

		for item in indexToPop:
			sys.argv.pop(item)

		if len(sys.argv)>0:
			app=sys.argv[0]

		if epiFile!=None:
			if epiFile!="error":
				self.gatherInfoT=GatherInfo(epiFile,noCheck,debug,app)
				self.gatherInfoT.start()
				self.gatherInfoT.finished.connect(self._gatherInfoRet)

	#def initBridge

	def _gatherInfoRet(self):

		if 	self.gatherInfoT.ret[0]:
			self._showInfo()
		else:
			if self.gatherInfoT.ret[2]=="End":
				self.loadErrorCode=self.gatherInfoT.ret[1]
				self.currentStack=1
			elif self.gatherInfoT.ret[2]=="LocalDeb":
				self.loadErrorCode=self.gatherInfoT.ret[1]
				self.localDebError=self.gatherInfoT.ret[3]
				self.currentStack=1
			elif self.gatherInfoT.ret[2]=="Wait":
				self.loadMsgCode=Bridge.epiGuiManager.MSG_LOADING_WAIT
				self.waitUnlockTimer=QTimer()
				self.waitUnlockTimer.timeout.connect(self._waitUnlockTimerRet)
				self.waitUnlockTimer.start(5000)
			elif self.gatherInfoT.ret[2]=="Lock":
				self.showDialog=True

	#def _gatherInfoRet

	def _showInfo(self):

		self.core.packageStack.showInfo()
		self.manageRemoveBtn(True)

		if len(Bridge.epiGuiManager.epiManager.packages_selected)>0:
			self.enableApplyBtn=True
		
		if Bridge.epiGuiManager.initialStatusCode[0]!="":
			self.showStatusMessage=[True,Bridge.epiGuiManager.initialStatusCode[0],Bridge.epiGuiManager.initialStatusCode[1]]
		
		self.currentStack=2

	#def _showInfo

	def _waitUnlockTimerRet(self):

		Bridge.epiGuiManager.checkLockInfo()
		ret=Bridge.epiGuiManager.getLockInfo()

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

	#def _waitUnlockTimerRet

	def _getLoadMsgCode(self):

		return self._loadMsgCode

	#def _getLoadMsgCode

	def _setLoadMsgCode(self,loadMsgCode):

		if self._loadMsgCode!=loadMsgCode:
			self._loadMsgCode=loadMsgCode
			self.on_loadMsgCode.emit()

	#def _setLoadMsgCode

	def _getLocalDebError(self):

		return self._localDebError

	#def _getLocalDebError

	def _setLocalDebError(self,localDebError):

		if self._localDebError!=localDebError:
			self._localDebError=localDebError
			self.on_localDebError.emit()

	#def _setLocalDebError

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

	def _getFeedbackCode(self):

		return self._feedbackCode

	#def _getFeedbackCode

	def _setFeedbackCode(self,feedbackCode):

		if self._feedbackCode!=feedbackCode:
			self._feedbackCode=feedbackCode
			self.on_feedbackCode.emit()

	#def _setFeedbackCode

	def _getLoadErrorCode(self):

		return self._loadErrorCode

	#def _getLoadErrorCode

	def _setLoadErrorCode(self,loadErrorCode):

		if self._loadErrorCode!=loadErrorCode:
			self._loadErrorCode=loadErrorCode
			self.on_loadErrorCode.emit()

	#def _setLoadErrorCode

	def _getEnableApplyBtn(self):

		return self._enableApplyBtn

	#def _getEnableApplyBtn

	def _setEnableApplyBtn(self,enableApplyBtn):

		if self._enableApplyBtn!=enableApplyBtn:
			self._enableApplyBtn=enableApplyBtn
			self.on_enableApplyBtn.emit()

	#def _setEnableApplyBtn

	def _getEnableRemoveBtn(self):

		return self._enableRemoveBtn

	#def _getEnableRemoveBtn

	def _setEnableRemoveBtn(self,enableRemoveBtn):

		if self._enableRemoveBtn!=enableRemoveBtn:
			self._enableRemoveBtn=enableRemoveBtn
			self.on_enableRemoveBtn.emit()

	#def _setEnableRemoveBtn

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

	def _getEnableKonsole(self):

		return self._enableKonsole

	#def _getEnableKonsole

	def _setEnableKonsole(self,enableKonsole):

		if self._enableKonsole!=enableKonsole:
			self._enableKonsole=enableKonsole
			self.on_enableKonsole.emit()

	#def _setEnableKonsole

	def _getLaunchedProcess(self):

		return self._launchedProcess

	#def _getLaunchedProcess

	def _setLaunchedProcess(self,launchedProcess):

		if self._launchedProcess!=launchedProcess:
			self._launchedProcess=launchedProcess
			self.on_launchedProcess.emit()

	#def _setLaunchedProcess

	def _getIsProgressBarVisible(self):

		return self._isProgressBarVisible

	#def _getIsProgressBarVisible

	def _setIsProgressBarVisible(self,isProgressBarVisible):

		if self._isProgressBarVisible!=isProgressBarVisible:
			self._isProgressBarVisible=isProgressBarVisible
			self.on_isProgressBarVisible.emit()

	#def _setIsProgressBarVisible

	def _getShowCloseDialog(self):

		return self._showCloseDialog

	#def _getShowCloseDialog

	def _setShowCloseDialog(self,showCloseDialog):

		if self._showCloseDialog!=showCloseDialog:
			self._showCloseDialog=showCloseDialog
			self.on_showCloseDialog.emit()

	#def _setShowCloseDialog

	def _getCloseGui(self):

		return self._closeGui

	#def _getCloseGui	

	def _setCloseGui(self,closeGui):
		
		if self._closeGui!=closeGui:
			self._closeGui=closeGui		
			self.on_closeGui.emit()

	#def _setCloseGui

	def _getRunPkexec(self):

		return self._runPkexec

	#def _getRunPkexec

	@Slot()
	def getNewCommand(self):
		
		self.endCurrentCommand=False
		
	#def getNewCommand

	@Slot()
	def launchUnlockProcess(self):

		self.showDialog=False
		self.loadMsgCode=Bridge.epiGuiManager.MSG_LOADING_UNLOCK
		self.unlockProcessT=UnlockProcess()
		self.unlockProcessT.start()
		self.unlockProcessT.finished.connect(self._unlockProcessRet)

	#def launchUnlockProcess

	def _unlockProcessRet(self):

		if self.unlockProcessT.ret[0]:
			self._showInfo()
		else:
			self.loadErrorCode=self.unlockProcessT.ret[1]
			self.currentStack=1

	#def _unlockProcessT	

	def manageRemoveBtn(self,pkgSelected):

		match=False
		
		if Bridge.epiGuiManager.showRemoveBtn:
			if Bridge.epiGuiManager.pkgsInstalled:
				self.showRemoveBtn=True
			else:
				self.showRemoveBtn=False
		
		for item in Bridge.epiGuiManager.epiManager.packages_selected:
			if item in Bridge.epiGuiManager.pkgsInstalled:
				match=True
				break
		
		if match:
			self.enableRemoveBtn=True
		else:
			self.enableRemoveBtn=False

	#def manageRemoveBtn

	@Slot()
	def launchInstallProcess(self):

		self.showStatusMessage=[False,"","Ok"]
		self.core.packageStack.enablePkgList=False
		self.core.packageStack.filterStatusValue="all"
		self.endProcess=False
		self.enableApplyBtn=False
		if not Bridge.epiGuiManager.noCheck:
			self.isProgressBarVisible=True
			self.feedbackCode=Bridge.epiGuiManager.MSG_FEEDBACK_INTERNET
			self.core.installStack.checkInternetConnection()
		else:
			self.core.packageStack.getEulas()
	
	#def launchInstallProcess

	@Slot()
	def launchUninstallProcess(self):

		self.enableApplyBtn=False
		self.enableRemoveBtn=False
		self.core.packageStack.enablePkgList=False
		self.core.packageStack.filterStatusValue="all"
		self.showStatusMessage=[False,"","Ok"]
		self.endProcess=False
		self.isProgressBarVisible=True
		Bridge.epiGuiManager.totalUninstallError=0
		Bridge.epiGuiManager.totalWarningSkipPkg=0
		Bridge.epiGuiManager.totalWarningSkipMeta=0
		Bridge.epiGuiManager.totalWarningSkipPkg=0
		self.feedbackCode=Bridge.epiGuiManager.MSG_FEEDBACK_UNINSTALL_CHECK
		self.core.uninstallStack.checkMetaProtection()

	#def launchUninstallProcess 

	@Slot(int)
	def manageTransitions(self,stack):

		if self.currentOptionsStack!=stack:
			self.currentOptionsStack=stack

	#de manageTransitions

	@Slot()
	def openHelp(self):

		self.helpCmd='xdg-open %s'%self.core.packageStack.wikiUrl

		if self.runPkexec:
			user=pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
			self.helpCmd="su -c '%s' %s"%(self.helpCmd,user)
		else:
			self.helpCmd="su -c '%s' $USER"%self.helpCmd
		
		self.openHelp_t=threading.Thread(target=self._openHelpRet)
		self.openHelp_t.daemon=True
		self.openHelp_t.start()

	#def openHelp

	def _openHelpRet(self):

		os.system(self.helpCmd)

	#def _openHelpRet

	@Slot()
	def closeApplication(self):

		if self.endProcess:
			Bridge.epiGuiManager.clearEnvironment()
			self.closeGui=True
		else:
			try:
				if os.path.exists(Bridge.epiGuiManager.tokenPostInstall[1]):
					self.showCloseDialog=True
			except:
				pass
			self.closeGui=False

	#def closeApplication

	@Slot()
	def forceClossing(self):

		self.showCloseDialog=False
		self.endProcess=True
		Bridge.epiGuiManager.clearEnvironment(True)
		self.closeGui=True

	#def forceClossing

	@Slot()
	def cancelClossing(self):

		self.showCloseDialog=False

	#def cancelClossing
	
	on_loadMsgCode=Signal()
	loadMsgCode=Property(int,_getLoadMsgCode,_setLoadMsgCode,notify=on_loadMsgCode)
	
	on_currentStack=Signal()
	currentStack=Property(int,_getCurrentStack,_setCurrentStack, notify=on_currentStack)
	
	on_currentOptionsStack=Signal()
	currentOptionsStack=Property(int,_getCurrentOptionsStack,_setCurrentOptionsStack, notify=on_currentOptionsStack)

	on_loadErrorCode=Signal()
	loadErrorCode=Property(int,_getLoadErrorCode,_setLoadErrorCode,notify=on_loadErrorCode)
	
	on_localDebError=Signal()
	localDebError=Property(str,_getLocalDebError,_setLocalDebError,notify=on_localDebError)

	on_feedbackCode=Signal()
	feedbackCode=Property(int,_getFeedbackCode,_setFeedbackCode,notify=on_feedbackCode)

	on_enableApplyBtn=Signal()
	enableApplyBtn=Property(bool,_getEnableApplyBtn,_setEnableApplyBtn,notify=on_enableApplyBtn)

	on_enableRemoveBtn=Signal()
	enableRemoveBtn=Property(bool,_getEnableRemoveBtn,_setEnableRemoveBtn,notify=on_enableRemoveBtn)

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

	on_enableKonsole=Signal()
	enableKonsole=Property(bool,_getEnableKonsole,_setEnableKonsole,notify=on_enableKonsole)

	on_launchedProcess=Signal()
	launchedProcess=Property('QString',_getLaunchedProcess,_setLaunchedProcess,notify=on_launchedProcess)
	
	on_isProgressBarVisible=Signal()
	isProgressBarVisible=Property(bool,_getIsProgressBarVisible,_setIsProgressBarVisible,notify=on_isProgressBarVisible)

	on_showCloseDialog=Signal()
	showCloseDialog=Property(bool,_getShowCloseDialog,_setShowCloseDialog,notify=on_showCloseDialog)

	on_closeGui=Signal()
	closeGui=Property(bool,_getCloseGui,_setCloseGui, notify=on_closeGui)

	runPkexec=Property(bool,_getRunPkexec,constant=True)

#class Bridge

from . import Core

