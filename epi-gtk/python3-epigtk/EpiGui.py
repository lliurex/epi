#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys
import pwd

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

class CheckMetaProtection(QThread):

	def __init__(self, *args):

		QThread.__init__(self)

	#def __init__

	def run(self):

		EpiGui.epiGuiManager.checkRemoveMeta()

	#def run

#class CheckMetaProtection

class EpiGui(QObject):

	epiGuiManager=EpiGuiManager.EpiGuiManager()
	MSG_LOADING_INFO=0
	MSG_LOADING_WAIT=1
	MSG_LOADING_UNLOCK=2
	MSG_FEEDBACK_INTERNET=3
	MSG_FEEDBACK_EULA=7
	MSG_FEEDBACK_INSTALL_1=8
	MSG_FEEDBACK_UNINSTALL_CHECK=9

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
		self._localDebError=""
		self._showStatusMessage=[False,"","Ok"]
		self._currentStack=0
		self._currentOptionsStack=0
		self._currentPkgOption=0
		self._feedbackCode=""
		self._uncheckAll=True
		self._selectPkg=False
		self._showRemoveBtn=False
		self._isProcessRunning=False
		self._enableActionBtn=False
		self._enablePkgList=True
		self._showDialog=False
		self._eulaUrl=""
		self._currentEulaPkg=""
		self._wikiUrl=""
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
				self.gatherInfoT=GatherInfo(epiFile,noCheck,debug)
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
				self.loadMsgCode=EpiGui.MSG_LOADING_WAIT
				self.waitUnlockTimer=QTimer()
				self.waitUnlockTimer.timeout.connect(self._waitUnlockTimerRet)
				self.waitUnlockTimer.start(5000)
			elif self.gatherInfo.ret[2]=="Lock":
				self.showDialog=True

	#def _gatherInfoRet

	def _showInfo(self):

		self._updatePackagesModel()
		self.uncheckAll=EpiGui.epiGuiManager.uncheckAll
		self.selectPkg=EpiGui.epiGuiManager.selectPkg
		self.wikiUrl=EpiGui.epiGuiManager.wikiUrl

		if EpiGui.epiGuiManager.showRemoveBtn:
			if EpiGui.epiGuiManager.pkgsInstalled:
				self.showRemoveBtn=True
		
		if len(EpiGui.epiGuiManager.epiManager.packages_selected)>0:
			self.enableActionBtn=True
		
		if EpiGui.epiGuiManager.initialStatusCode[0]!="":
			self.showStatusMessage=[True,EpiGui.epiGuiManager.initialStatusCode[0],EpiGui.epiGuiManager.initialStatusCode[1]]
		
		self.currentStack=2

	#def _showInfo

	def _waitUnlockTimerRet(self):

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

	def _getEnablePkgList(self):

		return self._enablePkgList

	#def _getEnablePkgList

	def _setEnablePkgList(self,enablePkgList):

		if self._enablePkgList!=enablePkgList:
			self._enablePkgList=enablePkgList
			self.on_enablePkgList.emit()

	#def setEnablePkgList

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

	def _getEulaUrl(self):

		return self._eulaUrl

	#def _getEulaUrl

	def _setEulaUrl(self,eulaUrl):

		if self._eulaUrl!=eulaUrl:
			self._eulaUrl=eulaUrl
			self.on_eulaUrl.emit()

	#def _setEulaUrl

	def _getCurrentEulaPkg(self):

		return self._currentEulaPkg

	#def _getCurrentEulaPkg

	def _setCurrentEulaPkg(self,currentEulaPkg):

		if self._currentEulaPkg!=currentEulaPkg:
			self._currentEulaPkg=currentEulaPkg
			self.on_currentEulaPkg.emit()

	#def _setCurrentEulaPkg

	def _getWikiUrl(self):

		return self._wikiUrl

	#def _getWikiUrl

	def _setWikiUrl(self,wikiUrl):

		if self._wikiUrl!=wikiUrl:
			self._wikiUrl=wikiUrl
			self.on_wikiUrl.emit()

	#def _setWikiUrl

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
		self.unlockProcessT.finished.connect(self._unlockProcessRet)

	#def launchUnlockProcess

	def _unlockProcessRet(self):

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
	def initInstallProcess(self):

		self.showStatusMessage=[False,"","Ok"]
		self.enablePkgList=False
		self.enableActionBtn=False
		if not EpiGui.epiGuiManager.noCheck:
			self.feedbackCode=EpiGui.MSG_FEEDBACK_INTERNET
			EpiGui.epiGuiManager.checkInternetConnection()
			self.checkConnectionTimer=QTimer()
			self.checkConnectionTimer.timeout.connect(self._checkConnectionTimerRet)
			self.checkConnectionTimer.start(1000)
		else:
			self._getEulas()
	
	#def initInstallProcess

	def _checkConnectionTimerRet(self):

		EpiGui.epiGuiManager.getResultCheckConnection()
		if EpiGui.epiGuiManager.endCheck:
			self.checkConnectionTimer.stop()
			self.feedbackCode=0
			if EpiGui.epiGuiManager.retConnection[0]:
				self.enableActionBtn=True
				self.showStatusMessage=[True,EpiGui.epiGuiManager.retConnection[1],"Error"]
			else:
				self._getEulas()

	#def _checkConnectionTimerRet

	def _getEulas(self):

		if not EpiGui.epiGuiManager.eulaAccepted:
			EpiGui.epiGuiManager.getEulasToCheck()
			if len(EpiGui.epiGuiManager.eulasToShow)>0:
				self._manageEulas()
	
	#def _getEulas

	def _manageEulas(self):

		if len(EpiGui.epiGuiManager.eulasToCheck)>0:
			self.enableActionBtn=True
			self.eulaUrl=EpiGui.epiGuiManager.eulasToCheck[EpiGui.epiGuiManager.eulaOrder]["eula"]
			self.feedbackCode=EpiGui.MSG_FEEDBACK_EULA
			self.currentEulaPkg=EpiGui.epiGuiManager.eulasToCheck[EpiGui.epiGuiManager.eulaOrder]["pkg_name"]
			self.currentPkgOption=1
		else:
			self.currentPkgOption=0
			self.currentEulaPkg=""
			if EpiGui.epiGuiManager.eulaAccepted:
				self.enableActionBtn=False
				self.feedbackCode=EpiGui.MSG_FEEDBACK_INSTALL_1
				self.isProcessRunning=True
			else:
				self.feedbackCode=""
				self.enablePkgList=True
				if not self.selectPkg:
					self.enableActionBtn=True

	#def _manageEulas

	@Slot()
	def acceptEula(self):

		EpiGui.epiGuiManager.acceptEula()
		self._manageEulas()

	#def acceptEula	

	@Slot()
	def rejectEula(self):

		EpiGui.epiGuiManager.rejectEula()
		if self.selectPkg:
			self._refreshInfo()
		self._manageEulas()

	#def rejectEula

	@Slot()
	def launchUninstallProcess(self):

		self.enableActionBtn=False
		self.enablePkgList=False
		self.showStatusMessage=[False,"","Ok"]

		self.feedbackCode=EpiGui.MSG_FEEDBACK_UNINSTALL_CHECK
		self.checkMetaProtectionT=CheckMetaProtection()
		self.checkMetaProtectionT.start()
		self.checkMetaProtectionT.finished.connect(self._checkMetaProtectionRet)

	#def launchUninstallProcess

	def _checkMetaProtectionRet(self):

		if EpiGui.epiGuiManager.stopUninstall[0]:
			self.enableActionBtn=True
			self.enablePkgList=True
			self.feedbackCode=""
			self.showStatusMessage=[True,EpiGui.epiGuiManager.stopUninstall[1],"Error"]


	#def _checkMetaProtectionRet

	def _updatePackagesModelInfo(self,param):

		updatedInfo=EpiGui.epiGuiManager.packagesData

		if len(updatedInfo)>0:
			for i in range(len(updatedInfo)):
				index=self._packagesModel.index(i)
				self._packagesModel.setData(index,param,updatedInfo[i][param])
	
	#def _updatePackagesModelInfo

	@Slot()
	def openHelp(self):

		runPkexec=False

		if 'PKEXEC_UID' in os.environ:
			runPkexec=True

		self.helpCmd='xdg-open %s'%self.wikiUrl

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

		os.system(self.helpCmd)

	#def _openHelpRet

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
	
	on_localDebError=Signal()
	localDebError=Property(str,_getLocalDebError,_setLocalDebError,notify=on_localDebError)

	on_feedbackCode=Signal()
	feedbackCode=Property(int,_getFeedbackCode,_setFeedbackCode,notify=on_feedbackCode)

	on_uncheckAll=Signal()
	uncheckAll=Property(bool,_getUncheckAll,_setUncheckAll,notify=on_uncheckAll)

	on_selectPkg=Signal()
	selectPkg=Property(bool,_getSelectPkg,_setSelectPkg,notify=on_selectPkg)

	on_enableActionBtn=Signal()
	enableActionBtn=Property(bool,_getEnableActionBtn,_setEnableActionBtn,notify=on_enableActionBtn)

	on_enablePkgList=Signal()
	enablePkgList=Property(bool,_getEnablePkgList,_setEnablePkgList,notify=on_enablePkgList)
	
	on_showRemoveBtn=Signal()
	showRemoveBtn=Property(bool,_getShowRemoveBtn,_setShowRemoveBtn,notify=on_showRemoveBtn)

	on_isProcessRunning=Signal()
	isProcessRunning=Property(bool,_getIsProcessRunning,_setIsProcessRunning,notify=on_isProcessRunning)

	on_showStatusMessage=Signal()
	showStatusMessage=Property('QVariantList',_getShowStatusMessage,_setShowStatusMessage,notify=on_showStatusMessage)

	on_showDialog=Signal()
	showDialog=Property(bool,_getShowDialog,_setShowDialog,notify=on_showDialog)
	
	on_eulaUrl=Signal()
	eulaUrl=Property(str,_getEulaUrl,_setEulaUrl,notify=on_eulaUrl)

	on_currentEulaPkg=Signal()
	currentEulaPkg=Property(str,_getCurrentEulaPkg,_setCurrentEulaPkg,notify=on_currentEulaPkg)

	on_wikiUrl=Signal()
	wikiUrl=Property(str,_getWikiUrl,_setWikiUrl,notify=on_wikiUrl)

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

