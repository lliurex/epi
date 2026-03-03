#!/usr/bin/python3
import sys
import os
import shutil
import magic
import tempfile
import json
import subprocess
from multiprocessing import Process,Queue

dbg=False
retCode=0

class debInfo():
	def __init__(self,deb):
		self.dbg=True
		self.pkg=deb
		self.proc=[]
	#def __init_

	def _debug(self,msg):
		if self.dbg==True:
			print("debInfo: {}".format(msg))
	#def _debug

	def isValid(self):
		valid=False
		mime=magic.Magic(mime=True)
		if ((os.path.isfile(self.pkg)) and (mime.from_file(self.pkg)=='application/vnd.debian.binary-package')):
			valid=True
		return(valid)
	#def isValid

	def _unpackDeb(self,pkgFile):
		if os.path.isfile(pkgFile):
			subprocess.run(["ar","x",pkgFile,"--output",os.path.dirname(pkgFile)])
	#def _unpackDeb

	def _readDesktopF(self,desktopF):
		fcontent=""
		pkgData={"name":"","icon":"","description":"","summary":""}
		if os.path.isfile(desktopF):
			with open(desktopF,"r") as f:
				fcontent=f.read()
		for l in fcontent.split("\n"):
			if l.replace(" ","").lower().startswith("name="):
				pkgData["name"]=l.split("=",1)[-1]
			if l.replace(" ","").lower().startswith("comment="):
				pkgData["description"]=l.split("=",1)[-1]
			if l.replace(" ","").lower().startswith("genericname="):
				pkgData["summary"]=l.split("=",1)[-1]
		return(pkgData)
	#def _readDesktopF

	def _getInfoFromDesktopF(self,dataF,qData):
		desktopF=""
		iconF=""
		print("Load {}".format(dataF))
		tarOptions="Jtvf"
		if dataF.endswith(".gz"):
			tarOptions="ztvf"
		if os.path.isfile(dataF):
			out=subprocess.check_output(["tar",tarOptions,dataF],universal_newlines=True,encoding="utf8")
			for l in out.split("\n"):
				if "applications" in l and l.endswith("desktop"):
					desktopF="./{}".format(l.split("./",1)[-1])
					if iconF!="":
						break
				if "icons" in l and l.endswith("png"):
					iconF="./{}".format(l.split("./",1)[-1])
					if desktopF!="":
						break
		tarOptions=tarOptions.replace("t","x")
		if desktopF!="":
			subprocess.run(["tar",tarOptions,dataF,"-C",os.path.dirname(dataF),desktopF],universal_newlines=True,encoding="utf8")
			pkgData=self._readDesktopF(os.path.join(os.path.dirname(dataF),desktopF))
		if iconF!="":
			subprocess.run(["tar",tarOptions,dataF,"-C",os.path.dirname(dataF),iconF],universal_newlines=True,encoding="utf8")
			pkgData["icon"]=os.path.join(os.path.dirname(dataF),iconF)
		qData.put(pkgData)
	#def _getInfoFromDesktopF

	def _readControlF(self,controlF):
		fcontent=""
		pkgData={"pkgname":"","description":"","version":""}
		if os.path.isfile(controlF):
			with open(controlF,"r") as f:
				fcontent=f.read()
		for l in fcontent.split("\n"):
			if l.replace(" ","").lower().startswith("package:"):
				pkgData["pkgname"]=l.split(":",1)[-1].strip()
			if l.replace(" ","").lower().startswith("description:"):
				pkgData["pkgdescription"]=l.split(":",1)[-1].strip()
			if l.replace(" ","").lower().startswith("version:"):
				pkgData["pkgversion"]=l.split(":",1)[-1].strip()
		return(pkgData)
	#def _readControlF

	def _getInfoFromControlF(self,dataF,qData):
		controlF=""
		tarOptions="Jtvf"
		if dataF.endswith(".gz"):
			tarOptions="ztvf"
		if os.path.isfile(dataF):
			out=subprocess.check_output(["tar",tarOptions,dataF],universal_newlines=True,encoding="utf8")
			for l in out.split("\n"):
				if l.endswith("./control"):
					controlF="./{}".format(l.split("./",1)[-1])
					break
		tarOptions=tarOptions.replace("t","x")
		subprocess.run(["tar",tarOptions,dataF,"-C",os.path.dirname(dataF),controlF],universal_newlines=True,encoding="utf8")
		qData.put(self._readControlF(os.path.join(os.path.dirname(dataF),controlF)))
	#def _getInfoFromControlF

	def getPkgData(self):
		proc=[]
		pkgInfo={}
		wrkDir=tempfile.mkdtemp()
		shutil.copy(self.pkg,wrkDir)
		pkgFile=os.path.basename(self.pkg)
		self._unpackDeb(os.path.join(wrkDir,pkgFile))
		qData=Queue()
		dataF=os.path.join(wrkDir,"data.tar.xz")
		if os.path.isfile(dataF)==False:
			dataF=os.path.join(wrkDir,"data.tar.gz")
		p=Process(target=self._getInfoFromDesktopF,args=(dataF,qData))
		proc.append(p)
		p.start()
		controlF=os.path.join(wrkDir,"control.tar.xz")
		if os.path.isfile(controlF)==False:
			dataF=os.path.join(wrkDir,"control.tar.gz")
		p=Process(target=self._getInfoFromControlF,args=(controlF,qData))
		proc.append(p)
		p.start()
		for p in proc:
			p.join()
			pkgInfo.update(qData.get())
		pkgInfo["wrkDir"]=wrkDir
		return(pkgInfo)
	#def getPkgData
#class debInfo

class epiHelper():
	def __init__(self,pkgData):
		self._dbg=False
		self.pkgData=pkgData
		self.jepi=""
		self.sepi=""
	#def __init__

	def _jsonForEpi(self):
		pkgname=self.pkgData.get('pkgname',"").strip()
		tmpDir=self.pkgData["wrkDir"]
		epiJson="{}.epi".format(os.path.join(tmpDir,pkgname))
		if not os.path.isfile(epiJson):
			name=self.pkgData.get('name',"").strip()
			if len(name)==0:
				name=pkgname
			desc=self.pkgData.get('description',"").strip()
			pkgdesc=self.pkgData.get('pkgdescription',"").strip()
			if len(desc)==0:
				desc=pkgdesc
			icon=self.pkgData.get('icon','')
			version=self.pkgData.get("version","")
			if len(version)==0:
				version="all"
			epiFile={}
			epiFile["type"]="file"
			epiFile["pkg_list"]=[{"name":pkgname,"custom_name":"{}: {}".format(name,desc),"key_store":pkgname,'url_download':'','custom_icon':os.path.basename(icon),'version':{version:name}}]
			epiFile["script"]={"name":"{0}_script.sh".format(os.path.join(tmpDir,pkgname)),'download':True,'remove':True,'getStatus':True,'getInfo':True}
			if icon!="":
				epiFile["custom_icon_path"]=os.path.dirname(icon)
			epiFile["required_root"]=True
			epiFile["check_zomando_state"]=False
			try:
				with open(epiJson,'w') as f:
					json.dump(epiFile,f,indent=4)
			except Exception as e:
				_debug("Helper {}".format(e))
				retCode=1
		return(epiJson)
	#def _jsonForEpi

	def _populateEpi(self,epiScript,commands):
		with open(epiScript,'w') as f:
			f.write("#!/bin/bash\n")
			f.write("function getStatus()\n{")
			f.write("\t\t{}\n".format(commands.get('statusTestLine')))
			f.write("\t\tif [ \"$TEST\" == 'installed' ];then\n")
			f.write("\t\t\tINSTALLED=0\n")
			f.write("\t\telse\n")
			f.write("\t\t\tINSTALLED=1\n")
			f.write("\t\tfi\n")
			f.write("}\n")
			f.write("ACTION=\"$1\"\n")
			f.write("ERR=0\n")
			f.write("case $ACTION in\n")
			f.write("\tremove)\n")
			f.write("\t\t{}\n".format(commands.get('removeCmd')))
			for command in commands.get('removeCmdLine',[]):
				f.write("\t\t{}\n".format(command))
			f.write("\t\t;;\n")
			f.write("\tinstallPackage)\n")
			f.write("\t\t{}\n".format(commands.get('installCmd')))
			for command in commands.get('installCmdLine',[]):
				f.write("\t\t{}\n".format(command))
			f.write("\t\t;;\n")
			f.write("\ttestInstall)\n")	
			f.write("\t\techo \"0\"\n")
			f.write("\t\t;;\n")
			f.write("\tgetInfo)\n")
			f.write("\t\techo \"{}\"\n".format(self.pkgData['description']))
			f.write("\t\t;;\n")
			f.write("\tgetStatus)\n")
			f.write("\t\tgetStatus\n")
			f.write("\t\techo $INSTALLED\n")
			f.write("\t\t;;\n")
			f.write("\tdownload)\n")
			f.write("\t\techo \"Installing...\"\n")
			f.write("\t\t;;\n")
			f.write("esac\n")

			f.write("exit $ERR\n")
	#def _populateEpi

	def _getCommandsForPackage(self,pkgname,localdeb):
		commands={}
		(installCmd,installCmdLine,removeCmd,removeCmdLine,statusTestLine)=("",[],"",[],"")
		#pkcon has a bug detecting network if there's no network under NM (fails with systemd-networkd)
		#Temporary use apt until bug fix
		#FIX PKGNAME
		installCmd="export DEBIAN_FRONTEND=noninteractive"
		installCmdLine.append("export DEBIAN_PRIORITY=critical")
		installCmdLine.append("apt-get -qy -o \"Dpkg::Options::=--force-confdef\" -o \"Dpkg::Options::=--force-confold\" install \"{}\" 2>&1;ERR=$?".format(localdeb))
		removeCmd="apt remove -y {} 2>&1;ERR=$?".format(pkgname)
		removeCmdLine.append("TEST=$(pkcon resolve --filter installed {0}| grep {0} > /dev/null && echo 'installed')".format(pkgname))
		removeCmdLine.append("if [ \"$TEST\" == 'installed' ];then")
		removeCmdLine.append("exit 1")
		removeCmdLine.append("fi")
		statusTestLine=("TEST=$(pkcon resolve --filter installed {0}| grep {0} > /dev/null && echo 'installed')".format(pkgname))
		commands['installCmd']=installCmd
		commands['installCmdLine']=installCmdLine
		commands['removeCmd']=removeCmd
		commands['removeCmdLine']=removeCmdLine
		commands['statusTestLine']=statusTestLine
		return(commands)
	#def _getCommandsForPackage

	def _shForEpi(self):
		pkgname=self.pkgData.get('pkgname',"").strip()
		tmpDir=self.pkgData["wrkDir"]
		epiScript="{}_script.sh".format(os.path.join(tmpDir,pkgname))
		if not (os.path.isfile(epiScript)):
			commands=self._getCommandsForPackage(pkgname,self.pkgData["deb"])
			self._populateEpi(epiScript,commands)
			if os.path.isfile(epiScript):
				os.chmod(epiScript,0o755)
		return(epiScript)
	#def _shForEpi

	def generateEpi(self):
		self.jepi=self._jsonForEpi()
		self.sepi=self._shForEpi()
	#def generateEpi
#class epiHelper

#### MAIN ####
if len(sys.argv)>1:
	localDeb=sys.argv[1]
	deb=debInfo(localDeb)
	if deb.isValid()==False:
		print("{} is not a valid deb package.".format(localDeb))
		sys.exit(1)
	pkgData=deb.getPkgData()
	pkgData["deb"]=localDeb
	epi=epiHelper(pkgData)
	epi.generateEpi()
	if os.path.isfile(epi.jepi):
		subprocess.run(['epi-gtk',epi.jepi])
	if pkgData.get("wrkDir","")!="":
		if os.path.isdir(pkgData["wrkDir"]):
			shutil.rmtree(pkgData["wrkDir"])

