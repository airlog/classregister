# coding=utf-8

import externals
from torndb import Connection as MysqlConnection

class DatabaseManager(MysqlConnection):
    
	CREATE_TABLE_UCZNIOWIE = """CREATE TABLE IF NOT EXISTS Uczniowie (
		id INT AUTO_INCREMENT,
		imie VARCHAR(32),
		nazwisko VARCHAR(32),
		pesel VARCHAR(16) UNIQUE,
		klasaId INT,
		dataUrodzenia DATE,
		adres VARCHAR(128),
		telefon VARCHAR(16),
		imieRodzica1 VARCHAR(32),
		nazwiskoRodzica1 VARCHAR(32),
		imieRodzica2 VARCHAR(32),
		nazwiskoRodzica2 VARCHAR(32),
		
		PRIMARY KEY (id),
		FOREIGN KEY (klasaId) REFERENCES Klasy(id)
	) collate utf8_general_ci;
	"""
	
	CREATE_TABLE_KLASY = """CREATE TABLE IF NOT EXISTS Klasy (
		id INT AUTO_INCREMENT,
		nazwa VARCHAR(64),
		wychowawcaId INT,
		
		PRIMARY KEY (id),
		FOREIGN KEY (wychowawcaId) REFERENCES Nauczyciele(id)
	) collate utf8_general_ci;
	"""
	
	CREATE_TABLE_NAUCZYCIELE = """CREATE TABLE IF NOT EXISTS Nauczyciele (
		id INT AUTO_INCREMENT,
		imie VARCHAR(32),
		nazwisko VARCHAR(32),
		pesel VARCHAR(16) UNIQUE,
		dataUrodzenia DATE,
		dataZatrudnienia DATE,
		adres VARCHAR(128),
		telefon VARCHAR(16),
		
		PRIMARY KEY (id)
	) collate utf8_general_ci;
	"""
	
	CREATE_TABLE_PRZEDMIOTY = """CREATE TABLE IF NOT EXISTS Przedmioty (
		id INT AUTO_INCREMENT,
		nazwa VARCHAR(32),
		nauczycielId INT,
		klasaId INT,
		
		PRIMARY KEY (id),
		FOREIGN KEY (nauczycielId) REFERENCES Nauczyciele(id),
		FOREIGN KEY (klasaId) REFERENCES Klasy(id)
	) collate utf8_general_ci;
	"""
	
	CREATE_TABLE_LEKCJE = """CREATE TABLE IF NOT EXISTS Lekcje (
		id INT AUTO_INCREMENT,
		przedmiotId INT,
		sala VARCHAR(32),
		dzien INT,
		numerLekcji INT,
		
		PRIMARY KEY (id),
		FOREIGN KEY (przedmiotId) REFERENCES Przedmioty(id)
	) collate utf8_general_ci;
	"""
	
	CREATE_TABLE_OCENY = """CREATE TABLE IF NOT EXISTS Oceny (
		id INT AUTO_INCREMENT,
		uczenId INT,
		przedmiotId INT,
		ocena INT,
		data DATE,
		opis VARCHAR(256),
		
		PRIMARY KEY (id),
		FOREIGN KEY (uczenId) REFERENCES Uczniowie(id),
		FOREIGN KEY (przedmiotId) REFERENCES Przedmioty(id)
	) collate utf8_general_ci;
	"""
	
	CREATE_TABLE_LOGINY = """CREATE TABLE IF NOT EXISTS Loginy (
		id INT AUTO_INCREMENT,
		login VARCHAR(16),
		haslo VARCHAR(64),
		typ ENUM("UCZEN", "NAUCZYCIEL"),
		
		PRIMARY KEY (id)
	) collate utf8_general_ci;
	"""
	
	def __init__(self, host, user, password, database):
		MysqlConnection.__init__(self, host, database, user, password)
		
		self.__create_tables()
    
	def __create_tables(self):
		self.execute(DatabaseManager.CREATE_TABLE_LOGINY)
		self.execute(DatabaseManager.CREATE_TABLE_NAUCZYCIELE)
		self.execute(DatabaseManager.CREATE_TABLE_KLASY)
		self.execute(DatabaseManager.CREATE_TABLE_UCZNIOWIE)
		self.execute(DatabaseManager.CREATE_TABLE_PRZEDMIOTY)
		self.execute(DatabaseManager.CREATE_TABLE_LEKCJE)
		self.execute(DatabaseManager.CREATE_TABLE_OCENY)

	### dla kazdego:

	def get_password(self, login, type):
		query = """SELECT haslo FROM Loginy WHERE login = {} AND typ = "{}"""".format(login,type)
		result = self.query(query)
		if (result is not None and len(result)>0):
			return result[0][haslo]
		raise ValueError("Uzytkownik nie istnieje ({}, {})".format(login, type))
		
	### dla ucznia:
	
	def get_user_schedule(self, userId):
		schedule = """
			SELECT Lekcje.dzien, Lekcje.numerLekcji, Przedmioty.nazwa, Lekcje.sala, Nauczyciele.imie, Nauczyciele.nazwisko
			FROM Przedmioty
			INNER JOIN Lekcje ON Przedmioty.id = Lekcje.przedmiotId
			INNER JOIN Nauczyciele ON Przedmioty.nauczycielId = Nauczyciele.id
			WHERE klasaId = (SELECT klasaId FROM Uczniowie WHERE id = {})
			ORDER BY Lekcje.dzien, Lekcje.numerLekcji
			""".format(userId)
		result = self.query(schedule)
		if result is not None:
			return result
		return []
 
	def get_user_grades(self, userId, courseId = None): 		
		query = """
			SELECT OcenyUcznia.data, OcenyUcznia.ocena, Przedmioty.nazwa, Nauczyciele.imie, Nauczyciele.nazwisko, OcenyUcznia.opis
			FROM (SELECT * FROM Oceny WHERE uczenId = {}) AS OcenyUcznia
			INNER JOIN Przedmioty ON OcenyUcznia.przedmiotId = Przedmioty.id
			INNER JOIN Nauczyciele ON Przedmioty.nauczycielId = Nauczyciele.id
			""".format(userId)
 		
		if courseId is not None:
			query += "WHERE OcenyUcznia.przedmiotId = {}".format(courseId) 			
		query += "\nORDER BY OcenyUcznia.data"
		
		result = self.query(query)
		if result is not None:
			return result
		return []
  
	# dla nauczyciela:
	
	def get_teacher_schedule(self, teacherId):
		schedule = """
			SELECT Lekcje.dzien, Lekcje.numerLekcji, Klasy.nazwa, Przedmioty.nazwa, Lekcje.sala
			FROM Przedmioty
			INNER JOIN Lekcje ON Przedmioty.id = Lekcje.przedmiotId
			INNER JOIN Klasy ON Przedmioty.klasaId = Klasy.id
			WHERE nauczycielId = {}
			ORDER BY Lekcje.dzien, Lekcje.numerLekcji
			""".format(teacherId)
		result = self.query(schedule)
		if result is not None:
			return result
		return []
	
	def get_teacher_pupils(self, teacherId, courseId = None):
		query = """
			SELECT Klasy.nazwa, Przedmioty.nazwa, Uczniowie.imie, Uczniowie.nazwisko
			FROM Przedmioty
			INNER JOIN Klasy ON Przedmioty.klasaId = Klasy.id
			INNER JOIN Uczniowie ON Klasy.id = Uczniowie.klasaId
			WHERE Przedmioty.nauczycielId = {}
		""".format(teacherId)
		
		if courseId is not None:
			query += "\nAND Przedmioty.przedmiotId = {}".format(courseId) 			
		query += "\nORDER BY Klasy.nazwa, Uczniowie.nazwisko, Uczniowie.imie"
		
		result = self.query(query)
		if result is not None:
			return result
		return []
