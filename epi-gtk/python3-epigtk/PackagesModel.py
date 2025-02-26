#!/usr/bin/python3
import os
import sys
from PySide6 import QtCore, QtGui, QtQml

class PackagesModel(QtCore.QAbstractListModel):

	PkgIdRole= QtCore.Qt.UserRole + 1000
	ShowCbRole=QtCore.Qt.UserRole+1001
	IsCheckedRole=QtCore.Qt.UserRole+1002
	CustomNameRole=QtCore.Qt.UserRole+1003
	PkgIconRole=QtCore.Qt.UserRole+1004
	StatusRole=QtCore.Qt.UserRole+1005
	IsVisibleRole=QtCore.Qt.UserRole+1006
	ResultProcessRole=QtCore.Qt.UserRole+1007
	OrderRole=QtCore.Qt.UserRole+1008
	ShowSpinnerRole = QtCore.Qt.UserRole + 1009
	EntryPointRole = QtCore.Qt.UserRole+1010
	MetaInfoRole = QtCore.Qt.UserRole+1011


	def __init__(self,parent=None):
		
		super(PackagesModel, self).__init__(parent)
		self._entries =[]
	
	#def __init__

	def rowCount(self, parent=QtCore.QModelIndex()):
		
		if parent.isValid():
			return 0
		return len(self._entries)

	#def rowCount

	def data(self, index, role=QtCore.Qt.DisplayRole):
		
		if 0 <= index.row() < self.rowCount() and index.isValid():
			item = self._entries[index.row()]
			if role == PackagesModel.PkgIdRole:
				return item["pkgId"]
			elif role == PackagesModel.ShowCbRole:
				return item["showCb"]
			elif role == PackagesModel.IsCheckedRole:
				return item["isChecked"]
			elif role == PackagesModel.CustomNameRole:
				return item["customName"]
			elif role == PackagesModel.PkgIconRole:
				return item["pkgIcon"]
			elif role == PackagesModel.StatusRole:
				return item["status"]
			elif role == PackagesModel.IsVisibleRole:
				return item["isVisible"]
			elif role == PackagesModel.ResultProcessRole:
				return item["resultProcess"]
			elif role == PackagesModel.OrderRole:
				return item["order"]
			elif role == PackagesModel.ShowSpinnerRole:
				return item["showSpinner"]
			elif role == PackagesModel.EntryPointRole:
				return item["entryPoint"]
			elif role == PackagesModel.MetaInfoRole:
				return item["metaInfo"]

		#def data

	def roleNames(self):
		
		roles = dict()
		roles[PackagesModel.PkgIdRole] = b"pkgId"
		roles[PackagesModel.ShowCbRole] = b"showCb"
		roles[PackagesModel.IsCheckedRole] = b"isChecked"
		roles[PackagesModel.CustomNameRole] = b"customName"
		roles[PackagesModel.PkgIconRole] = b"pkgIcon"
		roles[PackagesModel.StatusRole] = b"status"
		roles[PackagesModel.IsVisibleRole] = b"isVisible"
		roles[PackagesModel.ResultProcessRole] = b"resultProcess"
		roles[PackagesModel.OrderRole] = b"order"
		roles[PackagesModel.ShowSpinnerRole] = b"showSpinner"
		roles[PackagesModel.EntryPointRole] = b"entryPoint"
		roles[PackagesModel.MetaInfoRole] = b"metaInfo"

		return roles

	#def roleName

	def appendRow(self,pkgid,scb,isc,cn,pkgic,st,isv,rpr,odr,ss,ep,mt):
		
		self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(),self.rowCount())
		self._entries.append(dict(pkgId=pkgid, showCb=scb, isChecked=isc, customName=cn, pkgIcon=pkgic, status=st, isVisible=isv, resultProcess=rpr, order=odr,showSpinner=ss,entryPoint=ep,metaInfo=mt))
		self.endInsertRows()

	#def appendRow

	def setData(self, index, valuesToUpdate, role=QtCore.Qt.EditRole):
		
		if role == QtCore.Qt.EditRole:
			row = index.row()
			for item in valuesToUpdate:
				for param in item:
					if param in ["status","showSpinner","pkgIcon","isVisible","isChecked","resultProcess"]:
						self._entries[row][param]=item[param]
						self.dataChanged.emit(index,index)

	#def setData

	def clear(self):
		
		count=self.rowCount()
		self.beginRemoveRows(QtCore.QModelIndex(), 0, count)
		self._entries.clear()
		self.endRemoveRows()
	
	#def clear
	
#class PackagesModel
