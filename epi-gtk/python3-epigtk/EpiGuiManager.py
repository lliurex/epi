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

	MSG_LOADING_INFO=0
	MSG_LOADING_WAIT=1
	MSG_LOADING_UNLOCK=2
	MSG_FEEDBACK_INTERNET=3
	INFO_ALREADY_INSTALLED=4
	INFO_ZMD_NOT_EXECUTED=5
	INFO_EPI_FAILED=6
	MSG_FEEDBACK_EULA=7
	MSG_FEEDBACK_INSTALL_1=8
	MSG_FEEDBACK_UNINSTALL_CHECK=9
	MSG_FEEDBACk_UNINSTALL_RUN=10
	SUCCESS_UNINSTALL_PROCESS=11
	WARNING_UNINSTALL_PROCESS=12


	def __init__(self):

		self.packagesData=[]
		self.packagesSelected=[]
		self.defaultIconPath="/usr/lib/python3/dist-packages/epigtk/rsrc/"
		self.lockInfo={}
		self.initialStatusCode=["","Info"]
		self.firstConnection=False
		self.secondConnection=False
		self.eulaAccepted=True
		self.stopUninstall=[False,""]
		self.konsoleLog="/tmp/EPI_konsoleLog.txt"

		self._clearEnvirontment()
		self.clearCache()

	#def __init__

	def initProcess(self,epiFile,noCheck,debug):

		self.epiManager=EpiManager.EpiManager(debug)
		self.epiFile=epiFile
		self.noCheck=noCheck
		ret=self._checkEpiFile()

		if ret[0]:
			ret=self._loadEpiFile()
	
		return ret

	#def initProcess

	def _checkEpiFile(self):

		ret=["","",""]
		validJson=self.epiManager.read_conf(self.epiFile)
		if validJson["status"]:
			validScript=self.epiManager.check_script_file()
			if validScript["status"]:
				ret=[True,'','']
			else:
				if validScript["error"]=="path":
					ret=[False,EpiGuiManager.ERROR_SCRIPT_FILE_NOT_EXISTS,'End']
				else:
					ret=[False,EpiGuiManager.ERROR_SCRIPT_FILE_NOT_EXECUTE,'End']
		else:
			if validJson["error"]=="path":
				ret=[False,EpiGuiManager.ERROR_EPI_FILE_NOT_EXISTS,'End']
			elif validJson["error"]=="json":
				ret=[False,EpiGuiManager.ERROR_EPI_JSON,'End']
			else:
				ret=[False,EpiGuiManager.ERROR_EPI_EMPTY_FILE,'End']

		return ret

	#def _checkEpiFile

	def _loadEpiFile(self):

		epiLoaded=self.epiManager.epiFiles
		order=len(epiLoaded)
		ret=[True,"","",""]

		if order>0:
			checkRoot=self.epiManager.check_root()
			self.epiManager.get_pkg_info()
			requiredRoot=self.epiManager.required_root()
			self.requiredEula=self.epiManager.required_eula()
			
			if len(self.requiredEula)>0:
				self.eulaAccepted=False
			if checkRoot:
				if not self.noCheck:	
					self.checkLockInfo()
				self._writeLog("Locks info: "+ str(self.lockInfo))
			else:
				self._writeLog("Locks info: Not checked. User is not root")
					
			testInstall=self.epiManager.test_install()
			self.loadEpiConf=self.epiManager.epiFiles
			self.order=len(self.loadEpiConf)
		else:
			self.loadEpiConf=epiLoaded
			self.order=order

		self._getEpiContent()
		self._getInitialStatus()
		
		if requiredRoot:
			ret=[False,EpiGuiManager.ERROR_USER_NO_ROOT,'End',""]
		elif len(self.lockInfo)>0:
			ret=self.getLockInfo()
		elif testInstall[0]!="":
			if testInstall[0]=="1":
				ret=[False,EpiGuiManager.ERROR_LOADING_LOCAL_DEB,'End',""]
			else:
				if testInstall[1]!="":
					return self._localDebError(testInstall)
		
		return ret

	#def _loadEpiFile

	def checkLockInfo(self):

		self.lockInfo=self.epiManager.check_locks()

	#def checkLockInfo

	def getLockInfo(self):

		ret=[True,'','']

		if len(self.lockInfo)>0:
			if "Lliurex-Up" in self.lockInfo:
				self._writeLog("Lock info: The system is being updated")
				ret=[False,EpiGuiManager.ERROR_LOCK_UPDATED,'End']
			else:
				if self.lockInfo["wait"]:
					self._writeLog("Lock info: Apt or Dpkg are being executed. Checking if they have finished...")
					ret=[False,EpiGuiManager.ERROR_LOCK_WAIT,'Wait']
				else:
					self._writeLog("Lock info: Apt or Dpkg seems locked. Unlock process need")
					ret=[False,EpiGuiManager.ERROR_LOCK_LOCKED,'Lock']

		return ret

	#def _getLockInfo

	def execUnlockProcess(self):

		ret=self.epiManager.unlock_process()

		if ret==0:
			self._writeLog("Unlock process ok")
			return [True,""]
		else:
			self._writeLog("Unlock process failed: %s"%str(self.unlock_result))
			return [False,EpiGuiManager.ERROR_LOCK_PROCESS] 

	#def execUnlockProcess

	def _localDebError(self,testInstall):

		if testInstall[1]!="":
			ret=[False,EpiGuiManager.ERROR_DEPENDS_LOCAL_DEB,'LocalDeb',str(testInstall[1])]
		else:
			ret=[False,EpiGuiManager.ERROR_LOCAL_DEB_PROBLEMS,'LocalDeb',str(testinstall[0])]

		self._writeLog("Test to install local deb: Unable to install package:"+str(testInstall))
	
		return ret

	#def _localDebError
	
	def _getEpiContent(self):

		self.info=copy.deepcopy(self.loadEpiConf)
		self.areDepends=False
		self.searchEntry=False
		self.selectPkg=False
		self.uncheckAll=False
		self.showRemoveBtn=False
		self.pkgsInstalled=[]
		defaultChecked=False
		self.wikiUrl=""

		if len(self.info)>1:
			self.areDepends=True

		for item in self.info:
			pkgOrder=0
			showCB=False
			order=item
			if order==0:
				if self.info[item]["selection_enabled"]["active"]:
					self.searchEntry=True
					self.selectPkg=True
					showCB=True
					if self.info[item]["selection_enabled"]["all_selected"]:
						defaultChecked=True
						self.uncheckAll=True

				try:
					if self.info[item]["script"]["remove"]:
						self.showRemoveBtn=True
				except :
					pass
				
				self.wikiUrl=self.info[item]["wiki"]
				self.totalPackages=len(self.info[item]["pkg_list"])
				
			for element in self.info[item]["pkg_list"]:
				if order>0 and pkgOrder>0:
					pass
				else:
					tmp={}
					tmp["pkgId"]=element["name"]
					tmp["showCb"]=showCB
					tmp["showSpinner"]=True

					if defaultChecked:
						tmp["isChecked"]=True
						self._managePkgSelected(element["name"],True)
					else:
						if not showCB:
							tmp["isChecked"]=True
							self._managePkgSelected(element["name"],True)
						else:
							try:
								tmp["isChecked"]=element["default_pkg"]
								if tmp["isChecked"]:
									self._managePkgSelected(element["name"],True)
							except:
								tmp["isChecked"]=False			
					
					if order!=0:
						tmp["customName"]=self.info[item]["zomando"]
					else:
						try:
							tmp["customName"]=element["custom_name"]
						except:
							tmp["customName"]=element["name"]

					tmp["status"]=self.epiManager.pkg_info[element["name"]]["status"]
					
					if tmp["status"]=="installed":
						if tmp["pkgId"] not in self.pkgsInstalled:
							self.pkgsInstalled.append(tmp["pkgId"])

					tmp["pkgIcon"]=self._getPkgIcon(order,pkgOrder,tmp["status"])
						
					if order==0:
						tmp["isVisible"]=True
					else:
						tmp["isVisible"]=False

					tmp["isRunning"]=False
					tmp["resultProcess"]=-1
					tmp["order"]=order
					if order!=0:
						if tmp["status"]!="installed":
							self.packagesData.append(tmp)
					else:
						self.packagesData.append(tmp)
				
				pkgOrder+=1
		
	#def _getEpiContent

	def _getPkgIcon(self,order,pkgIndex,status):

		if order==0:
			try:
				iconPath=self.info[order]["custom_icon_path"]
				if iconPath!="":
					if iconPath[-1]!="/":
						iconPath="%s/"%iconPath
					if status=="installed":
						pkgIcon="%s%s_OK"%(iconPath,self.info[order]["pkg_list"][pkgIndex]["custom_icon"])
					else:	
						pkgIcon="%s%s"%(iconPath,self.info[order]["pkg_list"][pkgIndex]["custom_icon"])
				else:
					if status=="installed":
						pkgIcon="%s%s"%(self.defaultIconPath,"package_install.png")
					else:
						pkgIcon="%s%s"%(self.defaultIconPath,"package.png")
			except Exception as e:
				print("ERROR: %s"%str(e))
				if status=="installed":
					pkgIcon="%s%s"%(self.defaultIconPath,"package_install.png")
				else:
					pkgIcon="%s%s"%(self.defaultIconPath,"package.png")
		else:
			if status=="installed":
				pkgIcon="%s%s"%(self.defaultIconPath,"package_install_dep.png")
			else:
				pkgIcon="%s%s"%(self.defaultIconPath,"package_dep.png")
	
		return pkgIcon

	#def _getPkgIcon

	def _getInitialStatus(self):

		if self.loadEpiConf[0]["status"]=="installed":
			zmdConfigured=self.epiManager.get_zmd_status(0)
			if not self.loadEpiConf[0]["selection_enabled"]["active"]:
				if zmdConfigured==1:
					self.initialStatusCode=[EpiGuiManager.INFO_ALREADY_INSTALLED,"Info"]
				elif zmdConfigured==0:
					self.initialStatusCode=[EpiGuiManager.INFO_ZMD_NOT_EXECUTED,"Warning"]
				elif zmdConfigured==-1:
					self.initialStatusCode=[EpiGuiManager.INFO_EPI_FAILED,"Warning"]

	#def _getInitialStatus

	def onCheckedPackages(self,pkgId,isChecked):

		if isChecked:
			self._managePkgSelected(pkgId,True)
		else:
			self._managePkgSelected(pkgId,False)

		if len(self.epiManager.packages_selected)==self.totalPackages:
			self.uncheckAll=True
		else:
			self.uncheckAll=False

		tmpParam={}
		tmpParam["isChecked"]=isChecked
		self._updatePackagesModel(tmpParam,pkgId)			
	
	#def onCheckedPackages

	def selectAll(self):

		if self.uncheckAll:
			active=False
		else:
			active=True

		pkgList=copy.deepcopy(self.packagesData)
		tmpParam={}
		tmpParam["isChecked"]=active
		for item in pkgList:
			if item["isChecked"]!=active:
				self._managePkgSelected(item["pkgId"],active)
				self._updatePackagesModel(tmpParam,item["pkgId"])
		
		self.uncheckAll=active
		
	#def selectAll

	def _updatePackagesModel(self,param,pkgId):

		for item in self.packagesData:
			if item["pkgId"]==pkgId:
				for element in param:
					if item[element]!=param[element]:
						item[element]=param[element]
						if element=="status":
							item["resultProcess"]=0
					else:
						if element=="status":
							item["resultProcess"]=1 
				break

	#def _updatePackagesModel

	def _managePkgSelected(self,pkgId,active=True):

		if active:
			if pkgId not in self.epiManager.packages_selected:
				self.epiManager.packages_selected.append(pkgId)
		else:
			if pkgId in self.epiManager.packages_selected:
				self.epiManager.packages_selected.remove(pkgId)

		#self.packagesSelected=copy.deepcopy(self.epiManager.packages_selected)
	
	#def _managePkgSelected

	def checkInternetConnection(self):

		self.checkingUrl1_t=threading.Thread(target=self._checkingUrl1)
		self.checkingUrl2_t=threading.Thread(target=self._checkingUrl2)
		self.checkingUrl1_t.daemon=True
		self.checkingUrl2_t.daemon=True
		self.checkingUrl1_t.start()
		self.checkingUrl2_t.start()

	#def checkInternetConnection

	def _checkingUrl1(self):

		self.connection=self.epiManager.check_connection(self.epiManager.urltocheck1)
		self.firstConnection=self.connection[0]

	#def _checkingUrl1	

	def _checkingUrl2(self):

		self.connection=self.epiManager.check_connection(self.epiManager.urltocheck2)
		self.secondConnection=self.connection[0]

	#def _checkingUrl2

	def getResultCheckConnection(self):

 		self.endCheck=False
 		error=False
 		urlError=False
 		self.retConnection=[False,""]

 		if self.checkingUrl1_t.is_alive() and self.checkingUrl2_t.is_alive():
 			pass
 		else:
 			if not self.firstConnection and not self.secondConnection:
 				if self.checkingUrl1_t.is_alive() or self.checkingUrl2_t.is_alive():
 					pass
 				else:
 					self.endCheck=True
 			else:
 				self.endCheck=True

 		if self.endCheck:
 			if not self.firstConnection and not self.secondConnection:
 				error=True
 				msgError=EpiGuiManager.ERROR_INTERNET_CONNECTION
 				self._writeLog("%s:%s"%(msgError,self.connection[1]))
 				self.retConnection=[error,msgError]

	#def getResultCheckConnection

	def getEulasToCheck(self):

		self.eulasToCheck=copy.deepcopy(self.requiredEula)
		
		for item in range(len(self.eulasToCheck)-1, -1, -1):
			if self.eulasToCheck[item]["pkg_name"] not in self.epiManager.packages_selected:
				self.eulasToCheck.pop(item)
		
		self.eulasToShow=self.eulasToCheck.copy()
		self.eulaOrder=len(self.eulasToCheck)-1	
		self._writeLog("Required Eulas: %s"%(str(self.eulasToCheck)))		
	
	#def getEulasToCheck

	def acceptEula(self):

		self.eulaAccepted=True
		pkgId=self.eulasToShow[self.eulaOrder]["pkg_name"]
		self.eulasToCheck.pop(self.eulaOrder)
		self.eulasToShow.pop(self.eulaOrder)
		self.eulaOrder-=1
		self._writeLog("Accepted EULA of: %s"%pkgId)

	#def acceptEula

	def rejectEula(self):

		pkgId=self.eulasToShow[self.eulaOrder]["pkg_name"]
		if self.selectPkg:
			self._managePkgSelected(pkgId,False)
			tmpParam={}
			tmpParam["isChecked"]=False
			self._updatePackagesModel(tmpParam,pkgId)
		
		self.eulasToCheck.pop(self.eulaOrder)
		self.eulasToShow.pop(self.eulaOrder)
		self.eulaOrder-=1
		self._writeLog("Rejected EULA of: %s"%pkgId)

	#def rejectEula

	def clearCache(self):

		clear=False
		user=os.environ["USER"]
		installedVersion=self._getPackageVersion()
	
		if user=="root":
			versionFile="/root/.epi-gui.conf"
			cachePath1="/root/.cache/epi-gtk"
		else:
			versionFile="/home/%s/.config/epi-gui.conf"%user
			cachePath1="/home/%s/.cache/epi-gtk"%user
		
		if not os.path.exists(versionFile):
			with open(versionFile,'w') as fd:
				fd.write(installedVersion)
				fd.close()

			clear=True

		else:
			with open(versionFile,'r') as fd:
				fileVersion=fd.readline()
				fd.close()

			if fileVersion!=installedVersion:
				with open(versionFile,'w') as fd:
					fd.write(installedVersion)
					fd.close()
				clear=True
		
		if clear:
			if os.path.exists(cachePath1):
				shutil.rmtree(cachePath1)

	#def clearCache

	def checkRemoveMeta(self):

		self._clearEnvirontment()
		self._writeLog("Packages selected to uninstall: %s"%self.epiManager.packages_selected)
		self.stopUninstall=[False,""]
		self.metaRemovedWarning=self.epiManager.check_remove_meta()
		self._writeLog("Check remove meta-package. Packages blocked because remove metapackage.: %s"%self.epiManager.blockedRemovePkgsList)

		tmpParam={}
		tmpParam["resultProcess"]=-1

		if self.metaRemovedWarning:
			if len(self.epiManager.packages_selected)==len(self.epiManager.blockedRemovePkgsList):
				self.stopUninstall=[True,EpiGuiManager.ERROR_UNINSTALL_STOP_META]
				self._writeLog("Uninstall blocked due to remove metapackage warning")
			
		for item in self.packagesData:
			tmpParam["showSpinner"]=True
			if self.metaRemovedWarning:
				if item["pkgId"] in self.epiManager.blockedRemovePkgsList:
					tmpParam["showSpinner"]=False
				
			self._updatePackagesModel(tmpParam,item["pkgId"])

	#def checkRemoveMeta

	def initUnInstallProcess(self):

		self.removePkgLaunched=False
		self.removePkgDone=False
		self.checkRemoveLaunched=False
		self.checkRemoveDone=False
		
	#def initUnInstallProcess

	def getUninstallCommand(self):

		command=self.epiManager.uninstall_app(0)
		length=len(command)

		if length>0:
			command=self._createProcessToken(command,"uninstall")

		return command

	#def getUninstallCommand

	def _createProcessToken(self,command,action):

		if action=="keys":
			self.tokenKeys=tempfile.mkstemp('_keys')
			removeTmp=' rm -f ' + self.tokenKeys[1] + ';'+'\n'
		elif action=="keyring":
			self.tokenKeyring=tempfile.mkstemp('_keyring')
			removeTmp=' rm -f ' + self.tokenKeyring[1] + ';'+'\n'
		elif action=="download":
			self.tokenDownload=tempfile.mkstemp('_download')
			removeTmp=' rm -f ' + self.tokenDownload[1] + ';'+'\n'
		elif action=="preinstall":
			self.tokenPreinstall=tempfile.mkstemp('_preinstall')	
			removeTmp=' rm -f ' + self.tokenPreinstall[1] + ';'+'\n'
		elif action=="arquitecture":
			self.tokenArquitecture=tempfile.mkstemp('_arquitecture')	
			removeTmp=' rm -f ' + self.tokenArquitecture[1] + ';'+'\n'	
		elif action=="updaterepos":
			self.tokenUpdaterepos=tempfile.mkstemp('_updaterepos')	
			removeTmp=' rm -f ' + self.tokenUpdaterepos[1] + ';'+'\n'	
		elif action=="install":
			self.tokenInstall=tempfile.mkstemp('_install')
			removeTmp=' rm -f ' + self.tokenInstall[1] +';'+'\n'
		elif action=="postinstall":	
			self.tokenPostinstall=tempfile.mkstemp('_postinstall')
			removeTmp=' rm -f ' + self.tokenPostinstall[1] +';'+'\n'
		elif action=="uninstall":
			self.tokenUninstall=tempfile.mkstemp('_uninstall')
			removeTmp=' rm -f ' + self.tokenUninstall[1] +';'+'\n'

		cmd='%s 2>&1 | tee -a %s; %s;\n'%(command,self.konsoleLog,removeTmp)

		return cmd

	#def _createProcessToken

	def checkRemove(self):

		self.remove=["","",""]

		uninstallStatus,remove=self.epiManager.check_install_remove("uninstall")
		self._updateProcessModelInfo(uninstallStatus)
		self.checkRemoveDone=True

		if remove:
			if len(self.epiManager.blockedRemovePkgsList)>0:
				msgCode=EpiGuiManager.WARNING_UNINSTALL_PROCESS
				typeMsg="Warning"
			else:
				msgCode=EpiGuiManager.SUCCESS_UNINSTALL_PROCESS
				typeMsg="Ok"

			self.epiManager.zerocenter_feedback(0,"uninstall",True)

		else:
			msgCode=EpiGuiManager.ERROR_UNINSTALL_FAILED
			typeMsg="Error"
			self.epiManager.zerocenter_feedback(0,"uninstall",False)

		self.remove=[remove,msgCode,typeMsg]
		self._writeLog("Uninstall process. Result: %s - Code:%s"%(typeMsg,msgCode))
		self._writeLogTerminal("Unistall")

	#def checkRemove

	def _updateProcessModelInfo(self,uninstallStatus):

		pkgIndex=0
		for element in self.info[0]["pkg_list"]:
			if element["name"] in self.epiManager.packages_selected:
				tmpParam={}
				tmpParam["status"]=uninstallStatus[element["name"]]
				tmpParam["pkgIcon"]=self._getPkgIcon(0,pkgIndex,tmpParam["status"])
				tmpParam["showSpinner"]=True
				self._updatePackagesModel(tmpParam,element["name"])
				if uninstallStatus[element["name"]]!='installed':
					if element["name"] in self.pkgsInstalled:
						self.pkgsInstalled.remove(element["name"])

			pkgIndex+=1	
	
	#def _updateProcessModelInfo

	def _getPackageVersion(self):

		command = "LANG=C LANGUAGE=en apt-cache policy epi-gtk"
		p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE)
		installed = None
		for line in iter(p.stdout.readline,b""):
			if type(line) is bytes:
				line=line.decode()

			stripedline = line.strip()
			if stripedline.startswith("Installed"):
				installed = stripedline.replace("Installed: ","")

		return installed

	#def _getPackageVersion

	def _writeLog(self,msg):

		syslog.openlog("EPI")
		syslog.syslog(msg)	

	#def _writeLog

	def _writeLogTerminal(self,process):

		syslog.openlog("EPI")
		syslog.syslog("%s process details"%process)
		content=""
		
		if os.path.exists(self.konsoleLog):
			with open(self.konsoleLog,'r') as fd:
				content=fd.readlines()

		if len(content)>0:
			for line in content:
				self._writeLog(line)
		else:
			self._writeLog("KonsoleLog is empty")

		os.remove(self.konsoleLog)
		
	#def _writeLogTerminal

	def _clearEnvirontment(self):

		if os.path.exists(self.konsoleLog):
			os.remove(self.konsoleLog)

	#def _clearEnvirontment			

#class EpiGuiManager
