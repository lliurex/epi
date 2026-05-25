#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import signal
import sys

signal.signal(signal.SIGINT, signal.SIG_DFL)

class InstallStack(QObject):

	GLOBALTOKENS = [
		("addRepositoryKeys", "tokenKeys"),
		("updateKeyRing", "tokenKeyring"),
		("checkArquitecture", "tokenArquitecture"),
		("updateRepos", "tokenUpdaterepos"),

	]

	PROCESSPKGTOKENS=[
		("downloadApp", "tokenDownload"),
		("preInstallApp", "tokenPreInstall"),
		("installApp", "tokenInstall"),
		("postInstallApp", "tokenPostInstall")
	]	

	def __init__(self):

		super().__init__()
		self.core=Core.Core.get_core()
		self.epiGuiManager=self.core.epiGuiManager

	#def __init__

	def checkInternetConnection(self):

		self.epiGuiManager.checkInternetConnection()
		self.checkConnectionTimer=QTimer()
		self.checkConnectionTimer.timeout.connect(self._checkConnectionTimerRet)
		self.checkConnectionTimer.start(1000)

	#def checkInternetConnection

	def _checkConnectionTimerRet(self):

		self.epiGuiManager.getResultCheckConnection()
		if self.epiGuiManager.endCheck:
			self.checkConnectionTimer.stop()
			self.core.mainStack.feedbackCode=0
			if not self.epiGuiManager.retConnection.get('status'):
				self.core.mainStack.isProgressBarVisible=False
				self.core.mainStack.endProcess=True
				self.core.mainStack.enableApplyBtn=True
				self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.epiGuiManager.retConnection.get("msgCode"),"type":self.epiGuiManager.retConnection.get("type")}
			else:
				self.core.mainStack.isProgressBarVisible=False
				self.core.packageStack.getEulas()

	#def _checkConnectionTimerRet

	def installProcess(self):

		self.core.mainStack.enableApplyBtn=False
		self.core.mainStack.enableRemoveBtn=False
		self.core.mainStack.enableKonsole=True
		self.core.mainStack.isProgressBarVisible=True
		self.totalError=0
		self.core.packageStack.totalErrorInProcess=0
		self.launchedProcess="install"
		self._initInstallProcess()
		self.globalInstallProcessTimer=QTimer(None)
		self.globalInstallProcessTimer.timeout.connect(self._globalInstallProcessTimerRet)
		self.globalInstallProcessTimer.start(100)		

	#def _installProcess

	def _initInstallProcess(self):

		self.core.mainStack.feedbackCode=self.epiGuiManager.MSG_FEEDBACK_INSTALL_GATHER
		self.epiGuiManager.initInstallProcess()
		self.core.mainStack.isProcessRunning=True
		self.error=False
		self.showError=False
		self.endAction=False
		self.pkgProcessed=False
		countLimit=len(self.epiGuiManager.pkgSelectedFromList)
		if countLimit==0:
			self.countLimit=1
		else:
			self.countLimit=countLimit

		self.pkgToSelect=-1
		self.pkgToProcess=""

	#def _initInstallProcess

	def _globalInstallProcessTimerRet(self):

		if not self.epiGuiManager.addRepositoryKeysLaunched:
			self.epiGuiManager.addRepositoryKeysLaunched=True
			self.core.mainStack.currentCommand=self.epiGuiManager.getAddRepositoryCommand()
			self.core.mainStack.endCurrentCommand=True

		if not self.epiGuiManager.addRepositoryKeysDone:
			return self._checkProcessTokens()

		if not self.epiGuiManager.updateKeyRingLaunched:
			self.epiGuiManager.updateKeyRingLaunched=True
			self.core.mainStack.currentCommand=self.epiGuiManager.getUpdateKeyRingCommand() 
			self.core.mainStack.endCurrentCommand=True

		if not self.epiGuiManager.updateKeyRingDone:
			return self._checkProcessTokens()
		
		if not self.epiGuiManager.checkArquitectureLaunched:
			self.core.mainStack.feedbackCode=self.epiGuiManager.MSG_FEEDBACK_INSTALL_ARQUITECTURE
			self.epiGuiManager.checkArquitectureLaunched=True
			self.core.mainStack.currentCommand=self.epiGuiManager.getCheckArquitectureCommand()
			self.core.mainStack.endCurrentCommand=True

		if not self.epiGuiManager.checkArquitectureDone:
			return self._checkProcessTokens()
		
		if not self.epiGuiManager.updateReposLaunched:
			self.core.mainStack.feedbackCode=self.epiGuiManager.MSG_FEEDBACK_INSTALL_REPOSITORIES
			self.epiGuiManager.updateReposLaunched=True
			self.core.mainStack.currentCommand=self.epiGuiManager.getUpdateReposCommand()
			self.core.mainStack.endCurrentCommand=True

		if not self.epiGuiManager.updateReposDone:
			return self._checkProcessTokens()
		
		self.globalInstallProcessTimer.stop()
		self.pkgInstallProcessTimer=QTimer(None)
		self.pkgInstallProcessTimer.timeout.connect(self._pkgInstallProcessTimerRet)
		self.pkgInstallProcessTimer.start(100)		
	
	#def _globalInstallProcessTimerRet

	def _pkgInstallProcessTimerRet(self):
		
		if not self.pkgProcessed:
			if self.epiGuiManager.order!=0:
				if self.error:
					self.endAction=True
				else:
					self.error=False
			
			if not self.endAction:
				self.pkgToSelect+=1
				if self.pkgToSelect<self.countLimit:
					if self.epiGuiManager.order==0:
						try:
							self.pkgToProcess=self.epiGuiManager.pkgSelectedFromList[self.pkgToSelect]
						except:
							self.pkgToProcess="all"
					else:
						self.pkgToProcess="all"

					self.epiGuiManager.initPkgInstallProcess(self.pkgToProcess)
					self.core.packageStack.updateResultPackagesModel('start',"install")
					if self.epiGuiManager.order>0:
						self.core.packageStack.showDependEpi=True
						self.core.packageStack.showDependLabel=True
					if not self.epiGuiManager.downloadAppLaunched:
						self.core.mainStack.feedbackCode=self.epiGuiManager.MSG_FEEDBACK_INSTALL_DOWNLOAD
						self.epiGuiManager.downloadAppLaunched=True
						self.core.mainStack.currentCommand=self.epiGuiManager.getDownloadAppCommand(self.pkgToProcess)
						self.core.mainStack.endCurrentCommand=True
					
				else:
					self.endAction=True

			self.pkgProcessed=True

		if not self.endAction:
			if not self.epiGuiManager.downloadAppDone:
				return self._checkProcessTokens()
			
			if not self.epiGuiManager.checkDownloadLaunched:
				self.epiGuiManager.checkDownloadLaunched=True
				self.epiGuiManager.checkDownload(self.pkgToProcess)

			if not self.epiGuiManager.checkDownloadDone:
				return
			
			if not self.epiGuiManager.feedBackCheck.get("status"):
				self._handleStepError()
				return

			if not self.epiGuiManager.preInstallAppLaunched:
				self.core.mainStack.feedbackCode=self.epiGuiManager.MSG_FEEDBACK_INSTALL_PREINSTALL
				self.epiGuiManager.preInstallAppLaunched=True
				self.core.mainStack.currentCommand=self.epiGuiManager.getPreInstallCommand(self.pkgToProcess)
				self.core.mainStack.endCurrentCommand=True

			if not self.epiGuiManager.preInstallAppDone:
				return self._checkProcessTokens()

			if not self.epiGuiManager.checkPreInstallLaunched:
				self.epiGuiManager.checkPreInstallLaunched=True
				self.epiGuiManager.checkPreInstall(self.pkgToProcess)

			if not self.epiGuiManager.checkPreInstallDone:
				return

			if not self.epiGuiManager.feedBackCheck.get("status"):
				self._handleStepError()
				return
			
			if not self.epiGuiManager.installAppLaunched:
				self.core.mainStack.feedbackCode=self.epiGuiManager.MSG_FEEDBACK_INSTALL_INSTALL
				self.epiGuiManager.installAppLaunched=True
				self.core.mainStack.currentCommand=self.epiGuiManager.getInstallCommand(self.pkgToProcess)
				self.core.mainStack.endCurrentCommand=True

			if not self.epiGuiManager.installAppDone:
				return self._checkProcessTokens()

			if not self.epiGuiManager.checkInstallLaunched:
				self.epiGuiManager.checkInstallLaunched=True
				self.epiGuiManager.checkInstall(self.pkgToProcess)

			if not self.epiGuiManager.checkInstallDone:
				return
			
			if not self.epiGuiManager.feedBackCheck.get("status"):
				self._handleStepError()
				return
			
			if not self.epiGuiManager.postInstallAppLaunched:
				self.core.mainStack.feedbackCode=self.epiGuiManager.MSG_FEEDBACK_INSTALL_ENDING
				self.epiGuiManager.postInstallAppLaunched=True
				self.core.mainStack.currentCommand=self.epiGuiManager.getPostInstallCommand(self.pkgToProcess)
				self.core.mainStack.endCurrentCommand=True
										
			if not self.epiGuiManager.postInstallAppDone:
				return self._checkProcessTokens()
										
			if not self.epiGuiManager.checkPostInstallLaunched:
				self.epiGuiManager.checkPostInstallLaunched=True
				self.epiGuiManager.checkPostInstall(self.pkgToProcess)
										
			if not self.epiGuiManager.checkPostInstallDone:
				return

			self.core.packageStack.updateResultPackagesModel('end',"install")

			if  self.epiGuiManager.feedBackCheck.get("status"):
				self.core.packageStack.showDependEpi=False
				if self.epiGuiManager.order>0:
					self.epiGuiManager.epiManager.zerocenter_feedback(self.epiGuiManager.order,"install",True)
					self._initInstallProcess()
				else:
					self.pkgProcessed=False
			else:
				self._handleStepError()
											

		if self.endAction:
			self.pkgInstallProcessTimer.stop()
			self._endInstallProcess()

	#def pkgInstallProcessTimer

	def _endInstallProcess(self):
		
		if self.epiGuiManager.order>0:
			if self.error:
				self.showError=True
		else:
			if self.totalError>0:
				self.showError=True

		self.core.mainStack.isProgressBarVisible=False
		self.core.mainStack.endProcess=True
		self.core.mainStack.feedbackCode=""
		self.core.mainStack.isProcessRunning=False
		self.core.packageStack.showDependEpi=False
		self.core.packageStack.isAllInstalled=self.epiGuiManager.isAllInstalled()
		self.core.packageStack.totalErrorInProcess=self.totalError

		if self.showError:
			self.epiGuiManager.epiManager.zerocenter_feedback(self.epiGuiManager.order,"install",False)
			if self.countLimit==1:
				self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.epiGuiManager.feedBackCheck.get("msgCode"),"type":self.epiGuiManager.feedBackCheck.get("type")}
			else:
				self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.epiGuiManager.ERROR_PARTIAL_INSTALL,"type":self.epiGuiManager.KIRIGAMI_MSG_ERROR}
		else:
			self.epiGuiManager.epiManager.zerocenter_feedback(self.epiGuiManager.order,"install",True)
			self.core.mainStack.manageRemoveBtn(True)
			self.core.mainStack.enableApplyBtn=True
			self.core.packageStack.enablePkgList=True
			self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.epiGuiManager.feedBackCheck.get("msgCode"),"type":self.epiGuiManager.feedBackCheck.get("type")}

		
		self.epiGuiManager.clearEnvironment()

	#def _endInstallProcess

	def _handleStepError(self):
		
		self.error = True
		self.pkgProcessed = False
		self.core.packageStack.updateResultPackagesModel('end', "install")
		if self.epiGuiManager.order == 0:
			self.totalError += 1

	#def _handleStepError

	def _checkProcessTokens(self):

		if not self.pkgProcessed:
			for prefix, token in self.GLOBALTOKENS:
				if getattr(self.epiGuiManager, f"{prefix}Launched") and not getattr(self.epiGuiManager, f"{prefix}Done"):
					tmpToken=getattr(self.epiGuiManager,token)
					if not os.path.exists(tmpToken):
						setattr(self.epiGuiManager, f"{prefix}Done", True)
		else:
			for prefix, token in self.PROCESSPKGTOKENS:
				if getattr(self.epiGuiManager, f"{prefix}Launched") and not getattr(self.epiGuiManager, f"{prefix}Done"):
					tmpToken=getattr(self.epiGuiManager,token)
					if not os.path.exists(tmpToken):
						setattr(self.epiGuiManager, f"{prefix}Done", True)
			
	#def _checkProcessTokens

#class InstallStack

from . import Core

