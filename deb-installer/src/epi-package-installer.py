#!/usr/bin/python3
import sys
import os
import shutil
import magic
import tempfile
import json
import subprocess
import grp,pwd

dbg=False
retCode=0

def _debug(msg):
	if dbg:
		print("Deb installer: %s"%msg)
#def _debug

def _generate_install_dir():
	global retCode
	installDir=''
	try:
		installDir=tempfile.mkdtemp()
	except:
		_debug("Couldn't create temp dir")
		retCode=1
	os.chown(installDir,pwd.getpwnam('_apt').pw_uid,grp.getgrnam('nogroup').gr_gid)
	return (installDir)
#def _generate_install_dir

def _get_deb_info(deb):
	global retCode
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
		retCode=1
	if not retCode:
		#read control file
		f_lines=[]
		try:
			f=open("control","r")
			f_lines=f.readlines()
			f.close()
		except Exception as e:
			_debug("%s"%e)
			retCode=1

		for line in f_lines:
			if line.startswith(" "):
				if oldKey in debInfo.keys():
					debInfo[oldKey]=("%s%s"%(debInfo[oldKey],line)).rstrip()
			else:
				key=line.split(":")[0]
				data=" ".join(line.split(" ")[1:]).rstrip()
				if key=='Description':
					data=data+"||"
				debInfo[key]=data
				oldKey=key
	return (debInfo)
#def _get_deb_info

def _begin_install_package(deb):
	global retCode
	mime=magic.Magic(mime=True)
	if ((os.path.isfile(deb)) and (mime.from_file(deb)=='application/vnd.debian.binary-package')):
		_generate_epi_file(deb)
	else:
		_debug("%s is an invalid file"%deb)
		retCode=1

#def _begin_install_package

def _generate_epi_json(debInfo,deb):
	global retCode
	tmpDir=os.path.dirname(deb)
	debName=os.path.basename(deb)
	epiJson=''
	#retCode controls the return code of the previous operations 
	if not retCode:
		epiJson="%s/%s.epi"%(tmpDir,debInfo['Package'].replace(" ","_"))
		epiFile={}
		epiFile["type"]="localdeb"
#		epiFile["pkg_list"]=[{"name":debInfo['Package'],'url_download':os.path.dirname(installFile),'version':{'all':debName}}]
		epiFile["pkg_list"]=[{"name":debInfo['Package'],'url_download':tmpDir,'version':{'all':debName}}]
		epiFile["script"]={"name":"%s/install_script.sh"%tmpDir,'remove':True}
		epiFile["required_root"]=True
		epiFile["required_dconf"]=True

		try:
			with open(epiJson,'w') as f:
				json.dump(epiFile,f,indent=4)
		except Exception as e:
			_debug("%s"%e)
			retCode=1
	return(epiJson)
#def _generate_epi_json

def _generate_epi_script(debInfo,deb):
	global retCode
	tmpDir=os.path.dirname(deb)
	try:
		with open("%s/install_script.sh"%tmpDir,'w') as f:
			f.write("#!/bin/bash\n")
			f.write("ACTION=\"$1\"\n")
			f.write("case $ACTION in\n")
			f.write("\tremove)\n")
			f.write("\t\tapt-get remove -y %s\n"%debInfo['Package'])
			f.write("\t\tTEST=$( dpkg-query -s  %s 2> /dev/null| grep Status | cut -d \" \" -f 4 )\n"%debInfo['Package'])
			f.write("\t\tif [ \"$TEST\" == 'installed' ];then\n")
			f.write("\t\t\texit 1\n")
			f.write("\t\tfi\n")
			f.write("\t\t;;\n")
			f.write("\ttestInstall)\n")
			if not retCode:
				f.write("\t\tapt-get update>/dev/null\"\"\n")
				f.write("\t\tRES=$(apt-get --simulate install %s 2>/tmp/err | awk 'BEGIN {sw=\"\"}{ver=0;if ($0~\" : \") sw=1; if ($0~\"[(]\") ver=1;if (sw==1 && ver==1) { print $0 } else if (sw==1) { print $1\" \"$2\" ( ) \"$3\" \"$4\" \"$5} }' | sed 's/.*: \(.*)\) .*/\\1/g;s/( *)//')\n"%deb)
                                
				f.write("\t\t[ -s /tmp/err ] && RES=${RES//$'\\n'/||}\"||\"$(cat /tmp/err) || RES=\"\"\n")
			else:
				f.write("\t\tRES=1\"\"\n")
			f.write("\t\techo \"${RES}\"\n")
			f.write("\t\t;;\n")
			f.write("\tgetInfo)\n")
			f.write("\t\techo \"%s\"\n"%debInfo['Description'])
			f.write("\t\t;;\n")
			f.write("esac\n")
			f.write("exit 0\n")
	except Exception as e:
		_debug("%s"%e)
		retCode=1
	os.chmod("%s/install_script.sh"%tmpDir,0o755)
#def _generate_epi_script

def _generate_epi_file(deb):
	global retCode
	installDir=_generate_install_dir()
	if installDir:
		#copy deb to installDir
		try:
			debName=os.path.basename(deb)
			shutil.copyfile(deb,"%s/%s"%(installDir,debName))
			deb="%s/%s"%(installDir,debName)
		except Exception as e:
			_debug("%s couldn't be copied to %s: %s"%(deb,installDir,e))
			retCode=1
		
		if not retCode:
			debInfo=_get_deb_info(deb)
			epiJson=_generate_epi_json(debInfo,deb)
			_generate_epi_script(debInfo,deb)
			if not retCode:
				_debug("Launching %s"%epiJson)
				subprocess.run(['epi-gtk',epiJson])
			else:
				subprocess.run(['epi-gtk',"--error"])
		else:
			subprocess.run(['epi-gtk',"--error"])
		#Remove tmp dir
		shutil.rmtree(installDir)
	elif retCode:
		subprocess.run(['epi-gtk',"--error"])
#def generate_epi_file
installFile=sys.argv[1]
_begin_install_package(installFile)


