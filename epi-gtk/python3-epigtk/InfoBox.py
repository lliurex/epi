#!/usr/bin/env python3


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib,Gdk

from . import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext

class InfoBox(Gtk.VBox):
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)

		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"epi-gtk.css"

		self.icon_size=64
		self.details_max_width=30
		self.app_max_width=30
		self.short_description_max_width=60

		self.main_box=builder.get_object("info_box")
		self.icon=builder.get_object("icon")
		self.icon.set_size_request(64,64)
		self.name_label=builder.get_object("name_label")
		self.name_label.set_max_width_chars(self.app_max_width)
		self.name_label.set_ellipsize(Pango.EllipsizeMode.END)
		self.name_label.set_alignment(0,1)

		self.summary_label=builder.get_object("summary_label")
		self.summary_label.set_alignment(0,0)
		self.summary_label.set_max_width_chars(self.short_description_max_width)
		self.summary_label.set_ellipsize(Pango.EllipsizeMode.END)

		self.scrolledwindow_desc=builder.get_object("scrolledwindow_desc")
		self.viewport_desc=builder.get_object("viewport_desc")

		self.description_box=builder.get_object("description_box")
		self.description_label=builder.get_object("description_label")
		self.description_label.set_margin_right(10)
		self.description_label.set_alignment(0,1)
		self.description_label.set_justify(Gtk.Justification.FILL)
		self.description_label.set_line_wrap(True)
		self.description_label.set_valign(Gtk.Align.START)
		self.description_label.set_halign(Gtk.Align.FILL)


		self.scrolledwindow_desc.set_shadow_type(Gtk.ShadowType.NONE)
		self.scrolledwindow_desc.set_overlay_scrolling(True)
		self.scrolledwindow_desc.set_kinetic_scrolling(True)

		self.scrolledwindow_desc.set_size_request(0,170)
		

		
		self.pack_start(self.main_box,True,True,0)
		self.set_css_info()
		
				
	#def __init__

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.name_label.set_name("TITLE")
		self.summary_label.set_name("SHORT_DESCRIPTION")
		self.description_label.set_name("FULL_DESCRIPTION")	
		self.description_box.set_name("DEPEND_BOX")
			
	#def set-css_info
	
	
		
#class InfoBox

from . import Core