#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys
import pwd

signal.signal(signal.SIGINT, signal.SIG_DFL)

class InstallStack(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		InstallStack.epiGuiManager=self.core.epiGuiManager

	#def __init__

	def checkInternetConnection(self):

		InstallStack.epiGuiManager.checkInternetConnection()
		self.checkConnectionTimer=QTimer()
		self.checkConnectionTimer.timeout.connect(self._checkConnectionTimerRet)
		self.checkConnectionTimer.start(1000)

	#def checkInternetConnection

	def _checkConnectionTimerRet(self):

		InstallStack.epiGuiManager.getResultCheckConnection()
		if InstallStack.epiGuiManager.endCheck:
			self.checkConnectionTimer.stop()
			self.core.mainStack.feedbackCode=0
			if InstallStack.epiGuiManager.retConnection[0]:
				self.core.mainStack.isProgressBarVisible=False
				self.core.mainStack.endProcess=True
				self.core.mainStack.enableApplyBtn=True
				self.core.mainStack.showStatusMessage=[True,InstallStack.epiGuiManager.retConnection[1],"Error"]
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
		self.launchedProcess="install"
		self._initInstallProcess()
		self.installProcessTimer=QTimer(None)
		self.installProcessTimer.timeout.connect(self._installProcessTimerRet)
		self.installProcessTimer.start(100)		

	#def _installProcess

	def _initInstallProcess(self):

		self.core.mainStack.feedbackCode=InstallStack.epiGuiManager.MSG_FEEDBACK_INSTALL_GATHER
		InstallStack.epiGuiManager.initInstallProcess()
		self.core.mainStack.isProcessRunning=True
		self.error=False
		self.showError=False
		self.endAction=False
		self.pkgProcessed=False
		countLimit=len(InstallStack.epiGuiManager.pkgSelectedFromList)
		if countLimit==0:
			self.countLimit=1
		else:
			self.countLimit=countLimit

		self.pkgToSelect=-1
		self.pkgToProcess=""

	#def _initInstallProcess

	def _installProcessTimerRet(self):

		if not InstallStack.epiGuiManager.addRepositoryKeysLaunched:
			InstallStack.epiGuiManager.addRepositoryKeysLaunched=True
			self.core.mainStack.currentCommand=InstallStack.epiGuiManager.getAddRepositoryCommand()
			self.core.mainStack.endCurrentCommand=True

		if InstallStack.epiGuiManager.addRepositoryKeysDone:
			if not InstallStack.epiGuiManager.updateKeyRingLaunched:
				InstallStack.epiGuiManager.updateKeyRingLaunched=True
				self.core.mainStack.currentCommand=InstallStack.epiGuiManager.getUpdateKeyRingCommand() 
				self.core.mainStack.endCurrentCommand=True

			if InstallStack.epiGuiManager.updateKeyRingDone:
				if not InstallStack.epiGuiManager.checkArquitectureLaunched:
					self.core.mainStack.feedbackCode=InstallStack.epiGuiManager.MSG_FEEDBACK_INSTALL_ARQUITECTURE
					InstallStack.epiGuiManager.checkArquitectureLaunched=True
					self.core.mainStack.currentCommand=InstallStack.epiGuiManager.getCheckArquitectureCommand()
					self.core.mainStack.endCurrentCommand=True

				if InstallStack.epiGuiManager.checkArquitectureDone:
					if not InstallStack.epiGuiManager.updateReposLaunched:
						self.core.mainStack.feedbackCode=InstallStack.epiGuiManager.MSG_FEEDBACK_INSTALL_REPOSITORIES
						InstallStack.epiGuiManager.updateReposLaunched=True
						self.core.mainStack.currentCommand=InstallStack.epiGuiManager.getUpdateReposCommand()
						self.core.mainStack.endCurrentCommand=True

					if InstallStack.epiGuiManager.updateReposDone:
						if not self.pkgProcessed:
							if InstallStack.epiGuiManager.order!=0:
								if self.error:
									self.endAction=True
								else:
									self.error=False
							
							if not self.endAction:
								self.pkgToSelect+=1
								if self.pkgToSelect<self.countLimit:
									if InstallStack.epiGuiManager.order==0:
										try:
											self.pkgToProcess=InstallStack.epiGuiManager.pkgSelectedFromList[self.pkgToSelect]
										except:
											self.pkgToProcess="all"
									else:
										self.pkgToProcess="all"

									InstallStack.epiGuiManager.initPkgInstallProcess(self.pkgToProcess)
									self.core.packageStack.updateResultPackagesModel('start',"install")
									if InstallStack.epiGuiManager.order>0:
										self.core.packageStack.showDependEpi=True
										self.core.packageStack.showDependLabel=True
									if not InstallStack.epiGuiManager.downloadAppLaunched:
										self.core.mainStack.feedbackCode=InstallStack.epiGuiManager.MSG_FEEDBACK_INSTALL_DOWNLOAD
										InstallStack.epiGuiManager.downloadAppLaunched=True
										self.core.mainStack.currentCommand=InstallStack.epiGuiManager.getDownloadAppCommand(self.pkgToProcess)
										self.core.mainStack.endCurrentCommand=True

								else:
									self.endAction=True

							self.pkgProcessed=True

						if not self.endAction:
							if InstallStack.epiGuiManager.downloadAppDone:
								if not InstallStack.epiGuiManager.checkDownloadLaunched:
									InstallStack.epiGuiManager.checkDownloadLaunched=True
									InstallStack.epiGuiManager.checkDownload(self.pkgToProcess)

								if InstallStack.epiGuiManager.checkDownloadDone:
									if InstallStack.epiGuiManager.feedBackCheck[0]:
										if not InstallStack.epiGuiManager.preInstallAppLaunched:
											self.core.mainStack.feedbackCode=InstallStack.epiGuiManager.MSG_FEEDBACK_INSTALL_PREINSTALL
											InstallStack.epiGuiManager.preInstallAppLaunched=True
											self.core.mainStack.currentCommand=InstallStack.epiGuiManager.getPreInstallCommand(self.pkgToProcess)
											self.core.mainStack.endCurrentCommand=True

										if InstallStack.epiGuiManager.preInstallAppDone:
											if not InstallStack.epiGuiManager.checkPreInstallLaunched:
												InstallStack.epiGuiManager.checkPreInstallLaunched=True
												InstallStack.epiGuiManager.checkPreInstall(self.pkgToProcess)

											if InstallStack.epiGuiManager.checkPreInstallDone:
												if InstallStack.epiGuiManager.feedBackCheck[0]:
													if not InstallStack.epiGuiManager.installAppLaunched:
														self.core.mainStack.feedbackCode=InstallStack.epiGuiManager.MSG_FEEDBACK_INSTALL_INSTALL
														InstallStack.epiGuiManager.installAppLaunched=True
														self.core.mainStack.currentCommand=InstallStack.epiGuiManager.getInstallCommand(self.pkgToProcess)
														self.core.mainStack.endCurrentCommand=True

													if InstallStack.epiGuiManager.installAppDone:
														if not InstallStack.epiGuiManager.checkInstallLaunched:
															InstallStack.epiGuiManager.checkInstallLaunched=True
															InstallStack.epiGuiManager.checkInstall(self.pkgToProcess)

														if InstallStack.epiGuiManager.checkInstallDone:
															if InstallStack.epiGuiManager.feedBackCheck[0]:
																if not InstallStack.epiGuiManager.postInstallAppLaunched:
																	self.core.mainStack.feedbackCode=InstallStack.epiGuiManager.MSG_FEEDBACK_INSTALL_ENDING
																	InstallStack.epiGuiManager.postInstallAppLaunched=True
																	self.core.mainStack.currentCommand=InstallStack.epiGuiManager.getPostInstallCommand(self.pkgToProcess)
																	self.core.mainStack.endCurrentCommand=True
																if InstallStack.epiGuiManager.postInstallAppDone:
																	if not InstallStack.epiGuiManager.checkPostInstallLaunched:
																		InstallStack.epiGuiManager.checkPostInstallLaunched=True
																		InstallStack.epiGuiManager.checkPostInstall(self.pkgToProcess)
																	if InstallStack.epiGuiManager.checkPostInstallDone:
																		self.core.packageStack.updateResultPackagesModel('end',"install")

																		if InstallStack.epiGuiManager.feedBackCheck[0]:
																			self.core.packageStack.showDependEpi=False
																			if InstallStack.epiGuiManager.order>0:
																				InstallStack.epiGuiManager.epiManager.zerocenter_feedback(InstallStack.epiGuiManager.order,"install",True)
																				self._initInstallProcess()
																			else:
																				self.pkgProcessed=False
																			
																		else:
																			self.error=True
																			self.pkgProcessed=False
																			self.core.packageStack.updateResultPackagesModel('end',"install")
																			if InstallStack.epiGuiManager.order==0:
																				self.totalError+=1
															else:
																self.error=True
																self.pkgProcessed=False
																self.core.packageStack.updateResultPackagesModel('end',"install")
																if InstallStack.epiGuiManager.order==0:
																	self.totalError+=1
												else:
													self.error=True
													self.pkgProcessed=False
													self.core.packageStack.updateResultPackagesModel('end',"install")
													if InstallStack.epiGuiManager.order==0:
														self.totalError+=1
									else:
										self.error=True
										self.pkgProcessed=False
										self.core.packageStack.updateResultPackagesModel('end',"install")
										if InstallStack.epiGuiManager.order==0:
											self.totalError+=1

		if self.endAction:
			if InstallStack.epiGuiManager.order>0:
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
			self.core.packageStack.isAllInstalled=InstallStack.epiGuiManager.isAllInstalled()
			self.installProcessTimer.stop()

			if self.showError:
				InstallStack.epiGuiManager.epiManager.zerocenter_feedback(InstallStack.epiGuiManager.order,"install",False)
				if self.countLimit==1:
					self.core.mainStack.showStatusMessage=[True,InstallStack.epiGuiManager.feedBackCheck[1],InstallStack.epiGuiManager.feedBackCheck[2]]
				else:
					self.core.mainStack.showStatusMessage=[True,InstallStack.epiGuiManager.ERROR_PARTIAL_INSTALL,"Error"]
				InstallStack.epiGuiManager.clearEnvironment()
			else:
				InstallStack.epiGuiManager.epiManager.zerocenter_feedback(InstallStack.epiGuiManager.order,"install",True)
				self.core.mainStack.manageRemoveBtn(True)
				self.core.mainStack.enableApplyBtn=True
				self.core.packageStack.enablePkgList=True
				self.core.mainStack.showStatusMessage=[True,InstallStack.epiGuiManager.feedBackCheck[1],InstallStack.epiGuiManager.feedBackCheck[2]]
				InstallStack.epiGuiManager.clearEnvironment()

		if InstallStack.epiGuiManager.addRepositoryKeysLaunched:
			if not InstallStack.epiGuiManager.addRepositoryKeysDone:
				if not os.path.exists(InstallStack.epiGuiManager.tokenKeys[1]):
					InstallStack.epiGuiManager.addRepositoryKeysDone=True

		if InstallStack.epiGuiManager.updateKeyRingLaunched:
			if not InstallStack.epiGuiManager.updateKeyRingDone:
				if not os.path.exists(InstallStack.epiGuiManager.tokenKeyring[1]):
					InstallStack.epiGuiManager.updateKeyRingDone=True

		if InstallStack.epiGuiManager.checkArquitectureLaunched:
			if not InstallStack.epiGuiManager.checkArquitectureDone:
				if not os.path.exists(InstallStack.epiGuiManager.tokenArquitecture[1]):
					InstallStack.epiGuiManager.checkArquitectureDone=True

		if InstallStack.epiGuiManager.updateReposLaunched:
			if not InstallStack.epiGuiManager.updateReposDone:
				if not os.path.exists(InstallStack.epiGuiManager.tokenUpdaterepos[1]):
					InstallStack.epiGuiManager.updateReposDone=True

		if self.pkgProcessed:
			if InstallStack.epiGuiManager.downloadAppLaunched:
				if not InstallStack.epiGuiManager.downloadAppDone:
					if not os.path.exists(InstallStack.epiGuiManager.tokenDownload[1]):
						InstallStack.epiGuiManager.downloadAppDone=True

			if InstallStack.epiGuiManager.preInstallAppLaunched:
				if not InstallStack.epiGuiManager.preInstallAppDone:
					if not os.path.exists(InstallStack.epiGuiManager.tokenPreInstall[1]):
						InstallStack.epiGuiManager.preInstallAppDone=True

			if InstallStack.epiGuiManager.installAppLaunched:
				if not InstallStack.epiGuiManager.installAppDone:
					if not os.path.exists(InstallStack.epiGuiManager.tokenInstall[1]):
						InstallStack.epiGuiManager.installAppDone=True

			if InstallStack.epiGuiManager.postInstallAppLaunched:
				if not InstallStack.epiGuiManager.postInstallAppDone:
					if not os.path.exists(InstallStack.epiGuiManager.tokenPostInstall[1]):
						InstallStack.epiGuiManager.postInstallAppDone=True
	
	#def _installProcessTimerRet

#class InstallStack

from . import Core

