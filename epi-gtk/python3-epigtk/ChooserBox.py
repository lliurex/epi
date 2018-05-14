#!/usr/bin/env python3


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,Pango,Gio,GObject,GLib,Gdk


from . import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext

class ChooserBox(Gtk.VBox):
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)

		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)


		self.css_file=self.core.rsrc_dir+"epi-gtk.css"

		self.main_box=builder.get_object("chooser_box")
		self.chooser_label=builder.get_object("chooser_label")
		self.filechooser_box=builder.get_object("filechooser_box")
		self.filechooser_label=builder.get_object("filechooser_label")
		self.filechooser_label.set_width_chars(60)
		self.filechooser_label.set_max_width_chars(60)
		self.filechooser_label.set_xalign(-1)
		self.filechooser_label.set_ellipsize(Pango.EllipsizeMode.END)
		self.filechooser_button=builder.get_object("filechooser_button")

		
		self.epi_loaded=None
		self.pack_start(self.main_box,True,True,0)

		self.set_css_info()
		self.connect_signals()

		
		#self.init_threads()

				
	#def __init__

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.filechooser_box.set_name("APP_BOX")
		self.chooser_label.set_name("OPTION_LABEL")
				
	#def set_css_info		
	
	def connect_signals(self):

		self.filechooser_button.connect("clicked",self.on_file_clicked)

	#def connect_signals	

	
	def on_file_clicked(self, widget):
		dialog = Gtk.FileChooserDialog(_("Please choose a epi file"), None,
			Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

		self.add_filters(dialog)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			file="<span font='Roboto'><b>"+dialog.get_filename()+"</b></span>"
			self.filechooser_label.set_markup(file)
			self.epi_loaded=dialog.get_filename()
		elif response == Gtk.ResponseType.CANCEL:
			if self.epi_loaded==None:
				self.filechooser_label.set_text("")


		if self.epi_loaded !=None:
			self.core.mainWindow.next_button.show()
		else:
			self.core.mainWindow.next_button.hide()
			
		dialog.destroy()	

	#def on_file_clicked	

	
	def add_filters(self, dialog):
		filter_epi = Gtk.FileFilter()
		filter_epi.set_name("Epi files")
		filter_epi.add_mime_type("application/easy-package-installer")
		dialog.add_filter(filter_epi)

    #def add_filters

		
#class ChooserBox

from . import Core