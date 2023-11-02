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

class CheckMetaProtection(QThread):

	def __init__(self, *args):

		QThread.__init__(self)

	#def __init__

	def run(self):

		UninstallStack.epiGuiManager.checkRemoveMeta()

	#def run

#class CheckMetaProtection

class UninstallStack(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		UninstallStack.epiGuiManager=self.core.epiGuiManager

	#def __init__

	def checkMetaProtection(self):

		self.checkMetaProtectionT=CheckMetaProtection()
		self.checkMetaProtectionT.start()
		self.checkMetaProtectionT.finished.connect(self._checkMetaProtectionRet)

	#def checkMetaProtection

	def _checkMetaProtectionRet(self):

		if UninstallStack.epiGuiManager.stopUninstall[0]:
			self.core.mainStack.isProgressBarVisible=False
			self.core.mainStack.enableApplyBtn=True
			self.core.mainStack.endProcess=True
			self.core.packageStack.enablePkgList=True
			self.core.mainStack.feedbackCode=""
			self.core.mainStack.showStatusMessage=[True,UninstallStack.epiGuiManager.stopUninstall[1],"Error"]
		else:
			self.core.mainStack.enableKonsole=True
			self.core.mainStack.feedbackCode=UninstallStack.epiGuiManager.MSG_FEEDBACk_UNINSTALL_RUN
			self.core.mainStack.isProcessRunning=True
			self.core.mainStack.launchedProcess="uninstall"
			UninstallStack.epiGuiManager.totalUninstallError=0
			self.endAction=False
			self.pkgProcessed=False
			countLimit=len(UninstallStack.epiGuiManager.pkgSelectedFromList)
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
						self.pkgToProcess=UninstallStack.epiGuiManager.pkgSelectedFromList[self.pkgToSelect]
					except:
						self.pkgToProcess="all"

					UninstallStack.epiGuiManager.initUnInstallProcess(self.pkgToProcess)
					self.core.packageStack.updateResultPackagesModel('start',"uninstall")
					if not UninstallStack.epiGuiManager.removePkgLaunched:
						UninstallStack.epiGuiManager.removePkgLaunched=True
						self.core.mainStack.currentCommand=UninstallStack.epiGuiManager.getUninstallCommand(self.pkgToProcess)
						self.core.mainStack.endCurrentCommand=True
				else:
					self.endAction=True

				self.pkgProcessed=True

		if not self.endAction:
			if UninstallStack.epiGuiManager.removePkgDone:
				if not UninstallStack.epiGuiManager.checkRemoveLaunched:
					UninstallStack.epiGuiManager.checkRemoveLaunched=True
					UninstallStack.epiGuiManager.checkRemove(self.pkgToProcess)

				if UninstallStack.epiGuiManager.checkRemoveDone:
					self.core.packageStack.updateResultPackagesModel("end","uninstall")
					self.pkgProcessed=False
		
		else:
			self.core.mainStack.isProgressBarVisible=False
			self.core.mainStack.isProcessRunning=False
			self.core.mainStack.endProcess=True
			self.core.mainStack.feedbackCode=""
			self.core.mainStack.enableApplyBtn=True
			self.core.packageStack.enablePkgList=True
			self.core.packageStack.isAllInstalled=UninstallStack.epiGuiManager.isAllInstalled()
			self.core.mainStack.manageRemoveBtn(True)
			self.uninstallProcessTimer.stop()
			if UninstallStack.epiGuiManager.totalUninstallError>0:
				UninstallStack.epiGuiManager.epiManager.zerocenter_feedback(0,"uninstall",False)
			else:
				UninstallStack.epiGuiManager.epiManager.zerocenter_feedback(0,"uninstall",True)
			
			getUninstallGlobalResult=UninstallStack.epiGuiManager.getUninstallGlobalResult()
			self.core.mainStack.showStatusMessage=[True,getUninstallGlobalResult[0],getUninstallGlobalResult[1]]
			UninstallStack.epiGuiManager.epiManager.remove_repo_keys()
		
		if UninstallStack.epiGuiManager.removePkgLaunched:
			if not UninstallStack.epiGuiManager.removePkgDone:
				if not os.path.exists(UninstallStack.epiGuiManager.tokenUninstall[1]):
					UninstallStack.epiGuiManager.removePkgDone=True
		
	#def _uninstallProcessTimerRet

#class UninstallStack

from . import Core

