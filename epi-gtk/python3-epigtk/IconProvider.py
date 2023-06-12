#!/usr/bin/python3

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtSvg import *
from PySide2.QtQuick import QQuickImageProvider
import os

class IconProvider(QQuickImageProvider):

	def __init__(self):

		super(IconProvider,self).__init__(QQuickImageProvider.Image)
		self.checkImage="/usr/lib/python3/dist-packages/epigtk/rsrc/check.png"
		self.localPackage="/usr/lib/python3/dist-packages/epigtk/rsrc/package.png"

	#def __init__
	
	def requestImage(self,imagePath,size1,size2):

		return self.createIcon("/%s"%imagePath)

	#def requestImage

	def createIcon(self,imagePath):

		destImage=QImage()

		if "_OK" in imagePath:
			isInstalled=True
			appIcon=imagePath.split("_OK")[0]
		else:
			isInstalled=False
			appIcon=imagePath

		if os.path.exists(appIcon):
			if ".svg" in appIcon:
				tmpsvg=QSvgRenderer(appIcon)
				tmpImage=QImage(48,48,QImage.Format_ARGB32)
				tmpImage.fill("#00000000")
				p=QPainter()
				p.begin(tmpImage)
				tmpsvg.render(p)
				p.end()
				destImage=tmpImage
			else:
				destImage.load(appIcon,"png")
		else:
			destImage.load(self.localPackage,"png")
		
		s=QSize(48,48)
		destImage=destImage.scaled(s,aspectRatio=Qt.KeepAspectRatio,mode=Qt.SmoothTransformation)
		lastImage=QImage()
		lastImage.load(self.checkImage,"png")
		p=QPainter()
		p.begin(destImage)
		p.drawImage(0,0,destImage)
		if isInstalled:
			p.drawImage(30,30,lastImage)
			p.end()

		return destImage

	#def createIcon

#clas IconProvider
