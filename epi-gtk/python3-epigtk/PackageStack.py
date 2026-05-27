#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import subprocess
import signal
import sys

from . import PackagesModel

signal.signal(signal.SIGINT, signal.SIG_DFL)

class GetPkgInfo(QThread):

	pkgInfoGetted=Signal('QVariant')

	def __init__(self,manager,pkgId):

		super().__init__()
		self.manager=manager
		self.pkgId=pkgId

	#def __init__

	def run(self):

		ret=self.manager.getStoreInfo(self.pkgId)
		self.pkgInfoGetted.emit(ret)

	#def run

#class GetPkgInfo

class Bridge(QObject):

	currentPkgOptionChanged=Signal()
	uncheckAllChanged=Signal()
	selectPkgChanged=Signal()
	enablePkgListChanged=Signal()
	eulaUrlChanged=Signal()
	currentEulaPkgChanged=Signal()
	wikiUrlChanged=Signal()
	showDependEpiChanged=Signal()
	showDependLabelChanged=Signal()
	pkgStoreInfoChanged=Signal()
	isAllInstalledChanged=Signal()
	filterStatusValueChanged=Signal()
	totalErrorInProcessChanged=Signal()
	appFromStoreChanged=Signal()


	def __init__(self):

		super().__init__()
		self.core=Core.Core.get_core()
		self.epiGuiManager=self.core.epiGuiManager
		self._packagesModel=PackagesModel.PackagesModel()
		self._currentPkgOption=0
		self._uncheckAll=True
		self._selectPkg=False
		self._enablePkgList=True
		self._eulaUrl=""
		self._currentEulaPkg=""
		self._wikiUrl=""
		self._showDependEpi=False
		self._showDependLabel=False
		self._launchedProcess=""
		self._pkgStoreInfo={"icon":'',"name":'',"summary":'',"description":''}
		self._isAllInstalled={"allInstalled":False,"allAvailable":False}
		self._filterStatusValue="all"
		self._totalErrorInProcess=0
		self.getPkgInfoRunning=False
		self._appFromStore=""

	#def __init__

	@Property(int,notify=currentPkgOptionChanged)
	def currentPkgOption(self):

		return self._currentPkgOption

	#def currentPkgOption

	@currentPkgOption.setter
	def currentPkgOption(self,currentPkgOption):

		if self._currentPkgOption!=currentPkgOption:
			self._currentPkgOption=currentPkgOption
			self.currentPkgOptionChanged.emit()

	#def currentPkgOption

	@Property(bool,notify=uncheckAllChanged)	
	def uncheckAll(self):

		return self._uncheckAll

	#def uncheckAll

	@uncheckAll.setter
	def uncheckAll(self,uncheckAll):

		if self._uncheckAll!=uncheckAll:
			self._uncheckAll=uncheckAll
			self.uncheckAllChanged.emit()

	#def uncheckAll

	@Property(bool,notify=selectPkgChanged)
	def selectPkg(self):

		return self._selectPkg

	#def selectPkg

	@selectPkg.setter
	def selectPkg(self,selectPkg):

		if self._selectPkg!=selectPkg:
			self._selectPkg=selectPkg
			self.selectPkgChanged.emit()

	#def selectPkg

	@Property(bool,notify=enablePkgListChanged)
	def enablePkgList(self):

		return self._enablePkgList

	#def enablePkgList

	@enablePkgList.setter
	def enablePkgList(self,enablePkgList):

		if self._enablePkgList!=enablePkgList:
			self._enablePkgList=enablePkgList
			self.enablePkgListChanged.emit()

	#def enablePkgList

	@Property(str,notify=eulaUrlChanged)
	def eulaUrl(self):

		return self._eulaUrl

	#def eulaUrl

	@eulaUrl.setter
	def eulaUrl(self,eulaUrl):

		if self._eulaUrl!=eulaUrl:
			self._eulaUrl=eulaUrl
			self.eulaUrlChanged.emit()

	#def eulaUrl

	@Property(str,notify=currentEulaPkgChanged)
	def currentEulaPkg(self):

		return self._currentEulaPkg

	#def currentEulaPkg

	@currentEulaPkg.setter
	def currentEulaPkg(self,currentEulaPkg):

		if self._currentEulaPkg!=currentEulaPkg:
			self._currentEulaPkg=currentEulaPkg
			self.currentEulaPkgChanged.emit()

	#def currentEulaPkg
	
	@Property(str,notify=wikiUrlChanged)
	def wikiUrl(self):

		return self._wikiUrl

	#def wikiUrl

	@wikiUrl.setter
	def wikiUrl(self,wikiUrl):

		if self._wikiUrl!=wikiUrl:
			self._wikiUrl=wikiUrl
			self.wikiUrlChanged.emit()

	#def wikiUrl
	
	@Property(bool,notify=showDependEpiChanged)
	def showDependEpi(self):

		return self._showDependEpi

	#def showDependEpi

	@showDependEpi.setter
	def showDependEpi(self,showDependEpi):

		if self._showDependEpi!=showDependEpi:
			self._showDependEpi=showDependEpi
			self.showDependEpiChanged.emit()

	#def showDependEpi

	@Property(bool,notify=showDependLabelChanged)
	def showDependLabel(self):

		return self._showDependLabel

	#def showDependLabel

	@showDependLabel.setter
	def showDependLabel(self,showDependLabel):

		if self._showDependLabel!=showDependLabel:
			self._showDependLabel=showDependLabel
			self.showDependLabelChanged.emit()

	#def showDependLabel	

	@Property('QVariant',notify=pkgStoreInfoChanged)
	def pkgStoreInfo(self):

		return self._pkgStoreInfo

	#def pkgStoreInfo

	@pkgStoreInfo.setter
	def pkgStoreInfo(self,pkgStoreInfo):

		if self._pkgStoreInfo!=pkgStoreInfo:
			self._pkgStoreInfo=pkgStoreInfo
			self.pkgStoreInfoChanged.emit()
	
	#def pkgStoreInfo

	@Property('QVariant',notify=isAllInstalledChanged)
	def isAllInstalled(self):
		return self._isAllInstalled

	#def isAllInstalled

	@isAllInstalled.setter
	def isAllInstalled(self,isAllInstalled):

		if self._isAllInstalled!=isAllInstalled:
			self._isAllInstalled=isAllInstalled
			self.isAllInstalledChanged.emit()

	#def isAllInstalled

	@Property(str,notify=filterStatusValueChanged)
	def filterStatusValue(self):

		return self._filterStatusValue

	#def filterStatusValue

	@filterStatusValue.setter
	def filterStatusValue(self,filterStatusValue):

		if self._filterStatusValue!=filterStatusValue:
			self._filterStatusValue=filterStatusValue
			self.filterStatusValueChanged.emit()

	#def filterStatusValue

	@Property(int,notify=totalErrorInProcessChanged)
	def totalErrorInProcess(self):

		return self._totalErrorInProcess

	#def totalErrorInProcess

	@totalErrorInProcess.setter
	def totalErrorInProcess(self,totalErrorInProcess):

		if self._totalErrorInProcess!=totalErrorInProcess:
			self._totalErrorInProcess=totalErrorInProcess
			self.totalErrorInProcessChanged.emit()

	#def totalErrorInProcess	

	@Property(str,notify=appFromStoreChanged)
	def appFromStore(self):

		return self._appFromStore

	#def appFromStore

	@appFromStore.setter
	def appFromStore(self,appFromStore):

		if self._appFromStore!=appFromStore:
			self._appFromStore=appFromStore
			self.appFromStoreChanged.emit()

	#def appFromStore

	def _getPackagesModel(self):

		return self._packagesModel

	#def _getPackagesModel

	def showInfo(self):

		self._updatePackagesModel()
		self.uncheckAll=self.epiGuiManager.uncheckAll
		self.selectPkg=self.epiGuiManager.selectPkg
		self.wikiUrl=self.epiGuiManager.wikiUrl
		self.isAllInstalled=self.epiGuiManager.isAllInstalled()
		self.appFromStore=self.epiGuiManager.appFromStore

	#def showInfo

	def _updatePackagesModel(self):

		ret=self._packagesModel.clear()
		packagesEntries=self.epiGuiManager.packagesData
		for item in packagesEntries:
			if item["pkgId"]!="":
				self._packagesModel.appendRow(item["pkgId"],item["showCb"],item["isChecked"],item["customName"],item["pkgIcon"],item["status"],item["isVisible"],item["resultProcess"],item["order"],item["showSpinner"],item["entryPoint"],item["metaInfo"])

	#def _updatePackagesModel

	@Slot('QVariantList')
	def onCheckPkg(self,info):

		self.epiGuiManager.onCheckedPackages(info[0],info[1])
		self._refreshInfo()

	#def onCheckPkg

	@Slot()
	def selectAll(self):

		self.epiGuiManager.selectAll()
		self.filterStatusValue="all"
		self._refreshInfo()
		
	#def selectAll

	def _refreshInfo(self):

		params=[]
		params.append("isChecked")
		self._updatePackagesModelInfo(params)
		self.uncheckAll=self.epiGuiManager.uncheckAll
		if len(self.epiGuiManager.epiManager.packages_selected)>0:
			self.core.mainStack.enableApplyBtn=True
			self.core.mainStack.manageRemoveBtn(True)
		else:
			self.core.mainStack.enableApplyBtn=False
			self.core.mainStack.manageRemoveBtn(False)

	#def _refreshInfo

	def getEulas(self):

		if not self.epiGuiManager.eulaAccepted:
			self.epiGuiManager.getEulasToCheck()
			if len(self.epiGuiManager.eulasToCheck)>0:
				self._manageEulas()
			else:
				self.core.installStack.installProcess()
		else:
			self.core.installStack.installProcess()

	#def _getEulas

	def _manageEulas(self):

		nextStep=False
		if len(self.epiGuiManager.eulasToCheck)>0:
			self.core.mainStack.enableApplyBtn=True
			self.core.mainStack.enableRemoveBtn=True
			self.eulaUrl=self.epiGuiManager.eulasToCheck[self.epiGuiManager.eulaOrder]["eula"]
			self.core.mainStack.feedbackCode=self.epiGuiManager.MSG_FEEDBACK_EULA
			self.currentEulaPkg=self.epiGuiManager.eulasToCheck[self.epiGuiManager.eulaOrder]["pkg_name"]
			self.currentPkgOption=1
		else:
			self.currentPkgOption=0
			self.currentEulaPkg=""
			if self.epiGuiManager.eulaAccepted:
				if len(self.epiGuiManager.epiManager.packages_selected)>0:
					nextStep=True
			else:
				nextStep=False

			if nextStep:
				self.core.installStack.installProcess()
			else:
				self.core.mainStack.endProcess=True
				self.core.mainStack.feedbackCode=""
				self.enablePkgList=True
				if not self.selectPkg:
					self.core.mainStack.enableApplyBtn=True
					self.core.mainStack.enableRemoveBtn=True

	#def _manageEulas

	@Slot()
	def acceptEula(self):

		self.epiGuiManager.acceptEula()
		self._manageEulas()

	#def acceptEula	

	@Slot()
	def rejectEula(self):

		self.epiGuiManager.rejectEula()
		if self.selectPkg:
			self._refreshInfo()
		self._manageEulas()

	#def rejectEula

	def updateResultPackagesModel(self,step,action):

		params=[]
		params.append("showSpinner")
		params.append("resultProcess")
		if step=="start" and action=="install":
			if self.epiGuiManager.order>0:
				params.append("isVisible")
		if step=="end":
			params.append("pkgIcon")
			params.append("status")

		self._updatePackagesModelInfo(params)

	#def updateResultPackagesModel

	def _updatePackagesModelInfo(self,params):

		updatedInfo=self.epiGuiManager.packagesData
		if len(updatedInfo)>0:
			for i in range(len(updatedInfo)):
				valuesToUpdate=[]
				index=self._packagesModel.index(i)
				for item in params:
					tmp={}
					tmp[item]=updatedInfo[i][item]
					valuesToUpdate.append(tmp)
				self._packagesModel.setData(index,valuesToUpdate)
	
	#def _updatePackagesModelInfo

	@Slot('QVariantList')
	def showPkgInfo(self,params):

		if not self.getPkgInfoRunning:

			self.core.mainStack.showStatusMessage={"show":False,"msgCode":'',"type":''}

			if params[0]==0:
				self.getPkgInfoRunning=True
				self.core.mainStack.feedbackCode=self.epiGuiManager.MSG_FEEDBACK_STORE_INFO
				self.getPkgInfoT=GetPkgInfo(self.epiGuiManager,params[1])
				self.getPkgInfoT.start()
				self.getPkgInfoT.pkgInfoGetted.connect(self._getPkgInfoRet)
				self.getPkgInfoT.finished.connect(self.getPkgInfoT.deleteLater)
			else:
				self.core.mainStack.feedbackCode=""
				self.currentPkgOption=0

	#def showPkgInfo

	@Slot('QVariant')
	def _getPkgInfoRet(self,ret):

		if len(ret)==0:
			self.core.mainStack.feedbackCode=self.epiGuiManager.MSG_FEEDBACK_STORE_EMPTY
		else:
			self.core.mainStack.feedbackCode=""
			self.pkgStoreInfo=ret
			self.currentPkgOption=2

		self.getPkgInfoRunning=False
	
	#def _getPkgInfoRet

	@Slot(str)
	def launchApp(self, entryPoint):

		self.launchAppCmd=entryPoint
		self.launchAppT=threading.Thread(target=self._launchAppRet)
		self.launchAppT.daemon=True
		self.launchAppT.start()
		
	#def launchApp

	def _launchAppRet(self):

		suprocess.run(self.launchAppCmd,shell=True)

	#def _launchAppRet

	@Slot(str)
	def manageStatusFilter(self,value):

		self.filterStatusValue=value

	#def manageStatusFilter

	packagesModel=Property(QObject,_getPackagesModel,constant=True)

	
#class Bridge

from . import Core

