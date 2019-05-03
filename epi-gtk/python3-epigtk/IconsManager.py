#!/usr/bin/env python3

import urllib.request as urllib2
import os
import tempfile
import datetime
import time
import json

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11' }


class IconsManager:
	
	def __init__(self):
		
		self.distro_name="lliurex"
		self.base_url="http://appstream.ubuntu.com/data/"
		self.icons_url_file="icons-64x64.tar.gz"
		self.icons_path="/var/lib/app-info/icons/"
		self.dists=["xenial","xenial-updates","xenial-security"]
		self.components=["main","restricted","universe","multiverse"]
		
		
		self.icon_db=Gtk.IconTheme()
		#self.icon_db.set_custom_theme("Vibrancy-Dark-Orange")
		#self.package_icon=self.icon_db.lookup_icon("package",64,Gtk.IconLookupFlags.FORCE_SVG ).get_filename()
		self.package_icon="/usr/lib/python3/dist-packages/epigtk/rsrc/local_deb.svg"
		
	#def init

	def get_icon(self,debian_name,icon,component):
		
		#debian_name=pkg_info["package"]
		#icon=pkg_info["icon"]
		if icon==None:
			icon=""
		
		#component=pkg_info["component"]
		
		ret_icon=self.icon_db.lookup_icon(debian_name,64,Gtk.IconLookupFlags.FORCE_SVG)
		if ret_icon!=None:
			
			return ret_icon.get_filename()
			
		if len(icon)>0:
			
			for dist in self.dists:
				# "64x64/" is included in pkg_info["icon"]
				if "64x64/" not in icon:
					icon="64x64/" + icon
					if debian_name+"_"+debian_name not in icon:
						icon=icon.replace(debian_name,debian_name+"_"+debian_name)
										
				ret_icon=self.icons_path+"%s/%s"%(component,icon)
				if os.path.exists(ret_icon):
					return ret_icon
				
		ret_icon=self.package_icon
		return ret_icon
		
	#def get_icon

#class IconsManager	