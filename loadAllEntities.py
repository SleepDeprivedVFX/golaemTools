from maya import cmds
import maya.mel as mel
from functools import partial
import os, time

__author__ = 'Adam Benson'
__version__ = '1.0'

class loadAllEntities(object):
	"""docstring for loadAllEntities"""
	def __init__(self):
		super(loadAllEntities, self).__init__()
		self.path = 'K:/Maya/scenes/Assets/cre'

	def createEntity(self):
		entity = mel.eval('glmCrowdEntityTypeNodeCmd')
		cmds.select('entityType*', r=True)
		entities = cmds.ls(sl=True, type='CrowdEntityTypeNode')
		cmds.select(entities, r=True)
		cmds.pickWalk(d='up')
		selectedEntities = cmds.ls(sl=True)
		countAllUnnamedEntities = len(selectedEntities)
		newEntity = selectedEntities[countAllUnnamedEntities - 1]
		cmds.select(newEntity, r=True)
		return newEntity
		
	def getCharacterList(self):
		projectRoot = cmds.workspace(q=True, rd=True)
		folders = []
		characters = []
		getOSList = os.listdir(self.path)
		for this in getOSList:
			if os.path.isdir(os.path.join(self.path, this)):
				folders.append(this)
		for this in folders:
			char = '%s/golaem/char' % this
			fbx = '%s/golaem/FBX' % this
			shaders = '%s/golaem/shaders' % this
			if os.path.isdir(os.path.join(self.path, char)) and os.path.isdir(os.path.join(self.path, fbx)) and os.path.isdir(os.path.join(self.path, shaders)):
				characters.append(this)
		return characters

	def findLatestFile(self, path, type):
		filesInPath = sorted(os.listdir(path))
		for thisFile in filesInPath:
			if type not in thisFile:
				filesInPath.remove(thisFile)
		latestFile = filesInPath[-1]
		return latestFile
		
	def loadTextures(self, char, path):
		shaderFile = self.findLatestFile(path, '.mb')
		shaderPath = (path + '/' + shaderFile)
		nsName = ('%s_NS' % char)
		cmds.file(shaderPath, i=True, type='mayaBinary')
		print shaderPath
		
		
	def loadAllEntities(self, *args):
		characters = self.getCharacterList()
		for thisChar in characters:
			newEntity = self.createEntity()
			cmds.select(newEntity, r=True)
			cmds.rename(thisChar)
			gchaPath = (self.path + '/' + thisChar + '/golaem/char')
			shaderPath = (self.path + '/' + thisChar + '/golaem/shaders')
			gchaFile = self.findLatestFile(gchaPath, '.gcha')
			gcha = (gchaPath + '/' + gchaFile)
			entityShape = cmds.pickWalk(d='down')
			cmds.setAttr('%s.characterFile' % entityShape[0], gcha, type='string')
			cmds.setAttr('%s.renderFilter' % entityShape[0], 3)
			texture = self.loadTextures(thisChar, shaderPath)
		if cmds.window('createEntities', ex=True):
			cmds.deleteUI('createEntities')
	
	def entitiesUI(self):
		if cmds.window('createEntities', ex=True):
			cmds.deleteUI('createEntities')
		ui = cmds.window('createEntities', rtf=True, wh=(200, 200), t='Golaem Import All Entities')
		form = cmds.formLayout(nd=100)
		load = cmds.button('load', l='Load All Entities', c=partial(self.loadAllEntities))
		cmds.formLayout(form, edit=True, attachForm=((load, 'top', 15), (load, 'left', 15)))
		cmds.showWindow()
		


run = loadAllEntities()
run.entitiesUI()