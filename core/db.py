import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

from core.tag_controller import *
from core.strings import SONG_FORMATS
import sqlite3
import os

class Database:
	def __init__(self, musicPath):
		self.PATH = musicPath
		self.dbPath = 'assets/lib.db'
		self.tableName = 'medialib'
		self.create()

	def walk(self):
		for top, dirs, files in os.walk(self.PATH):
			for nm in files:
				#print(os.path.join(top, nm))
				file = os.path.join(top, nm)
				filename, file_extension = os.path.splitext(file)
				if file_extension.lower() in SONG_FORMATS:
					res = getTagFromPath(file)
					if res != None:
						self.insert(res)

	def create(self):
		self.conn = sqlite3.connect(self.dbPath, check_same_thread=False)
		#self.cursor = self.conn.cursor()
		cursor = self.conn.cursor()
		cursor.execute("""CREATE TABLE IF NOT EXISTS """ + self.tableName + """ 
		(artist TEXT,
		album TEXT,
		song TEXT,
		url TEXT NOT NULL,
		year TEXT,
		genre TEXT,
		coverart TEXT)
		""")
		cursor.close()

	def close(self):
		self.conn.close()
		#self.cursor.close()

	def open(self):
		self.conn = sqlite3.connect(self.dbPath)
		#self.cursor.close()

	def insert(self, tag):
		cursor = self.conn.cursor()
		#print(tag.url)
		artists = tag.artist.split(",")
		for artist in artists:
			cursor.execute("""INSERT INTO """+self.tableName+"""
				VALUES (?,?,?,?,?,?,?)""", 
				(artist,
				tag.album,
				tag.song,
				tag.url,
				str(tag.year),
				tag.genre,
				tag.coverart))
		self.conn.commit()
		cursor.close()

	def insertByPath(self, path):
		tag = getTagFromPath(path)
		if tag is None:
			log(LogLevel.ERROR, "cant get tag", path)
			return
		cursor = self.conn.cursor()
		cursor.execute("""INSERT INTO """+self.tableName+"""
			VALUES (?,?,?,?,?,?,?)""", 
			(tag.artist,
			tag.album,
			tag.song,
			tag.url,
			str(tag.year),
			tag.genre,
			tag.coverart))
		self.conn.commit()
		cursor.close()

	def insertMany(self, data):
		cursor = self.conn.cursor()
		cursor.executemany("INSERT INTO albums VALUES (?,?,?,?,?,?,?)", data)
		self.conn.commit()
		cursor.close()

	def selectDistinct(self, col):
		cursor = self.conn.cursor()
		cursor.execute("SELECT DISTINCT " + col + " FROM " + self.tableName)
		res = cursor.fetchall()
		cursor.close()
		return res

	def select(self, e):
		cursor = self.conn.cursor()
		cursor.execute(e)
		res = cursor.fetchall()
		cursor.close()
		return res

	def execute(self, text, params=()):
		cursor = self.conn.cursor()
		cursor.execute(text, params)
		res = cursor.fetchall()
		cursor.close()
		return res

	def search(self, text):
		cursor = self.conn.cursor()
		cursor.execute("SELECT * FROM "+self.tableName+
			" WHERE artist LIKE ? OR album LIKE ? OR song LIKE ? OR genre LIKE ?",
			(text, text, text, text))
		res = cursor.fetchall()
		cursor.close()
		return res

	def searchArtist(self, text):
		cursor = self.conn.cursor()
		cursor.execute("SELECT * FROM " + self.tableName + " WHERE artist LIKE ?", (text))
		res = cursor.fetchall()
		cursor.close()
		return res

	def searchAlbum(self, text):
		cursor = self.conn.cursor()
		cursor.execute("SELECT * FROM " + self.tableName + " WHERE album LIKE ?", (text))
		res = cursor.fetchall()
		cursor.close()
		return res

	def searchTrack(self, text):
		cursor = self.conn.cursor()
		cursor.execute("SELECT * FROM " + self.tableName + " WHERE song LIKE ?", (text))
		res = cursor.fetchall()
		cursor.close()
		return res
