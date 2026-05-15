#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import signal
import sys

signal.signal(signal.SIGINT, signal.SIG_DFL)

class InstallStack(QObject):

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
		self.installProcessTimer=QTimer(None)
		self.installProcessTimer.timeout.connect(self._installProcessTimerRet)
		self.installProcessTimer.start(100)		

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

	def _installProcessTimerRet(self):

		if not self.epiGuiManager.addRepositoryKeysLaunched:
			self.epiGuiManager.addRepositoryKeysLaunched=True
			self.core.mainStack.currentCommand=self.epiGuiManager.getAddRepositoryCommand()
			self.core.mainStack.endCurrentCommand=True

		if self.epiGuiManager.addRepositoryKeysDone:
			if not self.epiGuiManager.updateKeyRingLaunched:
				self.epiGuiManager.updateKeyRingLaunched=True
				self.core.mainStack.currentCommand=self.epiGuiManager.getUpdateKeyRingCommand() 
				self.core.mainStack.endCurrentCommand=True

			if self.epiGuiManager.updateKeyRingDone:
				if not self.epiGuiManager.checkArquitectureLaunched:
					self.core.mainStack.feedbackCode=self.epiGuiManager.MSG_FEEDBACK_INSTALL_ARQUITECTURE
					self.epiGuiManager.checkArquitectureLaunched=True
					self.core.mainStack.currentCommand=self.epiGuiManager.getCheckArquitectureCommand()
					self.core.mainStack.endCurrentCommand=True

				if self.epiGuiManager.checkArquitectureDone:
					if not self.epiGuiManager.updateReposLaunched:
						self.core.mainStack.feedbackCode=self.epiGuiManager.MSG_FEEDBACK_INSTALL_REPOSITORIES
						self.epiGuiManager.updateReposLaunched=True
						self.core.mainStack.currentCommand=self.epiGuiManager.getUpdateReposCommand()
						self.core.mainStack.endCurrentCommand=True

					if self.epiGuiManager.updateReposDone:
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
							if self.epiGuiManager.downloadAppDone:
								if not self.epiGuiManager.checkDownloadLaunched:
									self.epiGuiManager.checkDownloadLaunched=True
									self.epiGuiManager.checkDownload(self.pkgToProcess)

								if self.epiGuiManager.checkDownloadDone:
									if self.epiGuiManager.feedBackCheck.get("status"):
										if not self.epiGuiManager.preInstallAppLaunched:
											self.core.mainStack.feedbackCode=self.epiGuiManager.MSG_FEEDBACK_INSTALL_PREINSTALL
											self.epiGuiManager.preInstallAppLaunched=True
											self.core.mainStack.currentCommand=self.epiGuiManager.getPreInstallCommand(self.pkgToProcess)
											self.core.mainStack.endCurrentCommand=True

										if self.epiGuiManager.preInstallAppDone:
											if not self.epiGuiManager.checkPreInstallLaunched:
												self.epiGuiManager.checkPreInstallLaunched=True
												self.epiGuiManager.checkPreInstall(self.pkgToProcess)

											if self.epiGuiManager.checkPreInstallDone:
												if self.epiGuiManager.feedBackCheck.get("status"):
													if not self.epiGuiManager.installAppLaunched:
														self.core.mainStack.feedbackCode=self.epiGuiManager.MSG_FEEDBACK_INSTALL_INSTALL
														self.epiGuiManager.installAppLaunched=True
														self.core.mainStack.currentCommand=self.epiGuiManager.getInstallCommand(self.pkgToProcess)
														self.core.mainStack.endCurrentCommand=True

													if self.epiGuiManager.installAppDone:
														if not self.epiGuiManager.checkInstallLaunched:
															self.epiGuiManager.checkInstallLaunched=True
															self.epiGuiManager.checkInstall(self.pkgToProcess)

														if self.epiGuiManager.checkInstallDone:
															if self.epiGuiManager.feedBackCheck.get("status"):
																if not self.epiGuiManager.postInstallAppLaunched:
																	self.core.mainStack.feedbackCode=self.epiGuiManager.MSG_FEEDBACK_INSTALL_ENDING
																	self.epiGuiManager.postInstallAppLaunched=True
																	self.core.mainStack.currentCommand=self.epiGuiManager.getPostInstallCommand(self.pkgToProcess)
																	self.core.mainStack.endCurrentCommand=True
																if self.epiGuiManager.postInstallAppDone:
																	if not self.epiGuiManager.checkPostInstallLaunched:
																		self.epiGuiManager.checkPostInstallLaunched=True
																		self.epiGuiManager.checkPostInstall(self.pkgToProcess)
																	if self.epiGuiManager.checkPostInstallDone:
																		self.core.packageStack.updateResultPackagesModel('end',"install")

																		if self.epiGuiManager.feedBackCheck.get("status"):
																			self.core.packageStack.showDependEpi=False
																			if self.epiGuiManager.order>0:
																				self.epiGuiManager.epiManager.zerocenter_feedback(self.epiGuiManager.order,"install",True)
																				self._initInstallProcess()
																			else:
																				self.pkgProcessed=False
																			
																		else:
																			self.error=True
																			self.pkgProcessed=False
																			self.core.packageStack.updateResultPackagesModel('end',"install")
																			if self.epiGuiManager.order==0:
																				self.totalError+=1
															else:
																self.error=True
																self.pkgProcessed=False
																self.core.packageStack.updateResultPackagesModel('end',"install")
																if self.epiGuiManager.order==0:
																	self.totalError+=1
												else:
													self.error=True
													self.pkgProcessed=False
													self.core.packageStack.updateResultPackagesModel('end',"install")
													if self.epiGuiManager.order==0:
														self.totalError+=1
									else:
										self.error=True
										self.pkgProcessed=False
										self.core.packageStack.updateResultPackagesModel('end',"install")
										if self.epiGuiManager.order==0:
											self.totalError+=1

		if self.endAction:
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
			self.installProcessTimer.stop()

			if self.showError:
				self.epiGuiManager.epiManager.zerocenter_feedback(self.epiGuiManager.order,"install",False)
				if self.countLimit==1:
					self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.epiGuiManager.feedBackCheck.get("msgCode"),"type":self.epiGuiManager.feedBackCheck.get("type")}
				else:
					self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.epiGuiManager.ERROR_PARTIAL_INSTALL,"type":self.epiGuiManager.KIRIGAMI_MSG_ERROR}
				self.epiGuiManager.clearEnvironment()
			else:
				self.epiGuiManager.epiManager.zerocenter_feedback(self.epiGuiManager.order,"install",True)
				self.core.mainStack.manageRemoveBtn(True)
				self.core.mainStack.enableApplyBtn=True
				self.core.packageStack.enablePkgList=True
				self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.epiGuiManager.feedBackCheck.get("msgCode"),"type":self.epiGuiManager.feedBackCheck.get("type")}
				self.epiGuiManager.clearEnvironment()

		if self.epiGuiManager.addRepositoryKeysLaunched:
			if not self.epiGuiManager.addRepositoryKeysDone:
				if not os.path.exists(self.epiGuiManager.tokenKeys[1]):
					self.epiGuiManager.addRepositoryKeysDone=True

		if self.epiGuiManager.updateKeyRingLaunched:
			if not self.epiGuiManager.updateKeyRingDone:
				if not os.path.exists(self.epiGuiManager.tokenKeyring[1]):
					self.epiGuiManager.updateKeyRingDone=True

		if self.epiGuiManager.checkArquitectureLaunched:
			if not self.epiGuiManager.checkArquitectureDone:
				if not os.path.exists(self.epiGuiManager.tokenArquitecture[1]):
					self.epiGuiManager.checkArquitectureDone=True

		if self.epiGuiManager.updateReposLaunched:
			if not self.epiGuiManager.updateReposDone:
				if not os.path.exists(self.epiGuiManager.tokenUpdaterepos[1]):
					self.epiGuiManager.updateReposDone=True

		if self.pkgProcessed:
			if self.epiGuiManager.downloadAppLaunched:
				if not self.epiGuiManager.downloadAppDone:
					if not os.path.exists(self.epiGuiManager.tokenDownload[1]):
						self.epiGuiManager.downloadAppDone=True

			if self.epiGuiManager.preInstallAppLaunched:
				if not self.epiGuiManager.preInstallAppDone:
					if not os.path.exists(self.epiGuiManager.tokenPreInstall[1]):
						self.epiGuiManager.preInstallAppDone=True

			if self.epiGuiManager.installAppLaunched:
				if not self.epiGuiManager.installAppDone:
					if not os.path.exists(self.epiGuiManager.tokenInstall[1]):
						self.epiGuiManager.installAppDone=True

			if self.epiGuiManager.postInstallAppLaunched:
				if not self.epiGuiManager.postInstallAppDone:
					if not os.path.exists(self.epiGuiManager.tokenPostInstall[1]):
						self.epiGuiManager.postInstallAppDone=True
	
	#def _installProcessTimerRet

#class InstallStack

from . import Core

