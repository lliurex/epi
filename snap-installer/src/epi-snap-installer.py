#!/usr/bin/python3
import sys
import os
import shutil
import magic
import tempfile
import json
import subprocess
import grp,pwd
import logging

dbg=False
retCode=0

def _debug(msg):
	if dbg:
		logging.warning("snap installer: %s"%str(msg))
#def _debug

def _generate_install_dir():
	global retCode
	installDir=''
	try:
		installDir=tempfile.mkdtemp()
	except:
		_debug("Couldn't create temp dir")
		retCode=1
	return (installDir)
#def _generate_install_dir

logging.basicConfig(format='%(message)s')
installFile=sys.argv[1]
_begin_install_package(installFile)

