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

class GetPkgInfo(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.pkgId=args[0]

	#def __init__

	def run(self):

		self.ret=EpiGui.epiGuiManager.getStoreInfo(self.pkgId)

	#def run

#class getPkgInfo

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
		self._loadMsgCode=EpiGui.epiGuiManager.MSG_LOADING_INFO
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
		self._enableApplyBtn=False
		self._enableRemoveBtn=False
		self._enablePkgList=True
		self._showDialog=False
		self._eulaUrl=""
		self._currentEulaPkg=""
		self._wikiUrl=""
		self._endProcess=True
		self._endCurrentCommand=False
		self._currentCommand=""
		self._enableKonsole=False
		self._showDependEpi=False
		self._showDependLabel=False
		self._launchedProcess=""
		self._pkgStoreInfo=["","","",""]
		self._isAllInstalled=False
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
				self.loadMsgCode=EpiGui.epiGuiManager.MSG_LOADING_WAIT
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
		self._manageRemoveBtn(True)
		self.isAllInstalled=EpiGui.epiGuiManager.isAllInstalled()

		if len(EpiGui.epiGuiManager.epiManager.packages_selected)>0:
			self.enableApplyBtn=True
		
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
				self._packagesModel.appendRow(item["pkgId"],item["showCb"],item["isChecked"],item["customName"],item["pkgIcon"],item["status"],item["isVisible"],item["resultProcess"],item["order"],item["showSpinner"],item["entryPoint"])

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

	def _getEnableKonsole(self):

		return self._enableKonsole

	#def _getEnableKonsole

	def _setEnableKonsole(self,enableKonsole):

		if self._enableKonsole!=enableKonsole:
			self._enableKonsole=enableKonsole
			self.on_enableKonsole.emit()

	#def _setEnableKonsole

	def _getShowDependEpi(self):

		return self._showDependEpi

	#def _getShowDependEpi

	def _setShowDependEpi(self,showDependEpi):

		if self._showDependEpi!=showDependEpi:
			self._showDependEpi=showDependEpi
			self.on_showDependEpi.emit()

	#def _setShowDependEpi

	def _getShowDependLabel(self):

		return self._showDependLabel

	#def _getShowDependLabel

	def _setShowDependLabel(self,showDependLabel):

		if self._showDependLabel!=showDependLabel:
			self._showDependLabel=showDependLabel
			self.on_showDependLabel.emit()

	#def _setShowDependLabel

	def _getLaunchedProcess(self):

		return self._launchedProcess

	#def _getLaunchedProcess

	def _setLaunchedProcess(self,launchedProcess):

		if self._launchedProcess!=launchedProcess:
			self._launchedProcess=launchedProcess
			self.on_launchedProcess.emit()

	#def _setLaunchedProcess

	def _getPkgStoreInfo(self):

		return self._pkgStoreInfo

	#def _getPkgStoreInfo

	def _setPkgStoreInfo(self,pkgStoreInfo):

		if self._pkgStoreInfo!=pkgStoreInfo:
			self._pkgStoreInfo=pkgStoreInfo
			self.on_pkgStoreInfo.emit()
	
	#def _setPkgStoreInfo

	def _getIsAllInstalled(self):

		return self._isAllInstalled

	#def _getIsAllInstalled

	def _setIsAllInstalled(self,isAllInstalled):

		if self._isAllInstalled!=isAllInstalled:
			self._isAllInstalled=isAllInstalled
			self.on_isAllInstalled.emit()

	#def _setIsAllInstalled

	def _getCloseGui(self):

		return self._closeGui

	#def _getCloseGui	

	def _setCloseGui(self,closeGui):
		
		if self._closeGui!=closeGui:
			self._closeGui=closeGui		
			self.on_closeGui.emit()

	#def _setCloseGui

	@Slot()
	def getNewCommand(self):
		
		self.endCurrentCommand=False
		
	#def getNewCommand

	@Slot()
	def launchUnlockProcess(self):

		self.showDialog=False
		self.loadMsgCode=EpiGui.epiGuiManager.MSG_LOADING_UNLOCK
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

		params=[]
		params.append("isChecked")
		self._updatePackagesModelInfo(params)
		self.uncheckAll=EpiGui.epiGuiManager.uncheckAll
		if len(EpiGui.epiGuiManager.epiManager.packages_selected)>0:
			self.enableApplyBtn=True
			self._manageRemoveBtn(True)
		else:
			self.enableApplyBtn=False
			self._manageRemoveBtn(False)

	#def _refreshInfo

	def _manageRemoveBtn(self,pkgSelected):

		match=False
		
		if EpiGui.epiGuiManager.showRemoveBtn:
			if EpiGui.epiGuiManager.pkgsInstalled:
				self.showRemoveBtn=True
			else:
				self.showRemoveBtn=False
		
		for item in EpiGui.epiGuiManager.epiManager.packages_selected:
			if item in EpiGui.epiGuiManager.pkgsInstalled:
				match=True
				break
		
		if match:
			self.enableRemoveBtn=True
		else:
			self.enableRemoveBtn=False

	#def _manageRemoveBtn

	@Slot()
	def launchInstallProcess(self):

		self.showStatusMessage=[False,"","Ok"]
		self.enablePkgList=False
		self.endProcess=False
		self.enableApplyBtn=False
		if not EpiGui.epiGuiManager.noCheck:
			self.feedbackCode=EpiGui.epiGuiManager.MSG_FEEDBACK_INTERNET
			EpiGui.epiGuiManager.checkInternetConnection()
			self.checkConnectionTimer=QTimer()
			self.checkConnectionTimer.timeout.connect(self._checkConnectionTimerRet)
			self.checkConnectionTimer.start(1000)
		else:
			self._getEulas()
	
	#def launchInstallProcess

	def _checkConnectionTimerRet(self):

		EpiGui.epiGuiManager.getResultCheckConnection()
		if EpiGui.epiGuiManager.endCheck:
			self.checkConnectionTimer.stop()
			self.feedbackCode=0
			if EpiGui.epiGuiManager.retConnection[0]:
				self.endProcess=True
				self.enableApplyBtn=True
				self.showStatusMessage=[True,EpiGui.epiGuiManager.retConnection[1],"Error"]
			else:
				self._getEulas()

	#def _checkConnectionTimerRet

	def _getEulas(self):

		if not EpiGui.epiGuiManager.eulaAccepted:
			EpiGui.epiGuiManager.getEulasToCheck()
			if len(EpiGui.epiGuiManager.eulasToShow)>0:
				self._manageEulas()
		else:
			self._installProcess()

	#def _getEulas

	def _manageEulas(self):

		if len(EpiGui.epiGuiManager.eulasToCheck)>0:
			self.enableApplyBtn=True
			self.enableRemoveBtn=True
			self.eulaUrl=EpiGui.epiGuiManager.eulasToCheck[EpiGui.epiGuiManager.eulaOrder]["eula"]
			self.feedbackCode=EpiGui.epiGuiManager.MSG_FEEDBACK_EULA
			self.currentEulaPkg=EpiGui.epiGuiManager.eulasToCheck[EpiGui.epiGuiManager.eulaOrder]["pkg_name"]
			self.currentPkgOption=1
		else:
			self.currentPkgOption=0
			self.currentEulaPkg=""
			if EpiGui.epiGuiManager.eulaAccepted:
				self._installProcess()
			else:
				self.endProcess=True
				self.feedbackCode=""
				self.enablePkgList=True
				if not self.selectPkg:
					self.enableApplyBtn=True
					self.enableRemoveBtn=True

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

	def _installProcess(self):

		self.enableApplyBtn=False
		self.enableRemoveBtn=False
		self.enableKonsole=True
		self.launchedProcess="install"
		self.feedbackCode=EpiGui.epiGuiManager.MSG_FEEDBACK_INSTALL_GATHER
		EpiGui.epiGuiManager.initInstallProcess()
		self._updateResultPackagesModel('start',"install")
		if EpiGui.epiGuiManager.order>0:
			self.showDependEpi=True
			self.showDependLabel=True
		self.isProcessRunning=True
		self.installProcessTimer=QTimer(None)
		self.installProcessTimer.timeout.connect(self._installProcessTimerRet)
		self.installProcessTimer.start(100)		

	#def _installProcess

	def _installProcessTimerRet(self):

		error=False

		if not EpiGui.epiGuiManager.addRepositoryKeysLaunched:
			EpiGui.epiGuiManager.addRepositoryKeysLaunched=True
			self.currentCommand=EpiGui.epiGuiManager.getAddRepositoryCommand()
			self.endCurrentCommand=True

		if EpiGui.epiGuiManager.addRepositoryKeysDone:
			if not EpiGui.epiGuiManager.updateKeyRingLaunched:
				EpiGui.epiGuiManager.updateKeyRingLaunched=True
				self.currentCommand=EpiGui.epiGuiManager.getUpdateKeyRingCommand() 
				self.endCurrentCommand=True

			if EpiGui.epiGuiManager.updateKeyRingDone:
				if not EpiGui.epiGuiManager.downloadAppLaunched:
					self.feedbackCode=EpiGui.epiGuiManager.MSG_FEEDBACK_INSTALL_DOWNLOAD
					EpiGui.epiGuiManager.downloadAppLaunched=True
					self.currentCommand=EpiGui.epiGuiManager.getDownloadAppCommand()
					self.endCurrentCommand=True

				if EpiGui.epiGuiManager.downloadAppDone:
					if not EpiGui.epiGuiManager.checkDownloadLaunched:
						EpiGui.epiGuiManager.checkDownloadLaunched=True
						EpiGui.epiGuiManager.checkDownload()

					if EpiGui.epiGuiManager.checkDownloadDone:
						if EpiGui.epiGuiManager.feedBackCheck[0]:
							if not EpiGui.epiGuiManager.preInstallAppLaunched:
								self.feedbackCode=EpiGui.epiGuiManager.MSG_FEEDBACK_INSTALL_PREINSTALL
								EpiGui.epiGuiManager.preInstallAppLaunched=True
								self.currentCommand=EpiGui.epiGuiManager.getPreInstallCommand()
								self.endCurrentCommand=True

							if EpiGui.epiGuiManager.preInstallAppDone:
								if not EpiGui.epiGuiManager.checkPreInstallLaunched:
									EpiGui.epiGuiManager.checkPreInstallLaunched=True
									EpiGui.epiGuiManager.checkPreInstall()

								if EpiGui.epiGuiManager.checkPreInstallDone:
									if EpiGui.epiGuiManager.feedBackCheck[0]:
										if not EpiGui.epiGuiManager.checkArquitectureLaunched:
											self.feedbackCode=EpiGui.epiGuiManager.MSG_FEEDBACK_INSTALL_ARQUITECTURE
											EpiGui.epiGuiManager.checkArquitectureLaunched=True
											self.currentCommand=EpiGui.epiGuiManager.getCheckArquitectureCommand()
											self.endCurrentCommand=True		

										if EpiGui.epiGuiManager.checkArquitectureDone:
											if not EpiGui.epiGuiManager.updateReposLaunched:
												self.feedbackCode=EpiGui.epiGuiManager.MSG_FEEDBACK_INSTALL_REPOSITORIES
												EpiGui.epiGuiManager.updateReposLaunched=True
												self.currentCommand=EpiGui.epiGuiManager.getUpdateReposCommand()
												self.endCurrentCommand=True

											if EpiGui.epiGuiManager.updateReposDone:
												if not EpiGui.epiGuiManager.installAppLaunched:
													self.feedbackCode=EpiGui.epiGuiManager.MSG_FEEDBACK_INSTALL_INSTALL
													EpiGui.epiGuiManager.installAppLaunched=True
													self.currentCommand=EpiGui.epiGuiManager.getInstallCommand()
													self.endCurrentCommand=True

												if EpiGui.epiGuiManager.installAppDone:
													if not EpiGui.epiGuiManager.checkInstallLaunched:
														EpiGui.epiGuiManager.checkInstallLaunched=True
														EpiGui.epiGuiManager.checkInstall()

													if EpiGui.epiGuiManager.checkInstallDone:
														if EpiGui.epiGuiManager.feedBackCheck[0]:
															if not EpiGui.epiGuiManager.postInstallAppLaunched:
																self.feedbackCode=EpiGui.epiGuiManager.MSG_FEEDBACK_INSTALL_ENDING
																EpiGui.epiGuiManager.postInstallAppLaunched=True
																self.currentCommand=EpiGui.epiGuiManager.getPostInstallCommand()
																self.endCurrentCommand=True

															if EpiGui.epiGuiManager.postInstallAppDone:
																if not EpiGui.epiGuiManager.checkPostInstallLaunched:
																	EpiGui.epiGuiManager.checkPostInstallLaunched=True
																	EpiGui.epiGuiManager.checkPostInstall()

																if EpiGui.epiGuiManager.checkPostInstallDone:
																	if EpiGui.epiGuiManager.feedBackCheck[0]:
																		self.showDependEpi=False
																		if EpiGui.epiGuiManager.order>0:
																			EpiGui.epiGuiManager.initInstallProcess()
																			self._updateResultPackagesModel('end',"install")
																		else:
																			self.feedbackCode=""
																			self.endProcess=True
																			self.isProcessRunning=False
																			self.isAllInstalled=EpiGui.epiGuiManager.isAllInstalled()
																			self.installProcessTimer.stop()
																			self._updateResultPackagesModel('end',"install")
																			self._manageRemoveBtn(True)
																			self.enableApplyBtn=True
																			self.enablePkgList=True
																			self.showStatusMessage=[True,EpiGui.epiGuiManager.feedBackCheck[1],EpiGui.epiGuiManager.feedBackCheck[2]]
																			EpiGui.epiGuiManager.epiManager.remove_repo_keys()
																	else:
																		error=True
														else:
															error=True
									else:
										error=True
						else:
							error=True

		if error:
			self.endProcess=True
			self.feedbackCode=""
			self.isProcessRunning=False
			self.showDependEpi=False
			self.isAllInstalled=EpiGui.epiGuiManager.isAllInstalled()
			self.installProcessTimer.stop()
			self._updateResultPackagesModel("end","install")
			self.showStatusMessage=[True,EpiGui.epiGuiManager.feedBackCheck[1],EpiGui.epiGuiManager.feedBackCheck[2]]
			EpiGui.epiGuiManager.epiManager.remove_repo_keys()
		
		if EpiGui.epiGuiManager.addRepositoryKeysLaunched:
			if not EpiGui.epiGuiManager.addRepositoryKeysDone:
				if not os.path.exists(EpiGui.epiGuiManager.tokenKeys[1]):
					EpiGui.epiGuiManager.addRepositoryKeysDone=True

		if EpiGui.epiGuiManager.updateKeyRingLaunched:
			if not EpiGui.epiGuiManager.updateKeyRingDone:
				if not os.path.exists(EpiGui.epiGuiManager.tokenKeyring[1]):
					EpiGui.epiGuiManager.updateKeyRingDone=True

		if EpiGui.epiGuiManager.downloadAppLaunched:
			if not EpiGui.epiGuiManager.downloadAppDone:
				if not os.path.exists(EpiGui.epiGuiManager.tokenDownload[1]):
					EpiGui.epiGuiManager.downloadAppDone=True

		if EpiGui.epiGuiManager.preInstallAppLaunched:
			if not EpiGui.epiGuiManager.preInstallAppDone:
				if not os.path.exists(EpiGui.epiGuiManager.tokenPreInstall[1]):
					EpiGui.epiGuiManager.preInstallAppDone=True
	
		if EpiGui.epiGuiManager.checkArquitectureLaunched:
			if not EpiGui.epiGuiManager.checkArquitectureDone:
				if not os.path.exists(EpiGui.epiGuiManager.tokenArquitecture[1]):
					EpiGui.epiGuiManager.checkArquitectureDone=True

		if EpiGui.epiGuiManager.updateReposLaunched:
			if not EpiGui.epiGuiManager.updateReposDone:
				if not os.path.exists(EpiGui.epiGuiManager.tokenUpdaterepos[1]):
					EpiGui.epiGuiManager.updateReposDone=True

		if EpiGui.epiGuiManager.installAppLaunched:
			if not EpiGui.epiGuiManager.installAppDone:
				if not os.path.exists(EpiGui.epiGuiManager.tokenInstall[1]):
					EpiGui.epiGuiManager.installAppDone=True

		if EpiGui.epiGuiManager.postInstallAppLaunched:
			if not EpiGui.epiGuiManager.postInstallAppDone:
				if not os.path.exists(EpiGui.epiGuiManager.tokenPostInstall[1]):
					EpiGui.epiGuiManager.postInstallAppDone=True
	
	#def _installProcessTimerRet

	@Slot()
	def launchUninstallProcess(self):

		self.enableApplyBtn=False
		self.enableRemoveBtn=False
		self.enablePkgList=False
		self.showStatusMessage=[False,"","Ok"]
		self.endProcess=False
		self.feedbackCode=EpiGui.epiGuiManager.MSG_FEEDBACK_UNINSTALL_CHECK
		self.checkMetaProtectionT=CheckMetaProtection()
		self.checkMetaProtectionT.start()
		self.checkMetaProtectionT.finished.connect(self._checkMetaProtectionRet)

	#def launchUninstallProcess

	def _checkMetaProtectionRet(self):

		if EpiGui.epiGuiManager.stopUninstall[0]:
			self.enableApplyBtn=True
			self.enablePkgList=True
			self.feedbackCode=""
			self.showStatusMessage=[True,EpiGui.epiGuiManager.stopUninstall[1],"Error"]
		else:
			self.enableKonsole=True
			self.feedbackCode=EpiGui.epiGuiManager.MSG_FEEDBACk_UNINSTALL_RUN
			self.isProcessRunning=True
			self.launchedProcess="uninstall"
			EpiGui.epiGuiManager.initUnInstallProcess()
			self._updateResultPackagesModel('start',"uninstall")
			self.uninstallProcessTimer=QTimer(None)
			self.uninstallProcessTimer.timeout.connect(self._uninstallProcessTimerRet)
			self.uninstallProcessTimer.start(100)		

	#def _checkMetaProtectionRet

	def _uninstallProcessTimerRet(self):

		if not EpiGui.epiGuiManager.removePkgLaunched:
			EpiGui.epiGuiManager.removePkgLaunched=True
			self.currentCommand=EpiGui.epiGuiManager.getUninstallCommand()
			self.endCurrentCommand=True

		if EpiGui.epiGuiManager.removePkgDone:
			if not EpiGui.epiGuiManager.checkRemoveLaunched:
				EpiGui.epiGuiManager.checkRemoveLaunched=True
				EpiGui.epiGuiManager.checkRemove()

			if EpiGui.epiGuiManager.checkRemoveDone:
				self.isProcessRunning=False
				self.endProcess=True
				self.feedbackCode=""
				self.enableApplyBtn=True
				self.enablePkgList=True
				self.isAllInstalled=EpiGui.epiGuiManager.isAllInstalled()
				self._manageRemoveBtn(True)
				self.uninstallProcessTimer.stop()
				self._updateResultPackagesModel("end","uninstall")
				self.showStatusMessage=[True,EpiGui.epiGuiManager.remove[1],EpiGui.epiGuiManager.remove[2]]
				EpiGui.epiGuiManager.epiManager.remove_repo_keys()
		
		if EpiGui.epiGuiManager.removePkgLaunched:
			if not EpiGui.epiGuiManager.removePkgDone:
				if not os.path.exists(EpiGui.epiGuiManager.tokenUninstall[1]):
					EpiGui.epiGuiManager.removePkgDone=True
		
	#def _uninstallProcessTimerRet

	def _updateResultPackagesModel(self,step,action):

		params=[]
		params.append("showSpinner")
		params.append("resultProcess")
		if step=="start" and action=="install":
			if EpiGui.epiGuiManager.order>0:
				params.append("isVisible")
		if step=="end":
			params.append("pkgIcon")
			params.append("status")

		self._updatePackagesModelInfo(params)

	#def _updateResultPackagesModel

	def _updatePackagesModelInfo(self,params):

		updatedInfo=EpiGui.epiGuiManager.packagesData
		valuesToUpdate=[]
		if len(updatedInfo)>0:
			for i in range(len(updatedInfo)):
				index=self._packagesModel.index(i)
				for item in params:
					tmp={}
					tmp[item]=updatedInfo[i][item]
					valuesToUpdate.append(tmp)
				self._packagesModel.setData(index,valuesToUpdate)
	
	#def _updatePackagesModelInfo

	@Slot('QVariantList')

	def showPkgInfo(self,params):

		self.showStatusMessage=[False,"","Ok"]

		if params[0]==0:
			self.feedbackCode=EpiGui.epiGuiManager.MSG_FEEDBACK_STORE_INFO
			self.getPkgInfoT=GetPkgInfo(params[1])
			self.getPkgInfoT.start()
			self.getPkgInfoT.finished.connect(self._getPkgInfoRet)
		else:
			self.feedbackCode=""
			self.currentPkgOption=0

	#def showPkgInfo

	def _getPkgInfoRet(self):

		if len(self.getPkgInfoT.ret)==0:
			self.feedbackCode=EpiGui.epiGuiManager.MSG_FEEDBACK_STORE_EMPTY
		else:
			self.feedbackCode=""
			self.pkgStoreInfo=self.getPkgInfoT.ret
			self.currentPkgOption=2

	#def _getPkgInfoRet

	@Slot(str)

	def launchApp(self, entryPoint):

		self.launchAppCmd=entryPoint
		self.launchAppT=threading.Thread(target=self._launchAppRet)
		self.launchAppT.daemon=True
		self.launchAppT.start()
		
	#def launchApp

	def _launchAppRet(self):

		os.system(self.launchAppCmd)

	#def _launchAppRet

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

		if self.endProcess:
			self.closeGui=True
		else:
			self.closeGui=False

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

	on_enableApplyBtn=Signal()
	enableApplyBtn=Property(bool,_getEnableApplyBtn,_setEnableApplyBtn,notify=on_enableApplyBtn)

	on_enableRemoveBtn=Signal()
	enableRemoveBtn=Property(bool,_getEnableRemoveBtn,_setEnableRemoveBtn,notify=on_enableRemoveBtn)

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

	on_enableKonsole=Signal()
	enableKonsole=Property(bool,_getEnableKonsole,_setEnableKonsole,notify=on_enableKonsole)

	on_showDependEpi=Signal()
	showDependEpi=Property(bool,_getShowDependEpi,_setShowDependEpi,notify=on_showDependEpi)

	on_showDependLabel=Signal()
	showDependLabel=Property(bool,_getShowDependLabel,_setShowDependLabel,notify=on_showDependLabel)

	on_launchedProcess=Signal()
	launchedProcess=Property('QString',_getLaunchedProcess,_setLaunchedProcess,notify=on_launchedProcess)
	
	on_pkgStoreInfo=Signal()
	pkgStoreInfo=Property('QVariantList',_getPkgStoreInfo,_setPkgStoreInfo,notify=on_pkgStoreInfo)
	
	on_isAllInstalled=Signal()
	isAllInstalled=Property(bool,_getIsAllInstalled,_setIsAllInstalled,notify=on_isAllInstalled)

	on_closeGui=Signal()
	closeGui=Property(bool,_getCloseGui,_setCloseGui, notify=on_closeGui)

	packagesModel=Property(QObject,_getPackagesModel,constant=True)

#class EpiGui

