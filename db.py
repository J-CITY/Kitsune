from tag_controller import *
import sqlite3
import os

class Database:
	def __init__(self):
		self.PATH = 'E:\\music'
		self.dbName = 'lib.db'
		self.tableName = 'medialib'
		self.create()
		
	def walk(self):
		for top, dirs, files in os.walk(self.PATH):
			for nm in files:
				#print(os.path.join(top, nm))
				file = os.path.join(top, nm)
				filename, file_extension = os.path.splitext(file)
				if file_extension.lower() in ['.wav', '.flac', '.mp3']:
					res = getTagFromPath(file)
					if res != None:
						self.insert(res)
	
	def create(self):
		self.conn = sqlite3.connect(self.dbName)
		self.cursor = self.conn.cursor()

		self.cursor.execute("""CREATE TABLE IF NOT EXISTS """ + self.tableName + """ 
		(artist TEXT,
		album TEXT,
		song TEXT,
		url TEXT NOT NULL,
		year TEXT,
		genre TEXT,
		coverart TEXT)
		""")
		
	def insert(self, tag):
		#print(tag.url)
		self.cursor.execute("""INSERT INTO """+self.tableName+"""
			VALUES (?,?,?,?,?,?,?)""", 
			(tag.artist,
			tag.album,
			tag.song,
			tag.url,
			str(tag.year),
			tag.genre,
			tag.coverart))
		self.conn.commit()

	def insertByPath(self, path):
		tag = getTagFromPath(path)
		self.cursor.execute("""INSERT INTO """+self.tableName+"""
			VALUES (?,?,?,?,?,?,?)""", 
			(tag.artist,
			tag.album,
			tag.song,
			tag.url,
			str(tag.year),
			tag.genre,
			tag.coverart))
		self.conn.commit()
		
		
	def insertMany(self, data):
		self.cursor.executemany("INSERT INTO albums VALUES (?,?,?,?,?,?,?)", data)
		self.conn.commit()
	
	def selectDistinct(self, col):
		self.cursor.execute("SELECT DISTINCT " + col + " FROM " + self.tableName)
		
		return self.cursor.fetchall()

	def select(self, e):
		self.cursor.execute(e)
		return self.cursor.fetchall()

	def execute(self, text, params=()):
		self.cursor.execute(text, params)
		return self.cursor.fetchall()

	def search(self, text):
		self.cursor.execute("SELECT * FROM "+self.tableName+
			" WHERE artist LIKE ? OR album LIKE ? OR song LIKE ? OR genre LIKE ?",
			(text, text, text, text))
		return self.cursor.fetchall()