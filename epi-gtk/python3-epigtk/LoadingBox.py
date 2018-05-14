#!/usr/bin/env python3


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,Gio,GObject,GLib,Gdk


from . import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext

class LoadingBox(Gtk.VBox):
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)

		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)


		self.css_file=self.core.rsrc_dir+"epi-gtk.css"

		self.main_box=builder.get_object("loading_box")
		self.loading_label=builder.get_object("loading_label")
		self.loading_spinner=builder.get_object("loading_spinner")
		
		self.pack_start(self.main_box,True,True,0)

		self.set_css_info()

		
		#self.init_threads()

				
	#def __init__

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.loading_label.set_name("MSG_LABEL")
				
			
	#def set-css_info
	
		
	

		
#class LoadingBox

from . import Core