#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import signal
import sys

signal.signal(signal.SIGINT, signal.SIG_DFL)

class CheckMetaProtection(QThread):

	metaProtectionChecked=Signal()

	def __init__(self, manager):

		super().__init__()
		self.manager=manager

	#def __init__

	def run(self):

		self.manager.checkRemoveMeta()
		self.metaProtectionChecked.emit()

	#def run

#class CheckMetaProtection

class UninstallStack(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		self.epiGuiManager=self.core.epiGuiManager

	#def __init__

	def checkMetaProtection(self):

		self.checkMetaProtectionT=CheckMetaProtection(self.epiGuiManager)
		self.checkMetaProtectionT.start()
		self.checkMetaProtectionT.metaProtectionChecked.connect(self._checkMetaProtectionRet)
		self.checkMetaProtectionT.finished.connect(self.checkMetaProtectionT.deleteLater)

	#def checkMetaProtection

	@Slot()
	def _checkMetaProtectionRet(self):

		if self.epiGuiManager.stopUninstall.get("stop"):
			self.core.mainStack.isProgressBarVisible=False
			self.core.mainStack.enableApplyBtn=True
			self.core.mainStack.endProcess=True
			self.core.packageStack.enablePkgList=True
			self.core.mainStack.feedbackCode=""
			self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.epiGuiManager.stopUninstall.get("code"),"type":self.epiGuiManager.KIRIGAMI_MSG_ERROR}
		else:
			self.core.mainStack.enableKonsole=True
			self.core.mainStack.feedbackCode=self.epiGuiManager.MSG_FEEDBACk_UNINSTALL_RUN
			self.core.mainStack.isProcessRunning=True
			self.core.mainStack.launchedProcess="uninstall"
			self.epiGuiManager.totalUninstallError=0
			self.core.packageStack.totalErrorInProcess=self.epiGuiManager.totalUninstallError
			self.endAction=False
			self.pkgProcessed=False
			countLimit=len(self.epiGuiManager.pkgSelectedFromList)
			if countLimit==0:
				self.countLimit=1
			else:
				self.countLimit=countLimit

			self.pkgToSelect=-1
			self.pkgToProcess=""
			self.uninstallProcessTimer=QTimer(None)
			self.uninstallProcessTimer.timeout.connect(self._uninstallProcessTimerRet)
			self.uninstallProcessTimer.start(100)		

	#def _checkMetaProtectionRet

	def _uninstallProcessTimerRet(self):

		if not self.pkgProcessed:
			if not self.endAction:
				self.pkgToSelect+=1
				if self.pkgToSelect<self.countLimit:
					try:
						self.pkgToProcess=self.epiGuiManager.pkgSelectedFromList[self.pkgToSelect]
						print(self.pkgToProcess)
					except:
						self.pkgToProcess="all"

					self.epiGuiManager.initUnInstallProcess(self.pkgToProcess)
					self.core.packageStack.updateResultPackagesModel('start',"uninstall")
					if not self.epiGuiManager.removePkgLaunched:
						self.epiGuiManager.removePkgLaunched=True
						self.core.mainStack.currentCommand=self.epiGuiManager.getUninstallCommand(self.pkgToProcess)
						self.core.mainStack.endCurrentCommand=True
				else:
					self.endAction=True

				self.pkgProcessed=True

		if not self.endAction:
			if not self.epiGuiManager.removePkgDone:
				return self._checkProcessToken()
		
			if not self.epiGuiManager.checkRemoveLaunched:
				self.epiGuiManager.checkRemoveLaunched=True
				self.epiGuiManager.checkRemove(self.pkgToProcess)

			if not self.epiGuiManager.checkRemoveDone:
				return;
		
			self.core.packageStack.updateResultPackagesModel("end","uninstall")
			self.pkgProcessed=False
		
		else:
			self.core.mainStack.isProgressBarVisible=False
			self.core.mainStack.isProcessRunning=False
			self.core.mainStack.endProcess=True
			self.core.mainStack.feedbackCode=""
			self.core.mainStack.enableApplyBtn=True
			self.core.packageStack.enablePkgList=True
			self.core.packageStack.isAllInstalled=self.epiGuiManager.isAllInstalled()
			self.core.packageStack.totalErrorInProcess=self.epiGuiManager.totalUninstallError
			self.core.mainStack.manageRemoveBtn(True)
			self.uninstallProcessTimer.stop()
			if self.epiGuiManager.totalUninstallError>0:
				self.epiGuiManager.epiManager.zerocenter_feedback(0,"uninstall",False)
			else:
				self.epiGuiManager.epiManager.zerocenter_feedback(0,"uninstall",True)
			
			getUninstallGlobalResult=self.epiGuiManager.getUninstallGlobalResult()
			self.core.mainStack.showStatusMessage={"show":True,"msgCode":getUninstallGlobalResult.get("msgCode"),"type":getUninstallGlobalResult.get("type")}
			self.epiGuiManager.epiManager.remove_repo_keys()
		
		if self.epiGuiManager.removePkgLaunched:
			if not self.epiGuiManager.removePkgDone:
				if not os.path.exists(self.epiGuiManager.tokenUninstall[1]):
					self.epiGuiManager.removePkgDone=True
		
	#def _uninstallProcessTimerRet

	def _checkProcessToken(self):

		processPkgToken=[
			("removePkg", "tokenUninstall")
		]

		for prefix, token in processPkgToken:
			if getattr(self.epiGuiManager, f"{prefix}Launched") and not getattr(self.epiGuiManager, f"{prefix}Done"):
				tmpToken=getattr(self.epiGuiManager,token)[1]
				if not os.path.exists(tmpToken):
					setattr(self.epiGuiManager, f"{prefix}Done", True)

	#def _checkProcessToken

#class UninstallStack

from . import Core

