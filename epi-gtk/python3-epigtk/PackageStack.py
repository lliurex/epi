#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys
import pwd

from . import PackagesModel

signal.signal(signal.SIGINT, signal.SIG_DFL)

class GetPkgInfo(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.pkgId=args[0]

	#def __init__

	def run(self):

		self.ret=Bridge.epiGuiManager.getStoreInfo(self.pkgId)

	#def run

#class getPkgInfo

class Bridge(QObject):


	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.epiGuiManager=self.core.epiGuiManager
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
		self._pkgStoreInfo=["","","",""]
		self._isAllInstalled=[False,False]
		self._filterStatusValue="all"
		self._totalErrorInProcess=0


	#def __init__

	def showInfo(self):

		self._updatePackagesModel()
		self.uncheckAll=Bridge.epiGuiManager.uncheckAll
		self.selectPkg=Bridge.epiGuiManager.selectPkg
		self.wikiUrl=Bridge.epiGuiManager.wikiUrl
		self.isAllInstalled=Bridge.epiGuiManager.isAllInstalled()

	#def showInfo

	def _getCurrentPkgOption(self):

		return self._currentPkgOption

	#def _getCurrentPkgOption

	def _setCurrentPkgOption(self,currentPkgOption):

		if self._currentPkgOption!=currentPkgOption:
			self._currentPkgOption=currentPkgOption
			self.on_currentPkgOption.emit()

	#def _setCurrentPkgOption

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

	def _getEnablePkgList(self):

		return self._enablePkgList

	#def _getEnablePkgList

	def _setEnablePkgList(self,enablePkgList):

		if self._enablePkgList!=enablePkgList:
			self._enablePkgList=enablePkgList
			self.on_enablePkgList.emit()

	#def setEnablePkgList

	def _getPackagesModel(self):

		return self._packagesModel

	#def _getPackagesModel

	def _updatePackagesModel(self):

		ret=self._packagesModel.clear()
		packagesEntries=Bridge.epiGuiManager.packagesData
		for item in packagesEntries:
			if item["pkgId"]!="":
				self._packagesModel.appendRow(item["pkgId"],item["showCb"],item["isChecked"],item["customName"],item["pkgIcon"],item["status"],item["isVisible"],item["resultProcess"],item["order"],item["showSpinner"],item["entryPoint"])

	#def _updatePackagesModel

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

	def _getFilterStatusValue(self):

		return self._filterStatusValue

	#def _getFilterStatusValue

	def _setFilterStatusValue(self,filterStatusValue):

		if self._filterStatusValue!=filterStatusValue:
			self._filterStatusValue=filterStatusValue
			self.on_filterStatusValue.emit()

	#def _setFilterStatusValue

	def _getTotalErrorInProcess(self):

		return self._totalErrorInProcess

	#def _getTotalErrorInProcess

	def _setTotalErrorInProcess(self,totalErrorInProcess):

		if self._totalErrorInProcess!=totalErrorInProcess:
			print("cambio: %s"%str(totalErrorInProcess))
			self._totalErrorInProcess=totalErrorInProcess
			self.on_totalErrorInProcess.emit()

	#def _setTotalErrorInProcess

	@Slot('QVariantList')
	def onCheckPkg(self,info):

		Bridge.epiGuiManager.onCheckedPackages(info[0],info[1])
		self._refreshInfo()

	#def onCheckPkg

	@Slot()
	def selectAll(self):

		Bridge.epiGuiManager.selectAll()
		self.filterStatusValue="all"
		self._refreshInfo()
		
	#def selectAll

	def _refreshInfo(self):

		params=[]
		params.append("isChecked")
		self._updatePackagesModelInfo(params)
		self.uncheckAll=Bridge.epiGuiManager.uncheckAll
		if len(Bridge.epiGuiManager.epiManager.packages_selected)>0:
			self.core.mainStack.enableApplyBtn=True
			self.core.mainStack.manageRemoveBtn(True)
		else:
			self.core.mainStack.enableApplyBtn=False
			self.core.mainStack.manageRemoveBtn(False)

	#def _refreshInfo

	def getEulas(self):

		if not Bridge.epiGuiManager.eulaAccepted:
			Bridge.epiGuiManager.getEulasToCheck()
			if len(Bridge.epiGuiManager.eulasToShow)>0:
				self._manageEulas()
			else:
				self.core.installStack.installProcess()
		else:
			self.core.installStack.installProcess()

	#def _getEulas

	def _manageEulas(self):

		nextStep=False
		if len(Bridge.epiGuiManager.eulasToCheck)>0:
			self.core.mainStack.enableApplyBtn=True
			self.core.mainStack.enableRemoveBtn=True
			self.eulaUrl=Bridge.epiGuiManager.eulasToCheck[Bridge.epiGuiManager.eulaOrder]["eula"]
			self.core.mainStack.feedbackCode=Bridge.epiGuiManager.MSG_FEEDBACK_EULA
			self.currentEulaPkg=Bridge.epiGuiManager.eulasToCheck[Bridge.epiGuiManager.eulaOrder]["pkg_name"]
			self.currentPkgOption=1
		else:
			self.currentPkgOption=0
			self.currentEulaPkg=""
			if Bridge.epiGuiManager.eulaAccepted:
				if len(Bridge.epiGuiManager.epiManager.packages_selected)>0:
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

		Bridge.epiGuiManager.acceptEula()
		self._manageEulas()

	#def acceptEula	

	@Slot()
	def rejectEula(self):

		Bridge.epiGuiManager.rejectEula()
		if self.selectPkg:
			self._refreshInfo()
		self._manageEulas()

	#def rejectEula

	def updateResultPackagesModel(self,step,action):

		params=[]
		params.append("showSpinner")
		params.append("resultProcess")
		if step=="start" and action=="install":
			if Bridge.epiGuiManager.order>0:
				params.append("isVisible")
		if step=="end":
			params.append("pkgIcon")
			params.append("status")

		self._updatePackagesModelInfo(params)

	#def updateResultPackagesModel

	def _updatePackagesModelInfo(self,params):

		updatedInfo=Bridge.epiGuiManager.packagesData
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

		self.core.mainStack.showStatusMessage=[False,"","Ok"]

		if params[0]==0:
			self.core.mainStack.feedbackCode=Bridge.epiGuiManager.MSG_FEEDBACK_STORE_INFO
			self.getPkgInfoT=GetPkgInfo(params[1])
			self.getPkgInfoT.start()
			self.getPkgInfoT.finished.connect(self._getPkgInfoRet)
		else:
			self.core.mainStack.feedbackCode=""
			self.currentPkgOption=0

	#def showPkgInfo

	def _getPkgInfoRet(self):

		if len(self.getPkgInfoT.ret)==0:
			self.core.mainStack.feedbackCode=Bridge.epiGuiManager.MSG_FEEDBACK_STORE_EMPTY
		else:
			self.core.mainStack.feedbackCode=""
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

	@Slot(str)
	def manageStatusFilter(self,value):

		print(value)
		self.filterStatusValue=value

	#def manageStatusFilter

	on_currentPkgOption=Signal()
	currentPkgOption=Property(int,_getCurrentPkgOption,_setCurrentPkgOption,notify=on_currentPkgOption)
	
	on_uncheckAll=Signal()
	uncheckAll=Property(bool,_getUncheckAll,_setUncheckAll,notify=on_uncheckAll)

	on_selectPkg=Signal()
	selectPkg=Property(bool,_getSelectPkg,_setSelectPkg,notify=on_selectPkg)

	on_enablePkgList=Signal()
	enablePkgList=Property(bool,_getEnablePkgList,_setEnablePkgList,notify=on_enablePkgList)
	
	on_eulaUrl=Signal()
	eulaUrl=Property(str,_getEulaUrl,_setEulaUrl,notify=on_eulaUrl)

	on_currentEulaPkg=Signal()
	currentEulaPkg=Property(str,_getCurrentEulaPkg,_setCurrentEulaPkg,notify=on_currentEulaPkg)

	on_wikiUrl=Signal()
	wikiUrl=Property(str,_getWikiUrl,_setWikiUrl,notify=on_wikiUrl)

	on_showDependEpi=Signal()
	showDependEpi=Property(bool,_getShowDependEpi,_setShowDependEpi,notify=on_showDependEpi)

	on_showDependLabel=Signal()
	showDependLabel=Property(bool,_getShowDependLabel,_setShowDependLabel,notify=on_showDependLabel)

	on_pkgStoreInfo=Signal()
	pkgStoreInfo=Property('QVariantList',_getPkgStoreInfo,_setPkgStoreInfo,notify=on_pkgStoreInfo)
	
	on_isAllInstalled=Signal()
	isAllInstalled=Property('QVariantList',_getIsAllInstalled,_setIsAllInstalled,notify=on_isAllInstalled)

	on_filterStatusValue=Signal()
	filterStatusValue=Property(str,_getFilterStatusValue,_setFilterStatusValue,notify=on_filterStatusValue)

	on_totalErrorInProcess=Signal()
	totalErrorInProcess=Property(int,_getTotalErrorInProcess,_setTotalErrorInProcess,notify=on_totalErrorInProcess)
	
	packagesModel=Property(QObject,_getPackagesModel,constant=True)

#class Bridge

from . import Core

