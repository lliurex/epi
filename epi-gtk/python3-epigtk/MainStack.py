#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import subprocess
import threading
import signal
import copy
import time
import sys
import pwd

signal.signal(signal.SIGINT, signal.SIG_DFL)

class GatherInfo(QThread):

	infoGathered=Signal('QVariant')

	def __init__(self,manager,epiFile,noCheck,debug,app):

		super().__init__()
		self.manager=manager
		self.epiFile=epiFile
		self.noCheck=noCheck
		self.debug=debug
		self.app=app
	
	#def __init__
		
	def run(self,*args):
		
		ret=self.manager.initProcess(self.epiFile,self.noCheck,self.debug,self.app)
		self.infoGathered.emit(ret)
	
	#def run

#class GatherInfo

class UnlockProcess(QThread):

	processUnlocked=Signal('QVariant')

	def __init__(self,manager):

		super().__init__()
		self.manager=manager

	#def __init__
		
	def run(self,*args):
		
		ret=self.manager.execUnlockProcess()
		self.processUnlocked.emit(ret)

	#def run

#def UnlockProcess

class Bridge(QObject):

	loadMsgCodeChanged=Signal()
	currentStackChanged=Signal()
	currentOptionsStackChanged=Signal()
	loadErrorCodeChanged=Signal()
	additionalErrorInfoChanged=Signal()
	feedbackCodeChanged=Signal()
	enableApplyBtnChanged=Signal()
	enableRemoveBtnChanged=Signal()
	showRemoveBtnChanged=Signal()
	isProcessRunningChanged=Signal()
	showStatusMessageChanged=Signal()
	showDialogChanged=Signal()
	endProcessChanged=Signal()
	endCurrentCommandChanged=Signal()
	currentCommandChanged=Signal()
	enableKonsoleChanged=Signal()
	launchedProcessChanged=Signal()
	isProgressBarVisibleChanged=Signal()
	showCloseDialogChanged=Signal()
	closeGuiChanged=Signal()

	def __init__(self):

		super().__init__()
		self.core=Core.Core.get_core()
		self.epiGuiManager=self.core.epiGuiManager
		self._closeGui=False
		self._closePopUp=True
		self._loadMsgCode=self.epiGuiManager.MSG_LOADING_INFO
		self._loadErrorCode=""
		self._additionalErrorInfo=""
		self._currentStack=0
		self._currentOptionsStack=0
		self._showStatusMessage={"show":False,"msgCode":'',"type":''}
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

	#def __init__

	@Property(int,notify=loadMsgCodeChanged)
	def loadMsgCode(self):

		return self._loadMsgCode

	#def loadMsgCode	

	@loadMsgCode.setter
	def loadMsgCode(self,loadMsgCode):
		
		if self._loadMsgCode!=loadMsgCode:
			self._loadMsgCode=loadMsgCode
			self.loadMsgCodeChanged.emit()

	#def loadMsgCode

	@Property(int,notify=currentStackChanged)
	def currentStack(self):

		return self._currentStack

	#def currentStack	

	@currentStack.setter
	def currentStack(self,currentStack):
		
		if self._currentStack!=currentStack:
			self._currentStack=currentStack
			self.currentStackChanged.emit()

	#def currentStack
	
	@Property(int,notify=currentOptionsStackChanged)
	def currentOptionsStack(self):

		return self._currentOptionsStack

	#def currentOptionsStack

	@currentOptionsStack.setter
	def currentOptionsStack(self,currentOptionsStack):

		if self._currentOptionsStack!=currentOptionsStack:
			self._currentOptionsStack=currentOptionsStack
			self.currentOptionsStackChanged.emit()

	#def currentOptionsStack

	@Property(int,notify=loadErrorCodeChanged)
	def loadErrorCode(self):

		return self._loadErrorCode

	#def loadErrorCode

	@loadErrorCode.setter
	def loadErrorCode(self,loadErrorCode):

		if self._loadErrorCode!=loadErrorCode:
			self._loadErrorCode=loadErrorCode
			self.loadMsgCodeChanged.emit()

	#def loadErrorCode

	@Property(str,notify=additionalErrorInfoChanged)
	def additionalErrorInfo(self):

		return self._additionalErrorInfo

	#def additionalErrorInfo

	@additionalErrorInfo.setter
	def additionalErrorInfo(self,additionalErrorInfo):

		if self._additionalErrorInfo!=additionalErrorInfo:
			self._additionalErrorInfo=additionalErrorInfo
			self.additionalErrorInfoChanged.emit()

	#def additionalErrorInfo

	@Property(int,notify=feedbackCodeChanged)
	def feedbackCode(self):

		return self._feedbackCode

	#def feedbackCode

	@feedbackCode.setter
	def feedbackCode(self,feedbackCode):

		if self._feedbackCode!=feedbackCode:
			self._feedbackCode=feedbackCode
			self.feedbackCodeChanged.emit()

	#def feedbackCode

	@Property(bool,notify=enableApplyBtnChanged)
	def enableApplyBtn(self):

		return self._enableApplyBtn

	#def enableApplyBtn

	@enableApplyBtn.setter
	def enableApplyBtn(self,enableApplyBtn):

		if self._enableApplyBtn!=enableApplyBtn:
			self._enableApplyBtn=enableApplyBtn
			self.enableApplyBtnChanged.emit()

	#def enableApplyBtn

	@Property(bool,notify=enableRemoveBtnChanged)
	def enableRemoveBtn(self):

		return self._enableRemoveBtn

	#def enableRemoveBtn

	@enableRemoveBtn.setter
	def enableRemoveBtn(self,enableRemoveBtn):

		if self._enableRemoveBtn!=enableRemoveBtn:
			self._enableRemoveBtn=enableRemoveBtn
			self.enableRemoveBtnChanged.emit()

	#def enableRemoveBtn

	@Property(bool,notify=showRemoveBtnChanged)
	def showRemoveBtn(self):

		return self._showRemoveBtn

	#def showRemoveBtn

	@showRemoveBtn.setter
	def showRemoveBtn(self,showRemoveBtn):

		if self._showRemoveBtn!=showRemoveBtn:
			self._showRemoveBtn=showRemoveBtn
			self.showRemoveBtnChanged.emit()

	#def showRemoveBtn

	@Property(bool,notify=isProcessRunningChanged)
	def isProcessRunning(self):

		return self._isProcessRunning

	#def isProcessRunning

	@isProcessRunning.setter
	def isProcessRunning(self, isProcessRunning):

		if self._isProcessRunning!=isProcessRunning:
			self._isProcessRunning=isProcessRunning
			self.isProcessRunningChanged.emit()

	#def isProcessRunning

	@Property('QVariant',notify=showStatusMessageChanged)
	def showStatusMessage(self):

		return self._showStatusMessage

	#def showStatusMessage

	@showStatusMessage.setter
	def showStatusMessage(self,showStatusMessage):

		if self._showStatusMessage!=showStatusMessage:
			self._showStatusMessage=showStatusMessage
			self.showStatusMessageChanged.emit()

	#def showStatusMessage

	@Property(bool,notify=showDialogChanged)
	def showDialog(self):

		return self._showDialog

	#def showDialog

	@showDialog.setter
	def showDialog(self,showDialog):

		if self._showDialog!=showDialog:
			self._showDialog=showDialog
			self.showDialogChanged.emit()
	
	#def showDialog

	@Property(bool,notify=endProcessChanged)
	def endProcess(self):

		return self._endProcess

	#def endProcess	

	@endProcess.setter
	def endProcess(self,endProcess):
		
		if self._endProcess!=endProcess:
			self._endProcess=endProcess		
			self.endProcessChanged.emit()

	#def endProcess

	@Property(bool,notify=endCurrentCommandChanged)
	def endCurrentCommand(self):

		return self._endCurrentCommand

	#def endCurrentCommand

	@endCurrentCommand.setter
	def endCurrentCommand(self,endCurrentCommand):
		
		if self._endCurrentCommand!=endCurrentCommand:
			self._endCurrentCommand=endCurrentCommand		
			self.endCurrentCommandChanged.emit()

	#def endCurrentCommand

	@Property('QString',notify=currentCommandChanged)
	def currentCommand(self):

		return self._currentCommand

	#def currentCommand

	@currentCommand.setter
	def currentCommand(self,currentCommand):
		
		if self._currentCommand!=currentCommand:
			self._currentCommand=currentCommand		
			self.currentCommandChanged.emit()

	#def currentCommand

	@Property(bool,notify=enableKonsoleChanged)
	def enableKonsole(self):

		return self._enableKonsole

	#def enableKonsole

	@enableKonsole.setter
	def enableKonsole(self,enableKonsole):

		if self._enableKonsole!=enableKonsole:
			self._enableKonsole=enableKonsole
			self.enableKonsoleChanged.emit()

	#def enableKonsole

	@Property('QString',notify=launchedProcessChanged)
	def launchedProcess(self):

		return self._launchedProcess

	#def launchedProcess

	@launchedProcess.setter
	def launchedProcess(self,launchedProcess):

		if self._launchedProcess!=launchedProcess:
			self._launchedProcess=launchedProcess
			self.launchedProcessChanged.emit()

	#def launchedProcess

	@Property(bool,notify=isProgressBarVisibleChanged)
	def isProgressBarVisible(self):

		return self._isProgressBarVisible

	#def isProgressBarVisible

	@isProgressBarVisible.setter
	def isProgressBarVisible(self,isProgressBarVisible):

		if self._isProgressBarVisible!=isProgressBarVisible:
			self._isProgressBarVisible=isProgressBarVisible
			self.isProgressBarVisibleChanged.emit()

	#def isProgressBarVisible

	@Property(bool,notify=showCloseDialogChanged)
	def showCloseDialog(self):

		return self._showCloseDialog

	#def showCloseDialog

	@showCloseDialog.setter
	def showCloseDialog(self,showCloseDialog):

		if self._showCloseDialog!=showCloseDialog:
			self._showCloseDialog=showCloseDialog
			self.showCloseDialogChanged.emit()

	#def showCloseDialog

	@Property(bool,notify=closeGuiChanged)
	def closeGui(self):

		return self._closeGui

	#def closeGui	

	@closeGui.setter
	def closeGui(self,closeGui):
		
		if self._closeGui!=closeGui:
			self._closeGui=closeGui		
			self.closeGuiChanged.emit()

	#def closeGui

	def initBridge(self):

		debug=False
		noCheck=False
		epiFile=""
		app=None

		argsList=sys.argv[1:]
		remainingArgs=[]
		
		for item in argsList:
			if "-d" in item or "--debug" in item:
				if '.epi' not in item:
					debug=True
					continue
			if "-nc" in item or "--no-check" in item:
				if '.epi' not in item:
					noCheck=True
					continue
			if "-u" in item or "--unattended" in item:
				if '.epi' not in item:
					continue
			if ".epi" in item:
				epiFile=item
				continue

			remainingArgs.append(item)

		if len(remainingArgs)>0:
			app=remainingArgs[0]

		if epiFile and epiFile!="error":
			self.gatherInfoT=GatherInfo(self.epiGuiManager,epiFile,noCheck,debug,app)
			self.gatherInfoT.start()
			self.gatherInfoT.infoGathered.connect(self._gatherInfoRet)
			self.gatherInfoT.finished.connect(self.gatherInfoT.deleteLater)

	#def initBridge

	@Slot('QVariant')
	def _gatherInfoRet(self,ret):

		if 	ret.get("status"):
			self._showInfo()
		else:
			if ret.get("type")=="End":
				self.loadErrorCode=ret.get("msgCode")
				self.currentStack=1
			elif ret.get("type")=="LocalDeb" or ret.get("type")=="Depends":
				self.loadErrorCode=ret.get("msgCode")
				self.additionalErrorInfo=ret.get("data")
				self.currentStack=1
			elif ret.get("type")=="Wait":
				self.loadMsgCode=self.epiGuiManager.MSG_LOADING_WAIT
				self.waitUnlockTimer=QTimer()
				self.waitUnlockTimer.timeout.connect(self._waitUnlockTimerRet)
				self.waitUnlockTimer.start(5000)
			elif ret.get("type")=="Lock":
				self.showDialog=True

	#def _gatherInfoRet

	def _showInfo(self):

		self.core.packageStack.showInfo()
		self.manageRemoveBtn(True)

		if len(self.epiGuiManager.epiManager.packages_selected)>0:
			self.enableApplyBtn=True
		
		if self.epiGuiManager.initialStatusCode.get("msgCode")!="":
			self.showStatusMessage={"show":True,"msgCode":self.epiGuiManager.initialStatusCode.get("msgCode"),"type":self.epiGuiManager.initialStatusCode.get("type")}
		
		self.currentStack=2

	#def _showInfo

	def _waitUnlockTimerRet(self):

		self.epiGuiManager.checkLockInfo()
		ret=self.epiGuiManager.getLockInfo()

		if self.waitRetryCount<self.waitMaxRetry:
			if not ret.get("status"):
				self.waitRetryCount+=1
			else:
				self.waitUnlockTimer.stop()
				self._showInfo()
		else:
			self.waitUnlockTimer.stop()
			if ret.get("status"):
				self._showInfo()
			else:
				self.loadErrorCode=ret.get("msgCode")
				self.currentStack=1

	#def _waitUnlockTimerRet

	@Slot()
	def getNewCommand(self):
		
		self.endCurrentCommand=False
		
	#def getNewCommand

	@Slot()
	def launchUnlockProcess(self):

		self.showDialog=False
		self.loadMsgCode=self.epiGuiManager.MSG_LOADING_UNLOCK
		self.unlockProcessT=UnlockProcess()
		self.unlockProcessT.start()
		self.unlockProcessT.processUnlocked.connect(self._unlockProcessRet)
		self.unlockProcessT.finished.connect(self.unlockProcessT.deleteLater)

	#def launchUnlockProcess

	@Slot('QVariant')
	def _unlockProcessRet(self,ret):

		if ret.get("status"):
			self._showInfo()
		else:
			self.loadErrorCode=ret.get("msgCode")
			self.currentStack=1

	#def _unlockProcessT	

	def manageRemoveBtn(self,pkgSelected):

		match=False
		
		if self.epiGuiManager.showRemoveBtn:
			if self.epiGuiManager.pkgsInstalled:
				self.showRemoveBtn=True
			else:
				self.showRemoveBtn=False
		
		for item in self.epiGuiManager.epiManager.packages_selected:
			if item in self.epiGuiManager.pkgsInstalled:
				match=True
				break
		
		self.enableRemoveBtn=match

	#def manageRemoveBtn

	@Slot()
	def launchInstallProcess(self):

		self.showStatusMessage={"show":False,"msgCode":'',"type":''}
		self.core.packageStack.enablePkgList=False
		self.core.packageStack.filterStatusValue="all"
		self.endProcess=False
		self.enableApplyBtn=False
		if not self.epiGuiManager.noCheck:
			self.isProgressBarVisible=True
			self.feedbackCode=self.epiGuiManager.MSG_FEEDBACK_INTERNET
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
		self.showStatusMessage={"show":False,"msgCode":'',"type":''}
		self.endProcess=False
		self.isProgressBarVisible=True
		self.epiGuiManager.totalUninstallError=0
		self.epiGuiManager.totalWarningSkipPkg=0
		self.epiGuiManager.totalWarningSkipMeta=0
		self.epiGuiManager.totalWarningSkipPkg=0
		self.feedbackCode=self.epiGuiManager.MSG_FEEDBACK_UNINSTALL_CHECK
		self.core.uninstallStack.checkMetaProtection()

	#def launchUninstallProcess 

	@Slot(int)
	def manageTransitions(self,stack):

		if self.currentOptionsStack!=stack:
			self.currentOptionsStack=stack

	#de manageTransitions

	@Slot()
	def openHelp(self):

		runPkexec=False

		if 'PKEXEC_UID' in os.environ:
			runPkexec=True

		self.helpCmd='xdg-open %s'%self.core.packageStack.wikiUrl

		if runPkexec:
			user=pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
			self.helpCmd="su -c '%s' %s"%(self.helpCmd,user)
		else:
			self.helpCmd="su -c '%s' $USER"%self.helpCmd
		
		self.openHelp_t=threading.Thread(target=self._openHelpRet)
		self.openHelp_t.daemon=True
		self.openHelp_t.start()

	#def openHelp

	def _openHelpRet(self):

		subprocess.run(self.helpCmd,shell=True)

	#def _openHelpRet

	@Slot()
	def closeApplication(self):

		if self.endProcess:
			self.epiGuiManager.clearEnvironment()
			self.closeGui=True
		else:
			try:
				if os.path.exists(self.epiGuiManager.tokenPostInstall[1]):
					self.showCloseDialog=True
			except:
				pass
			self.closeGui=False

	#def closeApplication

	@Slot()
	def forceClossing(self):

		self.showCloseDialog=False
		self.endProcess=True
		self.epiGuiManager.clearEnvironment(True)
		self.closeGui=True

	#def forceClossing

	@Slot()
	def cancelClossing(self):

		self.showCloseDialog=False

	#def cancelClossing

#class Bridge

from . import Core

