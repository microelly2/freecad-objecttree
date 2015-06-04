# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- object tree
#--
#-- microelly 2015
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------



global fullRefresh, parentsView, childrensView, familyView, renderWidget
global doSomething,search, createTree, sayWidgetTree,cm,vlines,TypeIcon
global w, refresh

import os


class ConfigManager():

	def __init__(self,name):
		self.name="Plugins/"+name

	def get(self,param,default,defaultWindows=None,defaultMac=None):
		if not defaultWindows:
			defaultWindows=default
		if not defaultMac:
			defaultMac=default
		if default.__class__ == int:
			v=FreeCAD.ParamGet('User parameter:'+self.name).GetInt(param)
			if not v:
				FreeCAD.ParamGet('User parameter:'+self.name).SetInt(param,default)
		if default.__class__ == float:
			v=FreeCAD.ParamGet('User parameter:'+self.name).GetFloat(param)
			if not v:
				FreeCAD.ParamGet('User parameter:'+self.name).SetFloat(param,default)
		if default.__class__ == str:
			v=FreeCAD.ParamGet('User parameter:'+self.name).GetString(param)
			if not v:
				FreeCAD.ParamGet('User parameter:'+self.name).SetString(param,default)
		if default.__class__ == bool:
			v=FreeCAD.ParamGet('User parameter:'+self.name).GetBool(param)
			if not v:
				FreeCAD.ParamGet('User parameter:'+self.name).SetBool(param,default)
		if not v:
			v=default
		return v


cm=ConfigManager("ObjectTree")

def TypeIcon(typeId='Part::Cut'):
	
	typeIcons={
	'Part::MultiFuse' : "icons:Part_Fuse.svg",
	'Part::MultiCommon' : "icons:Part_Common.svg",
	'Sketcher::SketchObject' : "icons:Sketcher_Sketch.svg",
	#'Draft::Clone' : "Draft_Clone.svg",
	# 'App::DocumentObjectGroup' : icons:
	'Drawing::FeaturePage' : 'icons:Page.svg',
	'Drawing::FeatureViewPart' : 'icons:Draft_Drawing.svg'
	#'Drawing::FeatureViewPart' : 'icons:Drawing-orthoviews.svg',
	}

	tk=typeId.replace("::", "_");
	f2=QtCore.QFileInfo("icons:"+ tk + ".svg")
	if f2.exists():
		return QtGui.QIcon("icons:"+ tk + ".svg") 
	if typeIcons.has_key(typeId):
		f2=QtCore.QFileInfo(typeIcons[typeId])
		if f2.exists():
			return QtGui.QIcon(typeIcons[typeId])
	FreeCAD.Console.PrintError("TypeIcon: " + typeId + " - no Icon found \n")
	return QtGui.QIcon('icons:freecad.svg')


def createTree(obj,n,mode):
	if n<2: 
		tree={'obj':obj,'subs':[],'subtyp':n,'status':'normal','a_label':obj.Label,'a_typeId':obj.TypeId} 
	else:
		tree={'obj':obj,'subs':[],'subtyp':n,'status':'hide','a_label':obj.Label,'a_typeId':obj.TypeId} 
	
	print "--------------------"
	print obj.Label
	k=obj.OutList
	print "--------------------"
	for it in k:
		print it.Label, " => ",it.TypeId
	print "--------------------"
	
	if mode == 'parents':
		if obj.TypeId=='PartDesign::Mirrored' or obj.TypeId=='PartDesign::LinearPattern':
			k=obj.OutList
			for el in k:
				FreeCAD.Console.PrintMessage("\n: "+el.Label + "--"+el.TypeId + "\n")
			FreeCAD.Console.PrintMessage("\n size:" + str(len(k)) + "\n")
			#if len(k)>1:
			ske=k[-1]
			FreeCAD.Console.PrintMessage("Sonder: "+ske.Label)
			#else:
			#	stske=[]
			pad=k[0]
			stske=createTree(pad,n+2,mode)
			FreeCAD.Console.PrintMessage(" pad "+ pad.Label)
			tree1={'obj':ske,'subs':[stske],'subtyp':n+1,'status':'normal'} 
			tree['subs']=[tree1]
		elif obj.TypeId=='PartDesign::MultiTransform':
			k=obj.OutList
			for el in k:
				FreeCAD.Console.PrintMessage("\n: "+el.Label + "--"+el.TypeId + "\n")
			FreeCAD.Console.PrintMessage("\n size:" + str(len(k)) + "\n")
			#if len(k)>1:
			ske=k[0]
			FreeCAD.Console.PrintMessage("Sonder: "+ske.Label)
			# hier fehlt die hierarchie ...
			#else:
			#	stske=[]
			
			pad=k[-1]
			stske=createTree(pad,n+len(k)+0,mode)
			FreeCAD.Console.PrintMessage(" pad "+ pad.Label)
			treealt={'obj':ske,'subs':[stske],'subtyp':n+len(k)-1,'status':'normal'} 
			# tree['subs']=[treealt]
			k.pop()
			# k.reverse()
			
			# treealt=["intitree-----------------------------------"]
			print "#######"
			m=n+len(k)
			for it in k:
				print "++++++++++++++++"
				print it.Label," " ,it.TypeId," m",m
				treeneu={'obj':it,'subs':[treealt],'subtyp':m,'status':'normal','a_label':it.Label} 
				m -= 1
				treealt=treeneu
				import pprint
				pprint.pprint(treealt)
			print "########"
			tree['subs']=[treealt]
			tree['subtyp']=n



		else:
			for s in obj.OutList:
				st=createTree(s,n+1,mode)
				#st[s]['subtyp']=n
				tree['subs'].append(st)
	elif mode == 'children':
		for s in obj.InList:
			st=createTree(s,n+1,mode)
			#st[s]['subtyp']=n
			tree['subs'].append(st)
	else:
		FreeCAD.Console.PrintError("unknown mode:" + mode + "\n")
		raise Exception
	#FreeCAD.Console.PrintMessage(str(n) + " " + obj.Label +" typeId=")
	#FreeCAD.Console.PrintMessage(obj.TypeId +"\n")
	
	return tree

def sayTree(ot):
	ss="#"
	for k in ot.keys():
		if k=='subtyp': 
			ss= "* " * ot[k]
		if k == 'obj':
			name = ot[k].Label
#	print ss + name
	for s in ot['subs']:
			sayTree(s)

class MyWidget(QtGui.QWidget):
	def __init__(self, master,*args):
		QtGui.QWidget.__init__(self, *args)
		
		self.master=master
		FreeCAD.mywidget=self
		self.printed=[]
		#self.printed2=[]
#		
#	def myinit(self):
		layout = QtGui.QGridLayout()
		
		self.layout=layout
		self.layout.setAlignment(QtCore.Qt.AlignLeft)
		line=4
		self.mw=QtGui.QWidget()
		layout.setSpacing(0)
		
		self.mw.setLayout(layout)
		self.setWindowTitle("Object Design Workflow Tree")
		self.setStyleSheet("* {background-color:white;} *:focus { color:red;background-color:white;}")

		self.layout=layout
		self.line=line
		mlayout=QtGui.QVBoxLayout()
		self.mlayout=mlayout
		hlayout=QtGui.QHBoxLayout()
		self.hlayout=hlayout
		self.hw=QtGui.QWidget()
		self.hw.setLayout(self.hlayout)
		
		butti= QtGui.QPushButton(QtGui.QIcon('icons:view-refresh.svg'),"Refesh")
		butti.clicked.connect(fullRefresh) 
		self.hlayout.addWidget(butti)
		butti.clearFocus()
		butti= QtGui.QPushButton(QtGui.QIcon("icons:button_down.svg"),"Parents")
		butti.clicked.connect(parentsView) 
		self.hlayout.addWidget(butti)
		# butti= QtGui.QPushButton(QtGui.QIcon('/usr/lib/freecad/Mod/plugins/icons/web-refresh.png'),"View Children")
		butti= QtGui.QPushButton(QtGui.QIcon("icons:button_up.svg"),"Children")
		
		butti.clicked.connect(childrensView) 
		self.hlayout.addWidget(butti)
		butti= QtGui.QPushButton(QtGui.QIcon('/usr/lib/freecad/Mod/plugins/icons/web-refresh.png'),"Familiy")
		butti= QtGui.QPushButton(QtGui.QIcon('icons:Snap_Center.svg'),"Familiy")
		butti.clicked.connect(familyView) 
		self.hlayout.addWidget(butti)
		
		self.hw.setStyleSheet("QListWidget,QPushButton {border:none;text-align:left;}\
				QPushButton {border:0px solid red;text-align:left;}\
				QPushButton#mainLabel {border:0px solid green;text-align:left;background-color:yellow;padding:0px  5px 0px 0px;margin-right:10px;}\
				QPushButton#mainIcon {border:0px solid green;text-align:left;background-color:yellow;padding:0px  0px 0px 5px;}\
			QWidget2 {border:2px solid green;background-color:}")
		
		
		self.butti2= QtGui.QPushButton(QtGui.QIcon('/usr/lib/freecad/Mod/plugins/objecttree/icons/camera-photo.png'),"Snapshot")
		self.hlayout.addWidget(self.butti2)
		self.butti2.clicked.connect(renderWidget)
		
		self.butti2= QtGui.QPushButton(QtGui.QIcon('icons:Tree_Annotation.svg'),"Props")
		self.butti2.clicked.connect(doSomething)
		self.hlayout.addWidget(self.butti2)
		#self.butti2= QtGui.QPushButton(QtGui.QIcon('/usr/lib/freecad/Mod/plugins/icons/help.png'),"Search")
		#self.butti2= QtGui.QPushButton(QtGui.QIcon('/home/thomas/website_local/html/dokuwiki/data/media/story/ik.svg/view-select.svg'),"Search")
		self.butti2= QtGui.QPushButton(QtGui.QIcon("icons:"+ 'view-zoom-all.svg'),"Search")
		self.butti2.clicked.connect(search)
		self.hlayout.addWidget(self.butti2)
		butti= QtGui.QPushButton(QtGui.QIcon('icons:Part_Measure_Step_Done.svg'),"Close")
		butti.clicked.connect(self.hide) 
		self.hlayout.addWidget(butti)
		self.mlayout.addWidget(self.hw)
		self.mlayout.addWidget(self.mw)
		self.setLayout(mlayout)
		self.mw.setStyleSheet("QListWidget,QPushButton {border:none;text-align:left;}\
				QPushButton {border:0px solid red;text-align:left;}\
				QPushButton#mainLabel {border:0px solid green;text-align:left;background-color:yellow;padding:0px  5px 0px 0px;margin-right:10px;}\
				QPushButton#mainIcon {border:0px solid green;text-align:left;background-color:yellow;padding:0px  0px 0px 5px;}\
			QWidget2 {border:2px solid green;background-color:transparent}")
		# self.butti2.installEventFilter(self)
		FreeCAD.Console.PrintMessage('myinint done installed ')



# button left right double clicks
	def eventFilter(self, obj, event):
			if event.type() == QtCore.QEvent.MouseButtonPress:
				if event.button() == QtCore.Qt.LeftButton:
					#If image is left clicked, display a red bar.
					FreeCAD.Console.PrintMessage('one left\n')
				elif event.button() == QtCore.Qt.RightButton:
					FreeCAD.Console.PrintMessage('one right\n')
			elif event.type() == QtCore.QEvent.MouseButtonDblClick:
				#If image is double clicked, remove bar.
				FreeCAD.Console.PrintMessage('two\n')
			return super(MyWidget, self).eventFilter(obj, event)




	def addObj(self,ot,obj,row,count,mode,dir):
		global filled
		
		ox=cm.get('ox',1000)
		oy=cm.get('oy',1000)
		ax=cm.get('ax',1)
		ay=cm.get('ay',1)
		
		
		if dir == '-x':
			ax=-1
		
		pushButt = QtGui.QPushButton()
		try:
			butti= QtGui.QPushButton(QtGui.QIcon(obj.ViewObject.Proxy.getIcon()),"") 
		except:
			butti= QtGui.QPushButton(TypeIcon(obj.TypeId),"")
		tt="-: "+ str(oy+ay*self.line)
		tt=''
		if row==0:
			pushButt.setText(""+ obj.Label + "" + tt)
			pushButt.setObjectName("mainLabel")
			butti.setObjectName("mainIcon")
		else:
			pushButt.setText(obj.Label + tt)	
		
		lc=lambda: self.labelClick(ot)
		
		pushButt.clicked.connect(lc) 
		butti.clicked.connect(lc) 
		
		if obj in self.printed:
		#	pushButt.setText(obj.Label + "!")
			# butti= QtGui.QPushButton(QtGui.QIcon('/usr/lib/freecad/Mod/mylib/icons/mars.png'),"")
			
			pass 
		
		
		#pushButt.setStyleSheet("{border:2px solid green;color:green;}")
		
		self.printed.append(obj)
		if ax== -1:
			self.layout.addWidget(butti, oy+ay*self.line, ox+ax*3*row-1+1)
		else:
			self.layout.addWidget(butti, oy+ay*self.line, ox+ax*3*row)
		if ax== -1:
			self.layout.addWidget(pushButt, oy+ay*self.line, ox+ax*3*row+1)
		else:
			self.layout.addWidget(pushButt, oy+ay*self.line, ox+ax*3*row+1)
		subst=str(count)
#		if False and count >0:
#			butte= QtGui.QPushButton(QtGui.QIcon('/usr/lib/freecad/Mod/mylib/icons/mars.png'),subst)
#			self.layout.addWidget(butte, oy+self.line, ox+3*row+2)
		if row >0:
			if mode ==1  :
				butte= QtGui.QPushButton(QtGui.QIcon('/usr/lib/freecad/Mod/plugins/objecttree/icons/single.png'),"")
			elif mode ==0 :
				butte= QtGui.QPushButton(QtGui.QIcon('/usr/lib/freecad/Mod/plugins/objecttree/icons/start.png'),"")
			elif mode == -1:
				if ax== -1:
					butte= QtGui.QPushButton(QtGui.QIcon('/usr/lib/freecad/Mod/plugins/objecttree/icons/end2.png'),"")
				else:
					butte= QtGui.QPushButton(QtGui.QIcon('/usr/lib/freecad/Mod/plugins/objecttree/icons/end.png'),"")
			else:
				if ax== -1:
					butte= QtGui.QPushButton(QtGui.QIcon('/usr/lib/freecad/Mod/plugins/objecttree/icons/downl-l.png'),"" )
				else:
					butte= QtGui.QPushButton(QtGui.QIcon('/usr/lib/freecad/Mod/plugins/objecttree/icons/downl-r.png'),"" )
			if ax== -1:
				self.layout.addWidget(butte, oy+ay*self.line, ox+ax*3*row-1+2+1)
			else:
				self.layout.addWidget(butte, oy+ay*self.line, ox+ax*3*row-1)
			
			f=lambda: self.collapsTree(ot)
			
			if len(ot['subs']) >0 :
				butte.clicked.connect(f) 

			g=lambda: self.expandTree(ot)
			if ot['status'] == 'hide' and dir != '-x':
				if len(ot['subs']):
					buttx= QtGui.QPushButton(QtGui.QIcon('icons:add.svg'),"" )
					self.layout.addWidget(buttx, oy+ay*self.line, ox+ax*3*row+2)
					buttx.clicked.connect(g) 
			if ot['status'] == 'hide' and dir == '-x':
				if len(ot['subs']):
					buttx= QtGui.QPushButton(QtGui.QIcon('icons:add.svg'),"" )
					self.layout.addWidget(buttx, oy+ay*self.line, ox+ax*3*row+2-4)
					#buttx.clicked.connect(g) 
					buttx.clicked.connect(lc) 
			
			filled[self.line][3*row-1]=1
	
	def collapsTree(self,ot):
		ot['status']='hide'
		FreeCAD.Console.PrintMessage("collapsTree " +  ot['obj'].Label + "\n")
		FreeCAD.Console.PrintMessage("collapsTree " +  ot['status'] + "\n")
		refresh()

	def expandTree(self,ot):
		ot['status']='normal'
		FreeCAD.Console.PrintMessage("expandTree " +  ot['obj'].Label + "\n")
		FreeCAD.Console.PrintMessage("expandTree " +  ot['status'] + "\n")
		refresh()

	def labelClick(self,ot):
		FreeCAD.Console.PrintMessage("Label clicked  " +  ot['obj'].Label + "\n")
		FreeCADGui.Selection.clearSelection()
		FreeCADGui.Selection.addSelection(ot['obj'])
		fullRefresh('family')

vlines={}
vflines={}

def sayWidgetTree(w,ot,mode=0,dir='+x'):
	pos=ot['subtyp']
	w.addObj(ot,ot['obj'],pos,len(ot['subs']),mode,dir)
	#if obj in w.printed2:
	#	return
	#	pass
	# w.printed2.append(obj)
	for p in vlines.keys():
		if vlines[p]:
			if vlines[p]==1 and filled[w.line][3*p+2]<>1:
				butte= QtGui.QPushButton(QtGui.QIcon('/usr/lib/freecad/Mod/plugins/objecttree/icons/down.png'),"" )
	anz=len(ot['subs'])
	startline=w.line
	if ot['status']=='normal':
		for s in range(anz):
			# print (s)
			if s==0 and anz==1:
				mode2=1
				vlines[pos]=0
			elif s ==0: 
				mode2=0
				vlines[pos]=1
			elif s == anz -1:
				mode2= -1
				vlines[pos]=0
				w.line += 1
			else:
				mode2 = 2
				vlines[pos]=22
				w.line += 1
			sayWidgetTree(w,ot['subs'][s],mode2,dir)
			#w.line += 1
			endline=w.line
	


def refresh():
	#global otlist
	for k in w.mw.findChildren(QtGui.QPushButton):
		k.deleteLater()
	w.line=4
	#for ot in otlist:
	sayWidgetTree(w,w.ot,0)
	w.hide();w.show()


def fullRefresh(mode='parents'):
	global w,filled,ot,otlist
	ot=None
	w.ot=None
	w.printed=[]
	#w.printed2=[]
	w.line=4
	filled={}
	
	for x in range(100):
		filled[x]={}
		for y in range(100):
			#print x,y
			filled[x][y]=0
	
	for k in w.mw.findChildren(QtGui.QPushButton):
		k.deleteLater()
	#obs= [App.ActiveDocument.Fusion002,App.ActiveDocument.Cut001]
	#obs= [App.ActiveDocument.Cut001]
	#obs= [App.ActiveDocument.Fusion]
	obs= Gui.Selection.getSelection()
	if len(obs)<>1:
			w.layout.setAlignment(QtCore.Qt.AlignCenter)
			butte= QtGui.QPushButton(QtGui.QIcon('icons:freecad.svg'),"Error: Select your object of interest!" )
			butte.setObjectName("mainLabel")
			w.layout.addWidget(butte, 1,1)
			return
		
	obs=obs[0:1]

	otlist=[]
	for ob1 in obs:
		
		#otlist.append(ot)
		# import pprint;pprint.pprint(ot)

		if mode== 'children':
			ot=createTree(ob1,0,mode)
			dir = '-x'
			w.layout.setAlignment(QtCore.Qt.AlignLeft)
			sayWidgetTree(w,ot,0,dir)
		elif mode == 'parents':
			ot=createTree(ob1,0,mode)
			dir = '+x'
			w.layout.setAlignment(QtCore.Qt.AlignRight)
			sayWidgetTree(w,ot,0,dir)
		else:
			ot=createTree(ob1,0,'parents')
			sayWidgetTree(w,ot,0,'+x')
			ot2=createTree(ob1,0,'children')
			w.line=4
			w.printed=[]
			#w.printed2=[]
			w.layout.setAlignment(QtCore.Qt.AlignCenter)
			sayWidgetTree(w,ot2,0,'-x')
	w.ot=ot
	w.hide();w.show()



def parentsView():
	fullRefresh('parents')
	w.setWindowTitle("Object Design Workflow Tree - Parents View ")

def childrensView():
	fullRefresh('children')
	w.setWindowTitle("Object Design Workflow Tree - Children View ")

def familyView():
	fullRefresh('family')
	w.setWindowTitle("Object Design Workflow Tree - Children and Parents ")

#-----------------------

import re


class searchWidget(QtGui.QWidget):
	def __init__(self, *args):
		QtGui.QWidget.__init__(self, *args)
		self.vollabel = QtGui.QLabel('2. Select Object by Label ...')
		self.vollabel2 = QtGui.QLabel('1. Preselect Filter for Label ...')
	
		self.listWidget = QtGui.QListWidget() 
		#self.listWidget.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
		self.pat = QtGui.QLineEdit(self)
		self.pat.setText(".*")
		self.getlist()
		self.pat.textChanged.connect(self.run)

		for k in self.res:
			#if not self.config[k]['status'] == "ignore":
			
				# item = QtGui.QListWidgetItem(QtGui.QIcon('/usr/lib/freecad/Mod/plugins/icons/master.png'),k.Label)
				
				try:
					item= QtGui.QListWidgetItem(QtGui.QIcon(k.ViewObject.Proxy.getIcon()),k.Label) 
				except:
					item= QtGui.QListWidgetItem(TypeIcon(k.TypeId),k.Label)
				
				
				
				self.listWidget.addItem(item)
		layout = QtGui.QGridLayout()
		
		layout.addWidget(self.vollabel2, 1, 0,1,4)
		layout.addWidget(self.vollabel, 3, 0,1,4)
		
		layout.addWidget(self.listWidget, 4, 0,1,4)
		
		
		layout.addWidget(self.pat, 2, 0,1,4)
		
		self.pus = QtGui.QPushButton()
		self.pus.clicked.connect(self.runresult) 
		self.pus.setText("Set Selection")
		
		layout.addWidget(self.pus, 5, 0,1,4)
		self.setLayout(layout)
		self.setWindowTitle("Object Selector")



	def getlist(self):
		os=FreeCAD.ActiveDocument.Objects
		res=[]
		FreeCAD.Console.PrintMessage("pat:+++++++++++++\n")
		pat=str(self.pat.text())
		FreeCAD.Console.PrintMessage("pat:"+pat+"!\n")
		for oj in os:
			# print oj.Label
			
			
			if re.search(pat, oj.Label):
				FreeCAD.Console.PrintMessage(oj.Label)
				print oj.Label," okay" 
				res.append(oj)
		self.res=res


	def run(self):
		FreeCAD.Console.PrintMessage("k--------------- \n")
		# self.res=self.res[0]
		FreeCAD.Console.PrintMessage("k--------------- \n")
		k=True
		while  k:
			k=None
			k=self.listWidget.takeItem(0)
			
			
		#		FreeCAD.Console.PrintMessage("yy--------------- \n")
		#		FreeCAD.Console.PrintMessage(k)
		#		k.deleteLater()
		FreeCAD.Console.PrintMessage("k----dfd----------- \n")
		self.getlist()
		# self.res=[self.res[0]]
		for k in self.res:
			#if not self.config[k]['status'] == "ignore":
				# item = QtGui.QListWidgetItem(k.Label )
				
				try:
					item= QtGui.QListWidgetItem(QtGui.QIcon(k.ViewObject.Proxy.getIcon()),k.Label) 
				except:
					item= QtGui.QListWidgetItem(TypeIcon(k.TypeId),k.Label)
				
				
				self.listWidget.addItem(item)
		self.hide()
		self.show()

	def runresult(self):
		
		FreeCAD.Console.PrintMessage("k----dfd---runresult 1-------- \n")
		FreeCADGui.Selection.clearSelection()
		
		ll=self.listWidget.selectedItems()
		ls=ll[0].text()
		for s in self.res:
			if s.Label==ls:
				FreeCAD.Console.PrintMessage("k----dfd---runresult 1a-------- \n")
				FreeCADGui.Selection.addSelection(s)
		FreeCAD.Console.PrintMessage("k----dfd---runresult 2-------- \n")
		self.hide()
		fullRefresh('family')



def search():
	global searchWidget,w
	FreeCAD.Console.PrintMessage("Search -----------!!--------\n")
	try:
		t=searchWidget()
		FreeCAD.Console.PrintMessage("t:" +str(t))
		w.searchw=t
		t.show()
	except:
		FreeCAD.Console.PrintMessage("Fehler")




#-----------------------


def renderWidget():
	child=w
	child=w.mw
	image = QtGui.QPixmap(child.size())
	child.render(image)
	image.save( '/tmp/snapshot.png', 'PNG')
	import os
	os.system("eog /tmp/snapshot.png &")

import PySide

def doSomething():
	# display the properties dock window in foreground 
	FreeCAD.Console.PrintMessage("do something  ---------1--!!--------\n")
	mw=FreeCAD.Gui.getMainWindow()
	FreeCAD.Console.PrintMessage("do something  ----------2-!!--------\n")
	cn=mw.children()
	FreeCAD.Console.PrintMessage("do something  --------3b---!!--------\n")
	for c in cn:
		FreeCAD.Console.PrintMessage("do something  --------3a---!!--------\n")
		FreeCAD.Console.PrintMessage(c.__class__)
		if c.__class__ == QtGui.QDockWidget:
			FreeCAD.Console.PrintMessage("nix 1\n")
			FreeCAD.Console.PrintMessage(c.windowTitle())
			FreeCAD.Console.PrintMessage("nix 2\n")
			print c, c.objectName(), c.windowTitle()
			FreeCAD.Console.PrintMessage("do something  --------4---!!--------\n")
			if str(c.objectName())=="Property view":
				FreeCAD.Console.PrintMessage("do something  --------5---!!--------\n")
				c.show()
				c.raise_()
				FreeCAD.Console.PrintMessage("do something  --------6---!!--------\n")
		else:
			FreeCAD.Console.PrintMessage("nix\n")

# main 
if 1 or False:
	w=MyWidget(None)
	w.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
	#fullRefresh('parents')
	#fullRefresh('children')
	fullRefresh('family')
	w.show()

if False:
	ob1= App.ActiveDocument.MultiTransform
	mode='parents'
	ot=createTree(ob1,0,mode)
	print ot
	sayTree(ot)
	import pprint
	pprint.pprint(ot)
