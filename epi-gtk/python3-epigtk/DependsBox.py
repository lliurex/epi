#!/usr/bin/env python3


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,Gio,GObject,GLib,Gdk


from . import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext

class DependsBox(Gtk.VBox):
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)

		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)


		self.css_file=self.core.rsrc_dir+"epi-gtk.css"

		self.main_box=builder.get_object("deb_depends_box")
		self.deb_depends_label_box=builder.get_object("deb_depends_label_box")
		self.deb_depends_error_img=builder.get_object("deb depends_error_img")
		self.deb_depends_label=builder.get_object("deb_depends_label")

		self.list_depends_box=builder.get_object("list_depends_box")
		self.scrolledwindow_deb=builder.get_object("scrolledwindow_deb")
		self.viewport_deb=builder.get_object("viewport_deb")

		self.depends_label=builder.get_object("depends_label")
		self.depends_label.set_margin_right(10)
		self.depends_label.set_alignment(0,1)
		self.depends_label.set_justify(Gtk.Justification.FILL)
		self.depends_label.set_line_wrap(True)
		self.depends_label.set_valign(Gtk.Align.START)
		self.depends_label.set_halign(Gtk.Align.FILL)


		self.scrolledwindow_deb.set_shadow_type(Gtk.ShadowType.NONE)
		self.scrolledwindow_deb.set_overlay_scrolling(True)
		self.scrolledwindow_deb.set_kinetic_scrolling(True)

		self.scrolledwindow_deb.set_size_request(0,100)
		
		self.pack_start(self.main_box,True,True,0)

		self.set_css_info()

		
		#self.init_threads()

				
	#def __init__

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.deb_depends_label_box.set_name("ERROR_BOX")
		self.deb_depends_label.set_name("FEEDBACK_LABEL")
		self.depends_label.set_name("FEEDBACK_LABEL")
		self.list_depends_box.set_name("DEPEND_BOX")	

	#def set-css_info
	
		
	

		
#class DependsBox

from . import Core