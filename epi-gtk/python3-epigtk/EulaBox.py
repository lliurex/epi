#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,Gdk,Gio,GObject,GLib
gi.require_version('WebKit', '3.0')
from gi.repository import WebKit
import copy

import sys
import os
import html2text

from . import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext


class EulaBox(Gtk.VBox):
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)
		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"epi-gtk.css"

		self.eula_window=builder.get_object("eula_window")
		self.eula_window.set_default_size(600,700)
		self.eula_title=builder.get_object("eula_title")
		self.eula_pkg_name=builder.get_object("eula_pkg_name")
		self.webkit_box=builder.get_object("webkit_box")
		self.eula_buttons_box=builder.get_object("eula_buttons_box")
		self.cancel_eula_button=builder.get_object("cancel_eula_button")
		self.accept_eula_button=builder.get_object("accept_eula_button")

		self.scrolled_window = Gtk.ScrolledWindow()
		self.webview=None
		

		self.set_css_info()
		self.connect_signals()
		self.init_threads()		

				
	#def __init__

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.eula_title.set_name("OPTION_LABEL")
		self.eula_pkg_name.set_name("PKG_NAME")

	#def set_csss_info	

	def connect_signals(self):
		
		self.cancel_eula_button.connect("clicked",self.cancel_eula_button_clicked)
		self.accept_eula_button.connect("clicked",self.accept_eula_button_clicked)

	#def connect_signals

	def init_threads(self):

		GObject.threads_init()

	#def init_threads	

	def load_info(self,info):

		if self.webview==None:
			self.webview=WebKit.WebView()
			websettings=self.webview.get_settings()
			websettings.set_property('enable-default-context-menu', False)
			self.webview.set_settings(websettings)
			self.scrolled_window.add(self.webview)
			self.webkit_box.pack_start(self.scrolled_window,True,True,0)

		self.pkg_name=info["pkg_name"]
		self.eula_pkg_name.set_text(self.pkg_name)
		self.load_url(info["eula"])
		self.eula_window.show_all()

	#def load_info	

	def load_url(self,url):
		
		 self.webview.open(url)

	#def load_url

	def cancel_eula_button_clicked(self,widget):

		self.load_url("")
		
		if self.core.mainWindow.load_epi_conf[0]["selection_enabled"]["active"]:

			for item in self.core.epiBox.epi_list_box.get_children():
				for element in item.get_children():
					if element.id == self.pkg_name:
						item.get_children()[0].set_active(False)

			self.core.mainWindow.eulas_toshow.pop(self.core.mainWindow.eula_order)
			self.core.mainWindow.eula_order-=1
			self.core.mainWindow.accept_eula()
		else:
			self.eula_window.hide()
		


	#def cancel_eula_button_clicked
	
	def accept_eula_button_clicked(self,widget):

		self.core.mainWindow.eulas_tocheck.pop(self.core.mainWindow.eula_order)
		self.core.mainWindow.eulas_toshow.pop(self.core.mainWindow.eula_order)
		self.core.mainWindow.eula_order-=1
		self.load_url("")
		self.core.mainWindow.accept_eula()

	#def cancel_eula_button_clicked 	


#class EulaBox

from . import Core