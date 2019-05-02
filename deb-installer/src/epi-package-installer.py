#!/usr/bin/python3
import sys
import os
import shutil
import magic
import tempfile
import json
import subprocess

dbg=True

def _debug(msg):
	if dbg:
		print("Deb installer: %s"%msg)
#def _debug

def _generate_install_dir():
	installDir=''
	try:
		installDir=tempfile.mkdtemp()
	except:
		_debug("Couldn't create temp dir")

	return (installDir)
#def _generate_install_dir

def _get_deb_info(deb):
	sw_ok=True
	debInfo={}
	installDir=os.path.dirname(deb)
	os.makedirs("%s/debDir"%installDir)
	os.chdir("%s/debDir"%installDir)
	_debug("Extract control")
	subprocess.run(['ar','x',deb])
	_debug("Uncompress control")
	try:
		if os.path.isfile("control.tar.xz"):
			subprocess.run(['tar','Jxf',"control.tar.xz"])
		elif os.path.isfile("control.tar.gz"):
			subprocess.run(['tar','zxf',"control.tar.gz"])
	except:
		_debug("Failed to uncompress deb")
		sw_ok=False
	if sw_ok:
		#read control file
		f=open("control","r")
		f_lines=f.readlines()
		f.close()

		for line in f_lines:
			print(line)
			if line.startswith(" "):
				if oldInfo in debInfo.keys():
					debInfo[oldInfo]=("%s%s"%(debInfo[oldInfo],line)).rstrip()
			else:
				debInfo[line.split(":")[0]]=" ".join(line.split(" ")[1:]).rstrip()
				oldInfo=line.split(":")[0]
	return (debInfo)
#def _get_deb_info

def _begin_install_package(deb):
	mime=magic.Magic(mime=True)
	if ((os.path.isfile(deb)) and (mime.from_file(deb)=='application/vnd.debian.binary-package')):
		_generate_epi_file(deb)
	else:
		_debug("%s is an invalid file"%deb)

#def _begin_install_package

def _generate_epi_json(debInfo,deb):
	tmpDir=os.path.dirname(deb)
	debName=os.path.basename(deb)
	epiJson="%s/%s.epi"%(tmpDir,debInfo['Package'].replace(" ","_"))
	epi_json={}
	epi_json["type"]="localdeb"
	epi_json["pkg_list"]=[{"name":debInfo['Package'],'url_download':os.path.dirname(installFile),'version':{'all':debName}}]
	epi_json["script"]={"name":"%s/install_script.sh"%tmpDir}
	epi_json["required_root"]="true"

	with open(epiJson,'w') as f:
		json.dump(epi_json,f,indent=4)
	return(epiJson)
#def _generate_epi_json

def _generate_epi_script(debInfo,deb):
	tmpDir=os.path.dirname(deb)
	depends=[]
	for dep in debInfo['Depends'].split(', '):
		depends.append(dep.split(' ')[0])

	with open("%s/install_script.sh"%tmpDir,'w') as f:
		f.write("#!/bin/bash\n")
		f.write("case $ACTION in\n")
		f.write("\tpreInstall)\n")
		f.write("\t\tapt-get install %s\n"%','.join(depends))
		f.write("\t\t;;\n")
		f.write("\tgetInfo)\n")
		f.write("\t\techo \"%s\"\n"%debInfo['Description'])
		f.write("\t\t;;\n")
		f.write("\ttestInstall)\n")
		f.write("\t\tUNINSTALLABLE=\"\"\n")
		f.write("\t\tfor pkg in %s\n"%(' '.join(depends)))
		f.write("\t\tdo\n")
		f.write("\t\t\tif [ $(apt-cache search --names-only $pkg | wc -l) -eq 0 ]\n")
		f.write("\t\t\tthen\n")
		f.write("\t\t\t\tUNINSTALLABLE=$UNINSTALLABLE\",\"$pkg\n")
		f.write("\t\t\tfi\n")
		f.write("\t\tdone\n")
		f.write("\t\techo \"${UNINSTALLABLE/,/}\"\n")
		f.write("\t\t;;\n")
		f.write("esac\n")
		f.write("exit 0\n")
	os.chmod("%s/install_script.sh"%tmpDir,0o755)

#def generate_epi_script(debInfo,deb)

def _generate_epi_file(deb):
	sw_ok=True
	installDir=_generate_install_dir()
	if installDir:
		#copy deb to installDir
		try:
			debName=os.path.basename(deb)
			shutil.copyfile(deb,"%s/%s"%(installDir,debName))
			deb="%s/%s"%(installDir,debName)
		except Exception as e:
			_debug("%s couldn't be copied to %s: %s"%(deb,installDir,e))
			sw_ok=False
		
		if sw_ok:
			debInfo=_get_deb_info(deb)
			epiJson=_generate_epi_json(debInfo,deb)
			_generate_epi_script(debInfo,deb)
			if epiJson:
				print(epiJson)
				_debug("Launching %s"%epiJson)
				subprocess.run(['epi-gtk',epiJson])
		epi_dict={}
		epi_dict["type"]="localdeb"
#def generate_epi_file

def install_package(epi):
	pass
#def install_package
	
installFile=sys.argv[1]
_begin_install_package(installFile)


