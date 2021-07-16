#!/usr/bin/env python3

import os
import tempfile
import datetime
import time
import json
import re


import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')

from gi.repository import Gtk, Pango, PangoCairo,GdkPixbuf,Gdk

import cairo


HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11' }


class IconsManager:
	
	def __init__(self):
		
		self.core=Core.Core.get_core()
		self.check_image=self.core.rsrc_dir+"check.png"
		self.distro_name="lliurex"
		
		self.icons_path="/var/lib/app-info/icons/"
		self.dists=["focal","focal-updates","focal-security"]
		self.components=["main","restricted","universe","multiverse"]
		self.icon_dates_file="downloaded_icons.dates"
		
		#self.distro_name="ubuntu"
		
		self.icon_db=Gtk.IconTheme()
		self.icon_db.set_custom_theme("Breeze")
		
		
		#self.icon_db.set_custom_theme("Vibrancy-Dark-Orange")
		#self.package_icon=self.icon_db.lookup_icon("package",64,Gtk.IconLookupFlags.FORCE_SVG ).get_filename()
		self.package_icon="/usr/lib/python3/dist-packages/epigtk/rsrc/local_deb.png"
		
	#def init

	def get_icon(self,debian_name,icon,component=None):
		

		ret_icon=""
		if icon==None:
			icon=""
		
		
		ret_icon=self.icon_db.lookup_icon(debian_name,64,Gtk.IconLookupFlags.FORCE_SVG)
		if ret_icon!=None:
			return ret_icon.get_filename()


		ret_icon=self.icon_db.lookup_icon(icon,64,Gtk.IconLookupFlags.FORCE_SVG)
		if ret_icon!=None:
			return ret_icon.get_filename()	
			
		if len(icon)>0:
			
			for dist in self.dists:
				# "64x64/" is included in pkg_info["icon"]
				if not re.match("[0-9]*x[0-9]*\/",icon):
					if "64x64/" not in icon:
						icon="64x64/" + icon
						if debian_name!="":
							if debian_name+"_" not in icon:
								icon=icon.replace(debian_name,debian_name+"_"+debian_name)
										
				if component!="":
					#tmp_path=self.distro_name+"-"+dist+"-"+component
					ret_icon=self.icons_path+"%s/%s"%(component,icon)
					if os.path.exists(ret_icon):
						return ret_icon
				
				for item in self.components:
					tmp_path=self.distro_name+"-"+dist+"-"+item
					ret_icon=self.icons_path+"%s/%s"%(tmp_path,icon)
					if os.path.exists(ret_icon):
						return ret_icon
					else:
						tmp_path="ubuntu"+"-"+dist+"-"+item
						ret_icon=self.icons_path+"%s/%s"%(tmp_path,icon)
						if os.path.exists(ret_icon):
							return ret_icon		
			
		
		ret_icon=self.package_icon
		return ret_icon
		
	#def get_icon

	def search_icon(self,pkg,path,icon,component):

		icon_file=self.get_icon(pkg,icon,component)
		if icon_file=="" or "local_deb" in icon_file:
			if os.path.exists(os.path.join(path,icon)):
				icon_file=os.path.join(path,icon)
			else:
				icon_file=self.package_icon
		
		return icon_file

	#def search_icon	

	def create_pixbuf(self,icon):

		try:
			image=Gtk.Image.new_from_file(icon)
			surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,48,48)
			ctx=cairo.Context(surface)

			lg1 = cairo.LinearGradient(0.0,0.0, 0.0, 48)
			lg1.add_color_stop_rgba(0, 255.0, 255.0, 255.0, 1)
			lg1.add_color_stop_rgba(1, 255.0, 255.0, 255.0, 1)
			ctx.rectangle(0, 0, 48, 48)
			ctx.set_source(lg1)
			ctx.fill()
			pixbuf=image.get_pixbuf()
			pixbuf=pixbuf.scale_simple(48,48,GdkPixbuf.InterpType.BILINEAR)

			Gdk.cairo_set_source_pixbuf(ctx,pixbuf,0,0)
			ctx.paint()

			img=cairo.ImageSurface.create_from_png(self.check_image)
			ctx.set_source_surface(img,30,30)
			ctx.fill()
			ctx.paint()
			
			px=Gdk.pixbuf_get_from_surface(surface,0,0,48,48)

			return px
		except Exception as e:
			print(str(e))
			px=""
			return px	

	#def create_pixbuf

#class IconsManager	


from . import Core