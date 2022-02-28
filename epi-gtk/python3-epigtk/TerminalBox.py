#!/usr/bin/env python3


import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')

from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib,Gdk,Vte

import os

from . import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext

class TerminalBox(Gtk.VBox):
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)
		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"epi-gtk.css"
		self.terminal_config=self.core.rsrc_dir+"terminal.conf"
		self.main_box=builder.get_object("terminal_box")
		self.terminal_label=builder.get_object("terminal_label")
		self.viewport=builder.get_object("viewport")
		self.terminal_scrolled=builder.get_object("terminalScrolledWindow")
		
		self.vterminal=Vte.Terminal()
		self.vterminal.spawn_sync(
			Vte.PtyFlags.DEFAULT,
			os.environ['HOME'],
			#["/usr/sbin/dpkg-reconfigure", "xdm"],
			["/bin/bash","--rcfile",self.terminal_config],
			[],
			GLib.SpawnFlags.DO_NOT_REAP_CHILD,
			None,
			None,
		)
		font_terminal = Pango.FontDescription("monospace normal 9")

		self.vterminal.set_font(font_terminal)
		self.vterminal.set_scrollback_lines(-1)
		self.vterminal.set_sensitive(False)
		self.terminal_scrolled.add(self.vterminal)

		self.pack_start(self.main_box,True,True,0)
		self.pack_start(self.main_box,True,True,0)
		self.set_css_info()
		
	#def __init__

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.terminal_label.set_name("MSG_LABEL")	
			
	#def set-css_info
	
	def manage_vterminal(self,enabled_input,sensitive):

		self.vterminal.set_input_enabled(enabled_input)
		self.vterminal.set_sensitive(sensitive)	

	#def manage_vterminal		
	
#class TerminalBox

from . import Core