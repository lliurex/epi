#!/usr/bin/python3

import epi.epimanager as EpiManager
import os
import subprocess
import shutil
import sys
import syslog
import copy
import threading
import tempfile
import html2text
import pwd
import grp
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

class EpiGuiManager:

	ERROR_EPI_FILE_NOT_EXISTS=-1
	ERROR_EPI_EMPTY_FILE=-2
	ERROR_EPI_JSON=-3
	ERROR_SCRIPT_FILE_NOT_EXISTS=-4
	ERROR_SCRIPT_FILE_NOT_EXECUTE=-5
	ERROR_USER_NO_ROOT=-6
	ERROR_LOADING_LOCAL_DEB=-7
	ERROR_DEPENDS_LOCAL_DEB=-8
	ERROR_LOCAL_DEB_PROBLEMS=-9
	ERROR_LOCK_UPDATED=-10
	ERROR_LOCK_WAIT=-11
	ERROR_LOCK_LOCKED=-12
	ERROR_LOCK_PROCESS=-13
	ERROR_INTERNET_CONNECTION=-14
	ERROR_UNINSTALL_STOP_META=-15
	ERROR_UNINSTALL_FAILED=-16
	ERROR_UNINSTALL_STOP_SKIP_PKG=-21
	ERROR_UNINSTALL_STOP_META_SKIP_PKG=-22
	ERROR_INSTALL_INIT=-17
	ERROR_INSTALL_DOWNLOAD=-18
	ERROR_INSTALL_INSTALL=-19
	ERROR_INSTALL_ENDING=-20
	ERROR_PARTIAL_INSTALL=-23
	ERROR_PKG_TYPE_UNDEFINED=-24
	ERROR_WITH_DEPENDS=-25
	
	MSG_LOADING_INFO=0
	MSG_LOADING_WAIT=1
	MSG_LOADING_UNLOCK=2
	MSG_FEEDBACK_INTERNET=3
	INFO_ALREADY_INSTALLED=4
	INFO_ZMD_NOT_EXECUTED=5
	INFO_EPI_FAILED=6
	MSG_FEEDBACK_EULA=7
	MSG_FEEDBACK_INSTALL_REPOSITORIES=8
	MSG_FEEDBACK_INSTALL_ARQUITECTURE=9
	MSG_FEEDBACK_INSTALL_GATHER=10
	MSG_FEEDBACK_INSTALL_DOWNLOAD=11
	MSG_FEEDBACK_INSTALL_PREINSTALL=12
	MSG_FEEDBACK_INSTALL_INSTALL=13
	MSG_FEEDBACK_INSTALL_ENDING=14
	SUCCESS_INSTALL_PROCESS=15
	MSG_FEEDBACK_UNINSTALL_CHECK=16
	MSG_FEEDBACk_UNINSTALL_RUN=17
	SUCCESS_UNINSTALL_PROCESS=18
	WARNING_UNINSTALL_PROCESS_META=19
	WARNING_UNINSTALL_PROCESS_SKIP_PKG=22
	WARNING_UNINSTALL_PROCESS_META_SKIP=23
	MSG_FEEDBACK_STORE_INFO=20
	MSG_FEEDBACK_STORE_EMPTY=21

	KIRIGAMI_MSG_OK=0
	KIRIGAMI_MSG_ERROR=1
	KIRIGAMI_MSG_WARNING=2
	KIRIGAMI_MSG_INFO=3


	def __init__(self):

		self.packagesData=[]
		self.packagesMap={}
		self.defaultIconPath="/usr/lib/python3/dist-packages/epigtk/rsrc/"
		self.initialStatusCode={"msgCode":'',"type":''}
		self.lockInfo={}
		self.firstConnection=False
		self.secondConnection=False
		self.eulaAccepted=True
		self.stopUninstall={"stop":False,"msgCode":''}
		self.totalUninstallError=0
		self.totalWarningMeta=0
		self.totalWarningSkipPkg=0
		self.totalWarningSkipMeta=0
		self.appFromStore=""
		self.runPkexec=True
		self._getSessionLang()
		self.clearCache()

	#def __init__

	def _getSessionLang(self):

		tmpLang=os.environ["LANGUAGE"]

		if tmpLang!="":
			tmpLang=tmpLang.split(":")

		currentLang=""
		if len(tmpLang)>0:
			currentLang=tmpLang[0]
		else:
			currentLang=os.environ["LANG"]
		
		if 'ca' in currentLang:
			self.sessionLang="ca@valencia"
		elif 'es' in currentLang:
			self.sessionLang="es"
		else:
			self.sessionLang="en"

	#def _getSessionLang

	def initProcess(self,epiFile,noCheck,debug,app):

		self.epiManager=EpiManager.EpiManager([debug,False])
		self.epiFile=epiFile
		self.noCheck=noCheck
		self.tmpAppFromStore=app
		ret=self._checkEpiFile()

		if ret["status"]:
			ret=self._loadEpiFile()
	
		return ret

	#def initProcess

	def _checkEpiFile(self):

		valid_json = self.epiManager.read_conf(self.epiFile)

		if not valid_json.get("status"):
			if valid_json.get("depends")!="":
				return {"status":False,"msgCode":EpiGuiManager.ERROR_WITH_DEPENDS,"type":"Depends","data":valid_json.get("depends")}
			else:
				error_type = valid_json.get("error")
				if error_type == "path":
					return {"status": False, "msgCode": EpiGuiManager.ERROR_EPI_FILE_NOT_EXISTS, "type": 'End', "data":""}
				if error_type == "json":
					return {"status": False, "msgCode": EpiGuiManager.ERROR_EPI_JSON, "type": 'End',"data":""}
				return {"status": False, "msgCode": EpiGuiManager.ERROR_EPI_EMPTY_FILE, "type": 'End',"data":""}

		valid_script = self.epiManager.check_script_file()

		if not valid_script.get("status"):
			if valid_script.get("error") == "path":
				return {"status": False, "msgCode": EpiGuiManager.ERROR_SCRIPT_FILE_NOT_EXISTS, "type": 'End',"data":""}
			return {"status": False, "msgCode": EpiGuiManager.ERROR_SCRIPT_FILE_NOT_EXECUTE, "type": 'End',"data":""}

		return {"status": True, "msgCode": "", "type": "","data":""}

	#def _checkEpiFile
	
	def _loadEpiFile(self):

		self.loadEpiConf = self.epiManager.epiFiles
		self.order = len(self.loadEpiConf)

		ret = {"status": True, "msgCode": '', "type": '', "data": ""}
		requiredRoot = False
		testInstall = ["", ""]
		threadsLaunched = False

		if self.order > 0:
			self.epiManager.get_pkg_info()
			if not self.epiManager.pkg_info:
				return {"status": False, "msgCode": EpiGuiManager.ERROR_PKG_TYPE_UNDEFINED, "type": 'End', "data": ""}

			self._launchLoadThreads()
			threadsLaunched = True

			checkRoot = self.epiManager.check_root()
			requiredRoot = self.epiManager.required_root()
			self.requiredEula = self.epiManager.required_eula()

			if len(self.requiredEula) > 0:
				self.eulaAccepted = False

			if checkRoot:
				if not self.noCheck:
					self.checkLockInfo()
				self._writeLog(f"Locks info: {self.lockInfo}")
			else:
				self._writeLog("Locks info: Not checked. User is not root")

			testInstall = self.epiManager.test_install()
			self.loadEpiConf=self.epiManager.epiFiles
			self.order=len(self.loadEpiConf)

		if threadsLaunched:
			self._getEpiContent_t.join()
			self._getInitialStatus_t.join()

		if requiredRoot:
			return {"status": False, "msgCode": EpiGuiManager.ERROR_USER_NO_ROOT, "type": 'End', "data": ""}

		if len(self.lockInfo) > 0:
			return self.getLockInfo()

		if testInstall[0] != "":
			if testInstall[0] == "1":
				return {"status": False, "msgCode": EpiGuiManager.ERROR_LOADING_LOCAL_DEB, "type": 'End', "data": ""}
				if testInstall[1] != "":
					return self._localDebError(testInstall)

		return ret

	#def _loadEpiFile

	def _launchLoadThreads(self):

		self._getEpiContent_t=threading.Thread(target=self._getEpiContent)
		self._getEpiContent_t.daemon=True
		self._getEpiContent_t.start()
		self._getInitialStatus_t=threading.Thread(target=self._getInitialStatus)
		self._getInitialStatus_t.daemon=True
		self._getInitialStatus_t.start()

	#def _launchLoadThreads

	def checkLockInfo(self):

		self.lockInfo=self.epiManager.check_locks()

	#def checkLockInfo

	def getLockInfo(self):

		ret={"status":True,"msgCode":'',"type":'',"data":''}

		if len(self.lockInfo)>0:
			if "Lliurex-Up" in self.lockInfo:
				self._writeLog("Lock info: The system is being updated")
				ret={"status":False,"msgCode":EpiGuiManager.ERROR_LOCK_UPDATED,"type":'End',"data":''}
			else:
				if self.lockInfo["wait"]:
					self._writeLog("Lock info: Apt or Dpkg are being executed. Checking if they have finished...")
					ret={"status":False,"msgCode":EpiGuiManager.ERROR_LOCK_WAIT,"type":'End',"data":''}
				else:
					self._writeLog("Lock info: Apt or Dpkg seems locked. Unlock process need")
					ret={"status":False,"msgCode":EpiGuiManager.ERROR_LOCK_LOCKED,"type":'End',"data":''}

		return ret

	#def getLockInfo

	def execUnlockProcess(self):

		ret=self.epiManager.unlock_process()

		if ret==0:
			self._writeLog("Unlock process ok")
			return {"status":True,"msgCode":''}
		else:
			self._writeLog("Unlock process failed: %s"%str(ret))
			return {"status":False,"msgCode":EpiGuiManager.ERROR_LOCK_PROCESS} 

	#def execUnlockProcess

	def _localDebError(self,testInstall):

		if testInstall[1]!="":
			ret={"status":False,"msgCode":EpiGuiManager.ERROR_DEPENDS_LOCAL_DEB,"type":'LocalDeb',"data":str(testInstall[1])}
		else:
			ret={"status":False,"msgCode":EpiGuiManager.ERROR_LOCAL_DEB_PROBLEMS,"type":'LocalDeb',"data":str(testinstall[0])}

		self._writeLog(f"Test to install local deb: Unable to install package: {testInstall}")
	
		return ret

	#def _localDebError
	
	def _getEpiContent(self):

	    self.info = copy.deepcopy(self.loadEpiConf)
	    self.areDepends = len(self.info) > 1

	    self.searchEntry = False
	    self.selectPkg = False
	    self.uncheckAll = False
	    self.showRemoveBtn = False
	    self.pkgsInstalled = []
	    self.pkgSelectedFromList = []
	    self.wikiUrl = ""
	    self.defaultPkg = False
	    self.matchWithAppFromStore = False

	    defaultChecked = False

	    for order, content in self.info.items():
	        showCB = False

	        if order == 0:
	            selection = content.get("selection_enabled", {})
	            if selection.get("active"):
	                self.searchEntry = True
	                self.selectPkg = True
	                showCB = True
	                if selection.get("all_selected"):
	                    defaultChecked = True
	                    self.uncheckAll = True
	                    self.defaultPkg = True

	            if content.get("script", {}).get("remove") and not getattr(self.epiManager, 'lock_remove_for_group', False):
	                self.showRemoveBtn = True

	            self.wikiUrl = content.get("wiki", "")

	        for pkgOrder, element in enumerate(content.get("pkg_list", [])):
	            if order > 0 and pkgOrder > 0:
	                continue

	            pkgName = element.get("name")
	            pkgSkippedFlavours = element.get("skip_flavours", [])
	            pkgSkipped = self.epiManager.is_pkg_skipped_for_flavour(pkgName, pkgSkippedFlavours)

	            if not pkgSkipped:
	                pkgSkipGroups = element.get("skip_groups", [])
	                pkgSkippedGroup = self.epiManager.is_pkg_skipped_for_group(pkgName, pkgSkipGroups)

	                if pkgSkippedGroup != 1:
	                    tmp = {
	                        "pkgId": pkgName,
	                        "showCb": showCB,
	                        "showSpinner": False
	                    }

	                    if defaultChecked or not showCB:
	                        tmp["isChecked"] = True
	                        self._managePkgSelected(pkgName, True, order)
	                    else:
	                        isDefault = element.get("default_pkg", False)
	                        if isDefault:
	                            tmp["isChecked"] = True
	                            self.defaultPkg = True
	                            self._managePkgSelected(pkgName, True, order)
	                        elif self.tmpAppFromStore and tmp["pkgId"] == self.tmpAppFromStore:
	                            tmp["isChecked"] = True
	                            self.matchWithAppFromStore = True
	                            self._managePkgSelected(pkgName, True, order)
	                        else:
	                            tmp["isChecked"] = False

	                    if order != 0:
	                        tmp["customName"] = content.get("zomando", "")
	                        tmp["entryPoint"] = ""
	                        tmp["metaInfo"] = tmp["customName"]
	                    else:
	                        customName = element.get("custom_name", "")
	                        if isinstance(customName, dict):
	                            tmp["customName"] = customName.get(self.sessionLang, customName.get("en", pkgName))
	                        else:
	                            tmp["customName"] = customName if customName else pkgName

	                        tmp["metaInfo"] = f"{tmp['pkgId']}-{tmp['customName']}"
	                        tmp["entryPoint"] = element.get("entrypoint", "")

	                    pkgInfoData = self.epiManager.pkg_info.get(pkgName, {})
	                    tmp["status"] = pkgInfoData.get("status", "available")

	                    if tmp["status"] == "installed" and tmp["pkgId"] not in self.pkgsInstalled:
	                        self.pkgsInstalled.append(tmp["pkgId"])

	                    tmp["pkgIcon"] = self._getPkgIcon(order, pkgOrder, tmp["status"])
	                    tmp["isVisible"] = (order == 0)
	                    tmp["resultProcess"] = -1
	                    tmp["order"] = order

	                    if order == 0 or tmp["status"] != "installed":
	                        self.packagesData.append(tmp)

	        if not self.defaultPkg and self.matchWithAppFromStore:
	            self.appFromStore = self.tmpAppFromStore
	            self.selectPkg = False

	        total_actual_pkgs = len(self.packagesData)
	        if self.showRemoveBtn and len(getattr(self.epiManager, 'skipped_pkgs_groups', [])) == total_actual_pkgs:
	            self.showRemoveBtn = False

	    self.totalPackages = len(self.packagesData)
	    self.packagesMap = {item["pkgId"]: item for item in self.packagesData if "pkgId" in item}
	    self._endGetEpiContent = True

	#def _getEpiContent

	def _getPkgIcon(self, order, pkgIndex, status):

	    isInstalled = (status == "installed")
	    
	    if order != 0:
	    	if isInstalled:
	    		iconName = "package_install_dep.png"
	    	else:
	    		iconName="package_dep.png"

	    	return os.path.join(self.defaultIconPath, iconName)

	    try:
	        content = self.info[order]
	        iconPath = content.get("custom_icon_path", "")
	        
	        if iconPath:
	            pkgList = content.get("pkg_list", [])
	            if pkgIndex < len(pkgList):
	            	customIcon = pkgList[pkgIndex].get("custom_icon", "") 
	            else:
	            	customIcon=""
	            
	            if customIcon:
	                if isInstalled:
	                    customIcon = f"{customIcon}_OK"
	                return os.path.join(iconPath, customIcon)

	    except Exception as e:
	        pass

	    if isInstalled:
	    	defaultIcon = "package_install.png" 
	    else:
	    	defaultIcon="package.png"

	    return os.path.join(self.defaultIconPath, defaultIcon)

	 #def _getPkgIcon

	def _getInitialStatus(self):

		if self.loadEpiConf[0].get("status")=="installed":
			zmdConfigured=self.epiManager.get_zmd_status(0)
			if not self.loadEpiConf[0].get("selection_enabled",{}).get("active",False):
				if zmdConfigured==1:
					self.initialStatusCode={"msgCode":EpiGuiManager.INFO_ALREADY_INSTALLED,"type":EpiGuiManager.KIRIGAMI_MSG_INFO}
				elif zmdConfigured==0:
					self.initialStatusCode={"msgCode":EpiGuiManager.INFO_ZMD_NOT_EXECUTED,"type": EpiGuiManager.KIRIGAMI_MSG_WARNING}
				elif zmdConfigured==-1:
					self.initialStatusCode={"msgCode":EpiGuiManager.INFO_EPI_FAILED,"type":EpiGuiManager.KIRIGAMI_MSG_WARNING}


	#def _getInitialStatus

	def onCheckedPackages(self, pkgId, isChecked):

		self._managePkgSelected(pkgId, isChecked)

		self.uncheckAll = (len(self.epiManager.packages_selected) == self.totalPackages)

		tmpParam = {"isChecked": isChecked}

		self._updatePackagesModel(tmpParam, pkgId)

	#def onCheckedPackages

	def selectAll(self):

		active = not self.uncheckAll
		tmpParam = {"isChecked": active}

		for item in self.packagesData:
			if item.get("isChecked") != active:
				pkgId = item["pkgId"]
				self._managePkgSelected(pkgId, active)
				self._updatePackagesModel(tmpParam, pkgId)

		self.uncheckAll = active

	#def selectAll

	def _updatePackagesModel(self, param, pkgId):

		item = self.packagesMap.get(pkgId)

		if item:
			if "status" in param:
				item["resultProcess"] = 0
				if item.get("status") != param["status"]:
					item["resultProcess"]=0
				else:
					item["resultProcess"]=1

			item.update(param)

    #def _updatePackagesModel

	def _managePkgSelected(self, pkgId, active=True, order=0):

		pkgsSel = self.epiManager.packages_selected
		checkListFromReply = self.selectPkg and order == 0

		if active:
			if pkgId not in pkgsSel:
				pkgsSel.append(pkgId)

			if checkListFromReply and pkgId not in self.pkgSelectedFromList:
				self.pkgSelectedFromList.append(pkgId)
		else:
			if pkgId in pkgsSel:
				pkgsSel.remove(pkgId)

			if checkListFromReply and pkgId in self.pkgSelectedFromList:
				self.pkgSelectedFromList.remove(pkgId)

	#def _managePkgSelected
	
	def checkInternetConnection(self):

		self._writeLog(f"Packages selected to install: {self.epiManager.packages_selected}")

		urls = [self.epiManager.urltocheck1, self.epiManager.urltocheck2]

		self.executor = ThreadPoolExecutor(max_workers=2)

		self.connectionFutures = {
			self.executor.submit(self.epiManager.check_connection, url): url for url in urls
		}

	#def checkInternetConnection

	def getResultCheckConnection(self):

		self.endCheck = False
		self.retConnection = {"status":True, "msgCode":'',"type":''}

		doneFutures = [f for f in self.connectionFutures if f.done()]

		if not doneFutures:
			return

		errorsLogged = []

		for future in doneFutures:
			resultList = future.result()

			success = resultList[0]

			if success:
				self.endCheck = True
				self.retConnection = {"status":True, "msgCode":'',"type":''}
				self.executor.shutdown(wait=False)
				return
			else:
				if len(resultList) > 1:
					errorMsg = resultList[1]
				else:
					errorMsg="Unknown error"

				errorsLogged.append(errorMsg)

		if len(doneFutures) == len(self.connectionFutures):
			self.endCheck = True
			msgError = EpiGuiManager.ERROR_INTERNET_CONNECTION
			if errorsLogged:
				firstError = errorsLogged[0]
			else:
				firstError="No response"

			self._writeLog(f"{msgError}:{firstError}")
			self.retConnection = {"status":False, "msgCode":msgError,"type":EpiGuiManager.KIRIGAMI_MSG_ERROR}

	#def getResultCheckConnection

	def getEulasToCheck(self):

		self.eulasToCheck=[]

		for eula in self.requiredEula:
			if eula["pkg_name"] in self.epiManager.packages_selected:
				self.eulasToCheck.append(eula)

		self.eulaOrder = len(self.eulasToCheck) - 1	

		self._writeLog(f"Required Eulas: {self.eulasToCheck}")

	#def getEulasToCheck

	def acceptEula(self):

		self.eulaAccepted=True
		pkgId=self.eulasToCheck[self.eulaOrder]["pkg_name"]
		self.eulasToCheck.pop(self.eulaOrder)
		self.eulaOrder-=1
		self._writeLog(f"Accepted EULA of: {pkgId}")

	#def acceptEula

	def rejectEula(self):

		pkgId=self.eulasToCheck[self.eulaOrder]["pkg_name"]
		self.eulasToCheck.pop(self.eulaOrder)
		self.eulaOrder-=1

		if self.selectPkg:
			self._managePkgSelected(pkgId,False)
			tmpParam={}
			tmpParam["isChecked"]=False
			self._updatePackagesModel(tmpParam,pkgId)

			if len(self.eulasToCheck)==0 and len(self.epiManager.packages_selected)>0:
				self.eulaAccepted=True
		
		self._writeLog(f"Rejected EULA of: {pkgId}")

	#def rejectEula

	def clearCache(self):

		clear=False
		installedVersion=self._getPackageVersion()

		isElevated = (
			os.getuid() == 0 or 
			"SUDO_USER" in os.environ or 
			"PKEXEC_UID" in os.environ
		)

		if isElevated:
			versionFile = Path("/root/.epi-gui.conf")
			cachePath = Path("/root/.cache/epi-gtk")
		else:
			homeDir = Path.home()
			versionFile = homeDir / ".config" / "epi-gui.conf"
			cachePath = homeDir / ".cache" / "epi-gtk"
	
		if not os.path.exists(versionFile):
			clear=True
		else:
			with open(versionFile,'r') as fd:
				fileVersion=fd.readline().strip()

			if fileVersion!=installedVersion:
				clear=True

		if clear:
			with open(versionFile,'w') as fd:
				fd.write(installedVersion)

			if os.path.exists(cachePath):
				shutil.rmtree(cachePath)

	#def clearCache

	def checkRemoveMeta(self):

		selectedPkgs = self.epiManager.packages_selected
		self._writeLog(f"Packages selected to uninstall: {selectedPkgs}")

		self.stopUninstall = {"stop": False, "msgCode": ''}

		self.metaRemovedWarning = self.epiManager.check_remove_meta()
		blockedMeta = self.epiManager.blocked_remove_pkgs_list
		self._writeLog(f"Check remove meta-package. Packages blocked: {blockedMeta}")

		if self.metaRemovedWarning and len(selectedPkgs) == len(blockedMeta):
			self.stopUninstall = {"stop": True, "msgCode": EpiGuiManager.ERROR_UNINSTALL_STOP_META}
			self._writeLog("Uninstall blocked due to remove metapackage warning")
			return 

		self.skippedRemovedWarning = self.epiManager.check_remove_skip_pkg()
		blockedSkip = self.epiManager.blocked_remove_skipped_pkgs_list
		self._writeLog(f"Check remove skipped package. Packages blocked: {blockedSkip}")

		if self.skippedRemovedWarning:
			if len(selectedPkgs) == len(blockedSkip):
				self.stopUninstall = {"stop": True, "msgCode": EpiGuiManager.ERROR_UNINSTALL_STOP_SKIP_PKG}
				self._writeLog("Uninstall blocked due to remove skipped pkg warning")
			else:
				totalBlockedPkgs = len(blockedSkip) + len(blockedMeta)
				if len(selectedPkgs) == totalBlockedPkgs:
					self.stopUninstall = {"stop": True, "msgCode": EpiGuiManager.ERROR_UNINSTALL_STOP_META_SKIP_PKG}
					self._writeLog("Uninstall blocked due to remove skipped and meta pkg warning")

	#def checkRemoveMeta

	def initInstallProcess(self):

		self.addRepositoryKeysLaunched=False
		self.addRepositoryKeysDone=False
		self.updateKeyRingLaunched=False
		self.updateKeyRingDone=False
		self.checkArquitectureLaunched=False
		self.checkArquitectureDone=False
		self.updateReposLaunched=False
		self.updateReposDone=False

		if self.order>0:
			self.order=self.order-1

	#def initInstallProcess

	def initPkgInstallProcess(self,pkgId):

		self.downloadAppLaunched=False
		self.downloadAppDone=False
		self.checkDownloadLaunched=False
		self.checkDownloadDone=False
		self.preInstallAppLaunched=False
		self.preInstallAppDone=False
		self.checkPreInstallLaunched=False
		self.checkPreInstallDone=False
		self.installAppLaunched=False
		self.installAppDone=False
		self.checkInstallLaunched=False
		self.checkInstallDone=False
		self.postInstallAppLaunched=False
		self.postInstallAppDone=False
		self.checkPostInstallLaunched=False
		self.checkPostInstallDone=False

		self._initProcessValues(self.order,"install",pkgId)

	#def initPkgInstallProcess

	def getAddRepositoryCommand(self):

		command=""
		command=self.epiManager.add_repository_keys(self.order)
		length=len(command)

		if length>0:
			command=self._createProcessToken(command,"keys")
		else:
			self.addRepositoryKeysDone=True
		
		return command

	#def getAddRepositoryCommand

	def getUpdateKeyRingCommand(self):

		command=""
		command=self.epiManager.update_keyring()
		length=len(command)

		if length>0:
			command=self._createProcessToken(command,"keyring")
		else:
			self.updateKeyRingDone=True
		
		return command

	#def getUpdateKeyringCommand

	def getDownloadAppCommand(self,pkgId):

		command=""
		command=self.epiManager.download_app(pkgId)
		length=len(command)

		if length>0:
			command=self._createProcessToken(command,"download")
		else:
			self.downloadAppDone=True

		return command

	#def getDownloadAppCommand

	def checkDownload(self,pkgId):

		self.feedBackCheck={"status":True,"msgCode":'','type':''}
		downloadRet=self.epiManager.check_download(pkgId)

		if not downloadRet:
			msgCode=EpiGuiManager.ERROR_INSTALL_DOWNLOAD
			self._updateProcessModelInfo(self.order,pkgId,'install',False,None)
			self.feedBackCheck={"status":downloadRet,"msgCode":msgCode,"type":EpiGuiManager.KIRIGAMI_MSG_ERROR}
			self._writeLog(f"Install process. Result: PkgId: {pkgId} - Status: Error - Code: {msgCode}")

		self.checkDownloadDone=True

	#def checkDownloadApp

	def getPreInstallCommand(self,pkgId):

		command=""
		command=self.epiManager.preinstall_app(pkgId)
		length=len(command)

		if length>0:
			command=self._createProcessToken(command,"preInstall")
		else:
			self.preInstallAppDone=True

		return command

	#def getPreInstallCommand

	def checkPreInstall(self,pkgId):

		self.feedBackCheck={"status":True,"msgCode":'',"type":''}
		preInstallRet=self.epiManager.check_preinstall(pkgId)
		
		if not preInstallRet:
			msgCode=EpiGuiManager.ERROR_INSTALL_INIT
			self._updateProcessModelInfo(self.order,'install',False,None)
			self.feedBackCheck={"status":preInstallRet,"msgCode":msgCode,"type":EpiGuiManager.KIRIGAMI_MSG_ERROR}
			self._writeLog(f"Install process. Result: PkgId: {pkgId} - Status: Error - Code: {msgCode}")

		self.checkPreInstallDone=True

	#def checkPreInstall

	def getCheckArquitectureCommand(self):

		command=""
		command=self.epiManager.check_arquitecture()
		length=len(command)

		if length>0:
			command=self._createProcessToken(command,"arquitecture")
		else:
			self.checkArquitectureDone=True

		return command

	#def getCheckArquitectureCommand

	def getUpdateReposCommand(self):

		command=""
		command=self.epiManager.check_update_repos()
		length=len(command)

		if length>0:
			command=self._createProcessToken(command,"updaterepos")
		else:
			self.updateReposDone=True

		return command

	#def getUpdateReposCommand

	def getInstallCommand(self,pkgId):

		command=""
		command=self.epiManager.install_app("gui",pkgId)
		length=len(command)

		if length>0:
			command=self._createProcessToken(command,"install")
		else:
			self.installAppDone=True

		return command

	#def getInstallCommand

	def checkInstall(self,pkgId):

		self.feedBackCheck={"status":True,"msgCode":'',"type":''}
		self.dpkgStatus,self.installed=self.epiManager.check_install_remove("install",pkgId)

		if not self.installed:
			self._updateProcessModelInfo(self.order,pkgId,'install',self.installed,self.dpkgStatus)
			msgCode=EpiGuiManager.ERROR_INSTALL_INSTALL
			self.feedBackCheck={"status":installed,"msgCode":msgCode,"type":EpiGuiManager.KIRIGAMI_MSG_ERROR}
			self._writeLog(f"Install process. Result: PkgId: {pkgId} - Status: Error - Code: {msgCode}")
	
		self.checkInstallDone=True

	#def checkInstall

	def getPostInstallCommand(self,pkgId):

		command=self.epiManager.postinstall_app(pkgId)
		length=len(command)

		if length>0:
			command=self._createProcessToken(command,"postInstall")
		else:
			self.postInstallAppDone=True

		return command

	#def getPostInstallCommand

	def checkPostInstall(self,pkgId):

		self.feedBackCheck={"status":True,"msgCode":'',"type":''}
		postInstallRet=self.epiManager.check_postinstall(pkgId)
		
		if self.installed:
			self._updateProcessModelInfo(self.order,pkgId,"install",self.installed,self.dpkgStatus)

			if not postInstallRet:
				msgCode=EpiGuiManager.ERROR_INSTALL_ENDING
				typeMsg=EpiGuiManager.KIRIGAMI_MSG_ERROR
				status="Error"
		
			else:
				msgCode=EpiGuiManager.SUCCESS_INSTALL_PROCESS
				typeMsg=EpiGuiManager.KIRIGAMI_MSG_OK
				status="Ok"

			self.feedBackCheck={"status":postInstallRet,"msgCode":msgCode,"type":typeMsg}
			self._writeLog(f"Install process. Result: PkgId: {pkgId} - Status: {status} - Code: {msgCode}")

			self.checkPostInstallDone=True

	#def checkPostInstall

	def initUnInstallProcess(self,pkgId):

		self.removePkgLaunched=False
		self.removePkgDone=False
		self.checkRemoveLaunched=False
		self.checkRemoveDone=False
		self._initProcessValues(0,"uninstall",pkgId)
		
	#def initUnInstallProcess

	def getUninstallCommand(self,pkgId):

		command=""
		command=self.epiManager.uninstall_app(0,pkgId)
		length=len(command)

		if length>0:
			command=self._createProcessToken(command,"uninstall")

		return command

	#def getUninstallCommand

	def _createProcessToken(self,command,action):

		cmd=""
		if action=="keys":
			self.tokenKeys=self._getTempFile(action)
			removeTmp=f' rm -f {self.tokenKeys}'
		elif action=="keyring":
			self.tokenKeyring=self._getTempFile(action)
			removeTmp=f' rm -f {self.tokenKeyring}'
		elif action=="download":
			self.tokenDownload=self._getTempFile(action)
			removeTmp=f' rm -f {self.tokenDownload}'
		elif action=="preInstall":
			self.tokenPreInstall=self._getTempFile(action)	
			removeTmp=f' rm -f {self.tokenPreInstall}'
		elif action=="arquitecture":
			self.tokenArquitecture=self._getTempFile(action)	
			removeTmp=f' rm -f {self.tokenArquitecture}'	
		elif action=="updaterepos":
			self.tokenUpdaterepos=self._getTempFile(action)	
			removeTmp=f' rm -f {self.tokenUpdaterepos}'	
		elif action=="install":
			self.tokenInstall=self._getTempFile(action)
			removeTmp=f' rm -f {self.tokenInstall}'
		elif action=="postInstall":	
			self.tokenPostInstall=self._getTempFile(action)
			removeTmp=f' rm -f {self.tokenPostInstall}'
		elif action=="uninstall":
			self.tokenUninstall=self._getTempFile(action)
			removeTmp=f' rm -f {self.tokenUninstall}'

		cmd=f'{command} history -c;stty -echo;{removeTmp}\n'
		if cmd.startswith(";"):
			cmd=cmd[1:]

		return cmd

	#def _createProcessToken

	def _getTempFile(self,action):

		suffixName=f"_{action}"
		tmpFile=tempfile.NamedTemporaryFile(suffix=suffixName,delete=False)
		tmpFile.close()

		return tmpFile.name

	#def _getTempFile

	def checkRemove(self, pkgId):

		dpkgStatus, remove = self.epiManager.check_install_remove("uninstall", pkgId)
		self._updateProcessModelInfo(0, pkgId, 'uninstall', remove, dpkgStatus)
		self.checkRemoveDone = True

		hasBlocked = bool(self.epiManager.blocked_remove_pkgs_list)
		hasSkipped = bool(self.epiManager.blocked_remove_skipped_pkgs_list)

		typeMsg = EpiGuiManager.KIRIGAMI_MSG_WARNING

		if remove:
			if hasBlocked:
				if not hasSkipped:
					self.totalWarningSkipPkg += 1
					msgCode = EpiGuiManager.WARNING_UNINSTALL_PROCESS_META
				else:
					self.totalWarningSkipMeta += 1
					msgCode = EpiGuiManager.WARNING_UNINSTALL_PROCESS_META_SKIP
			elif hasSkipped:
				self.totalWarningSkipPkg += 1
				msgCode = EpiGuiManager.WARNING_UNINSTALL_PROCESS_SKIP_PKG
			else:
				typeMsg = EpiGuiManager.KIRIGAMI_MSG_OK
				msgCode = EpiGuiManager.SUCCESS_UNINSTALL_PROCESS
		else:
			if pkgId in self.epiManager.blocked_remove_pkgs_list:
				msgCode = EpiGuiManager.WARNING_UNINSTALL_PROCESS_META
			elif pkgId in self.epiManager.blocked_remove_skipped_pkgs_list:
				msgCode = EpiGuiManager.WARNING_UNINSTALL_PROCESS_SKIP_PKG
			else:
				self.totalUninstallError += 1
				typeMsg = EpiGuiManager.KIRIGAMI_MSG_ERROR
				msgCode = EpiGuiManager.ERROR_UNINSTALL_FAILED

		self._writeLog(f"Uninstall process. Result: PkgId: {pkgId} - Status: {typeMsg} - Code: {msgCode}")

	#def checkRemove

	def getUninstallGlobalResult(self):

		if self.totalUninstallError>0:
			return {"msgCode":EpiGuiManager.ERROR_UNINSTALL_FAILED,"type":EpiGuiManager.KIRIGAMI_MSG_ERROR}
		elif self.totalWarningSkipPkg>0:
			return {"msgCode":EpiGuiManager.WARNING_UNINSTALL_PROCESS_META,"type":EpiGuiManager.KIRIGAMI_MSG_WARNING}
		elif self.totalWarningSkipMeta>0:
			return {"msgCode":EpiGuiManager.WARNING_UNINSTALL_PROCESS_META_SKIP,"type":EpiGuiManager.KIRIGAMI_MSG_WARNING}
		elif self.totalWarningSkipPkg>0:
			return {"msgCode":EpiGuiManager.WARNING_UNINSTALL_PROCESS_SKIP_PKG,"type":EpiGuiManager.KIRIGAMI_MSG_WARNING}
		else:
			return {"msgCode":EpiGuiManager.SUCCESS_UNINSTALL_PROCESS,"type":EpiGuiManager.KIRIGAMI_MSG_OK}

	#def getUninstallGlobalResult

	def _updateProcessModelInfo(self, order, pkgId, action, result, dpkgStatus=None):
		
		if action == "install":
			self._updateInstallModelInfo(order, pkgId, result, dpkgStatus)
		elif action == "uninstall":
			self._updateUninstallModelInfo(order, pkgId, result, dpkgStatus)
	
	#def _updateProcessModelInfo

	def _updateInstallModelInfo(self, order, pkgId, result, dpkgStatus=None):

		for pkgIndex, element in enumerate(self.info[order]["pkg_list"]):
			name = element["name"]

			if (pkgId != "all" and name != pkgId) or (name not in self.epiManager.packages_selected):
				continue

			tmpParam = {"showSpinner": False}
			status = "available"
			resProcess = 1

			if result:
				status = 'installed'
				resProcess = 0
			else:
				if dpkgStatus and name in dpkgStatus:
					if dpkgStatus[name] == 'installed':
						status = 'installed'
						resProcess = 0
				else:
					if name not in self.pkgsInstalled:
						resProcess=1

			tmpParam["status"] = status
			tmpParam["resultProcess"] = resProcess

			if order == 0 and status == 'installed' and name not in self.pkgsInstalled:
				self.pkgsInstalled.append(name)

			tmpParam["pkgIcon"] = self._getPkgIcon(order, pkgIndex, tmpParam["status"])

			self._updatePackagesModel(tmpParam, name)

	#def _updateInstallModelInfo

	def _updateUninstallModelInfo(self, order, pkgId, result, dpkgStatus=None):

		for pkgIndex, element in enumerate(self.info[order]["pkg_list"]):
			name = element["name"]

			if (pkgId != "all" and name != pkgId) or (name not in self.epiManager.packages_selected):
				continue

			tmpParam = {"showSpinner": False}
			status = "available"
			resProcess = 1

			if result:
				isBlocked = (name in self.epiManager.blocked_remove_pkgs_list or 
					name in self.epiManager.blocked_remove_skipped_pkgs_list)

				if isBlocked:
					status = "installed"
				else:
					resProcess = 0
			else:
				if dpkgStatus and name in dpkgStatus:
					if dpkgStatus[name] != 'installed':
						resProcess = 0
					else:
						status = 'installed'
				else:
					if name in self.pkgsInstalled:
						status = 'installed'

			tmpParam["status"] = status
			tmpParam["resultProcess"] = resProcess

			if order == 0 and status == 'available' and name in self.pkgsInstalled:
				self.pkgsInstalled.remove(name)

			tmpParam["pkgIcon"] = self._getPkgIcon(order, pkgIndex, tmpParam["status"])
			self._updatePackagesModel(tmpParam, name)

	#def _updateUninstallModelInfo
	
	def _initProcessValues(self,order,action,pkgId):

		if action=="install":
			self._initInstallProcessValues(order,pkgId)
		else:
			self._initUninstallProcessValues(order,pkgId)

	#def _initProcessValues

	def _initInstallProcessValues(self, order, pkgId):

		for item in self.packagesData:
			if item["order"] != order:
				continue

			itemId = item["pkgId"]

			if (pkgId != "all" and itemId != pkgId) or (itemId not in self.epiManager.packages_selected):
				continue

			tmpParam = {
				"resultProcess": -1,
				"showSpinner": True
			}

			if order > 0:
				tmpParam["isVisible"] = True

			self._updatePackagesModel(tmpParam, itemId)

	#def _initInstallProcessValues

	def _initUninstallProcessValues(self, order, pkgId):

		if order != 0:
			return

		for item in self.packagesData:
			if item["order"] != 0:
				continue

			itemId = item["pkgId"]
			if (pkgId != "all" and itemId != pkgId) or (itemId not in self.epiManager.packages_selected):
				continue

			isBlocked = (itemId in self.epiManager.blocked_remove_pkgs_list or 
                      itemId in self.epiManager.blocked_remove_skipped_pkgs_list)

			if not isBlocked:
				tmpParam = {
				"resultProcess": -1,
				"showSpinner": True
				}
				self._updatePackagesModel(tmpParam, itemId)
	
	#def _initUninstallProcessValues

	def getStoreInfo(self,pkgId):

		self.epiManager.get_store_info(pkgId)
		ret={}
		summary=self.epiManager.pkg_info[pkgId]["summary"]

		pkgIndex=0

		for item in self.info[0]["pkg_list"]:
			if item["name"]==pkgId:
				break
			pkgIndex+=1

		if summary!="":
			icon=self._getPkgIcon(0,pkgIndex,'available')
			name=pkgId
			tmpDescription=self.epiManager.pkg_info[pkgId]["description"]

			h=html2text.HTML2Text()
			h.body_width=400
			description=h.handle(tmpDescription)
			description=description.replace("&lt;", "<")
			description=description.replace("&gt;", ">")
			description=description.replace("&amp;", "&")
			description=description.replace(" * ","\n- ")
			description=description.replace("**","")
			description=description.strip()

			ret["icon"]=icon
			ret["name"]=name
			ret["summary"]=summary
			ret["description"]=description

		return ret

	#def getStoreInfo

	def isAllInstalled(self):

		pkgAvailable=0

		if self.totalPackages==len(self.pkgsInstalled):
			return {"allInstalled":True,"allAvailable":False}
		else:
			pkgAvailable=self.totalPackages-len(self.pkgsInstalled)
			if pkgAvailable==self.totalPackages:
				return {"allInstalled":False,"allAvailable":True}
			else:
				return {"allInstalled":False,"allAvailable":False}

	#def isAllInstalled

	def _getPackageVersion(self):

		packageVersionFile="/var/lib/epi-gtk/version"
		pkgVersion=""

		if os.path.exists(packageVersionFile):
			with open(packageVersionFile,'r') as fd:
				pkgVersion=fd.readline().strip()

		return pkgVersion

	#def _getPackageVersion

	def _writeLog(self,msg):

		syslog.openlog("EPI")
		syslog.syslog(msg)	

	#def _writeLog

	def clearEnvironment(self,forceClossing=False):

		if forceClossing:
			self._writeLog("Force closure of EPI")

		self.epiManager.remove_repo_keys()
		self.epiManager.empty_cache_folder()

	#def clearEnvironment

#class EpiGuiManager
