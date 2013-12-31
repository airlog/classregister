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
	
	CREATE_TABLE_NIEOBECNOSCI = """CREATE TABLE IF NOT EXISTS Nieobecnosci (
		id INT AUTO_INCREMENT,
		uczenId INT,
		data DATE,
		lekcjaId INT,
		
		PRIMARY KEY (id),
		FOREIGN KEY (uczenId) REFERENCES Uczniowie(id),
		FOREIGN KEY (lekcjaId) REFERENCES Lekcje(id)
	) collate utf8_general_ci;
	"""
	
	CREATE_TABLE_WYDARZENIA = """CREATE TABLE IF NOT EXISTS Wydarzenia (
		id INT AUTO_INCREMENT,
		data DATE,
		lekcjaId INT,
		tresc VARCHAR(1024),
				
		PRIMARY KEY (id),
		FOREIGN KEY (lekcjaId) REFERENCES Lekcje(id)
	) collate utf8_general_ci;
	"""
	
	def __init__(self, host, user, password, database, charset = "utf8"):
		MysqlConnection.__init__(self, host, database, user, password, chset = charset)
		
		self.__create_tables()
    
	def __create_tables(self):
		self.execute(DatabaseManager.CREATE_TABLE_LOGINY)
		self.execute(DatabaseManager.CREATE_TABLE_NAUCZYCIELE)
		self.execute(DatabaseManager.CREATE_TABLE_KLASY)
		self.execute(DatabaseManager.CREATE_TABLE_UCZNIOWIE)
		self.execute(DatabaseManager.CREATE_TABLE_PRZEDMIOTY)
		self.execute(DatabaseManager.CREATE_TABLE_LEKCJE)
		self.execute(DatabaseManager.CREATE_TABLE_OCENY)
		self.execute(DatabaseManager.CREATE_TABLE_NIEOBECNOSCI)
		self.execute(DatabaseManager.CREATE_TABLE_WYDARZENIA)
				
	### dla kazdego:

	def get_type(self, login):
		query = """
			SELECT typ FROM Loginy
			WHERE login = "{}"
		""".format(login)
		result = self.query(query)
		if (result is not None and len(result)>0):
			return result[0]["typ"]
		raise ValueError("Dla uzytkownika {} nie znaleziono typu".format(login))
		
	def get_password(self, login, type):
		if type == "UCZEN":
			query = """SELECT Uczniowie.id AS uid, Loginy.haslo 
			FROM Loginy INNER JOIN Uczniowie ON Uczniowie.pesel = Loginy.login 
			WHERE Loginy.login = {} AND Loginy.typ = "{}"
			""".format(login,type)
		elif type == "NAUCZYCIEL":
			query = """SELECT Nauczyciele.id AS uid, Loginy.haslo 
			FROM Loginy INNER JOIN Nauczyciele ON Nauczyciele.pesel = Loginy.login 
			WHERE Loginy.login = {} AND Loginy.typ = "{}"
			""".format(login,type)
		else:
			raise ValueError("Typ {} nie istnieje".format(type))		

		result = self.query(query)
		if result is not None and len(result)>0:
			return result[0]
		raise ValueError("Uzytkownik nie istnieje ({}, {})".format(login, type))
		
	### dla ucznia:
	
	def get_user_schedule(self, userId):
		schedule = """
			SELECT Lekcje.dzien, Lekcje.numerLekcji, Przedmioty.nazwa, Przedmioty.id, Lekcje.sala, Nauczyciele.imie, Nauczyciele.nazwisko
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
			SELECT OcenyUcznia.data, OcenyUcznia.ocena, Przedmioty.nazwa, Przedmioty.id, Nauczyciele.imie, Nauczyciele.nazwisko, OcenyUcznia.opis
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
  
  	def get_user_events(self, userId):
  		query = """
			SELECT Wydarzenia.data, Lekcje.dzien, Lekcje.numerLekcji, Przedmioty.nazwa, Przedmioty.id, Nauczyciele.imie, Nauczyciele.nazwisko, Wydarzenia.tresc
			FROM Wydarzenia
			INNER JOIN Lekcje ON Wydarzenia.lekcjaId = Lekcje.id
			INNER JOIN Przedmioty ON Lekcje.przedmiotId = Przedmioty.id
			INNER JOIN Nauczyciele ON Przedmioty.nauczycielId = Nauczyciele.id
			WHERE Przedmioty.klasaId = (SELECT klasaId FROM Uczniowie WHERE id = {})
			ORDER BY Wydarzenia.data DESC, Lekcje.dzien, Lekcje.numerLekcji
			""".format(userId)
		result = self.query(query)
  		if result is not None:
			return result
		return []
	
	def get_user_absence(self, userId):
		query = """
			SELECT Nieobecnosci.data, Lekcje.dzien, Lekcje.numerLekcji, Przedmioty.id, Przedmioty.nazwa
			FROM Nieobecnosci 
			INNER JOIN Lekcje ON Nieobecnosci.lekcjaId = Lekcje.id
			INNER JOIN Przedmioty ON Lekcje.przedmiotId = Przedmioty.id
			WHERE UczenId = {}
			ORDER BY Nieobecnosci.data DESC, Lekcje.dzien DESC, Lekcje.numerLekcji
			""".format(userId)
		result = self.query(query)
  		if result is not None:
			return result
		return []		
		
	# dla nauczyciela:
	
	def get_teacher_schedule(self, teacherId):
		schedule = """
			SELECT Lekcje.dzien, Lekcje.numerLekcji, Przedmioty.id, Klasy.nazwa, Przedmioty.nazwa AS przedmiot, Lekcje.sala
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
			SELECT Klasy.nazwa, Przedmioty.nazwa, Przedmioty.id, Uczniowie.imie, Uczniowie.nazwisko, Uczniowie.id
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
	
	def get_teacher_pupil_grades(self, pupilId, courseId):
		query = """
			SELECT Uczniowie.id, Uczniowie.imie, Uczniowie.nazwisko, Przedmioty.id, Przedmioty.nazwa, Oceny.data, Oceny.ocena, Oceny.opis
			FROM Oceny
			INNER JOIN Uczniowie ON Oceny.uczenId = Uczniowie.id
			INNER JOIN Przedmioty ON Oceny.przedmiotId = Przedmioty.id
			WHERE przedmiotId = {} AND uczenId = {}
			ORDER BY data DESC
		""".format(courseId, pupilId)
		
		result = self.query(query)
		if result is not None:
			return result
		return []
	
	def get_teacher_events(self, teacherId, courseId = None):
		query = """
			SELECT Wydarzenia.data, Lekcje.dzien, Lekcje.numerLekcji, Przedmioty.nazwa AS przedmiot, Przedmioty.id, Klasy.nazwa, Wydarzenia.tresc
			FROM Wydarzenia
			INNER JOIN Lekcje ON Wydarzenia.lekcjaId = Lekcje.id
			INNER JOIN Przedmioty ON Lekcje.przedmiotId = Przedmioty.id
			INNER JOIN Klasy ON Przedmioty.klasaId = Klasy.id
			WHERE Przedmioty.nauczycielId = {}
		""".format(teacherId)

		if courseId != None:
			query += "AND Przedmioty.id = {}\n".format(courseId)
		query += "ORDER BY Wydarzenia.data DESC"
		
		result = self.query(query)
		if result is not None:
			return result
		return []
