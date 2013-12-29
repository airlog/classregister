# coding=utf-8

import externals
from torndb import Connection as MysqlConnection

class DatabaseManager(MysqlConnection):
    
	CREATE_TABLE_UCZNIOWIE = """CREATE TABLE IF NOT EXISTS Uczniowie (
		id INT,
		imie VARCHAR(32),
		nazwisko VARCHAR(32),
		pesel VARCHAR(16),
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
	);
	"""
	CREATE_TABLE_KLASY = """CREATE TABLE IF NOT EXISTS Klasy (
		id INT,
		nazwa VARCHAR(64),
		wychowawcaId INT,
		
		PRIMARY KEY (id),
		FOREIGN KEY (wychowawcaId) REFERENCES Nauczyciele(id)
	);
	"""
	CREATE_TABLE_NAUCZYCIELE = """CREATE TABLE IF NOT EXISTS Nauczyciele (
		id INT,
		imie VARCHAR(32),
		nazwisko VARCHAR(32),
		pesel VARCHAR(16),
		dataUrodzenia DATE,
		dataZatrudnienia DATE,
		adres VARCHAR(128),
		telefon VARCHAR(16),
		
		PRIMARY KEY (id)
	);
	"""
	CREATE_TABLE_PRZEDMIOTY = """CREATE TABLE IF NOT EXISTS Przedmioty (
		id INT,
		nazwa VARCHAR(32),
		nauczycielId INT,
		klasaId INT,
		
		PRIMARY KEY (id),
		FOREIGN KEY (nauczycielId) REFERENCES Nauczyciele(id),
		FOREIGN KEY (klasaId) REFERENCES Klasy(id)
	);
	"""
	CREATE_TABLE_LEKCJE = """CREATE TABLE IF NOT EXISTS Lekcje (
		id INT,
		przedmiotId INT,
		sala VARCHAR(32),
		dzien INT,
		numerLekcji INT,
		
		PRIMARY KEY (id),
		FOREIGN KEY (przedmiotId) REFERENCES Przedmioty(id)
	);
	"""

	CREATE_TABLE_OCENY = """CREATE TABLE IF NOT EXISTS Oceny (
		id INT,
		uczenId INT,
		przedmiotId INT,
		ocena INT,
		data DATE,
		opis VARCHAR(256),
		
		PRIMARY KEY (id),
		FOREIGN KEY (uczenId) REFERENCES Uczniowie(id),
		FOREIGN KEY (przedmiotId) REFERENCES Przedmioty(id)
	);
	"""
	
	def __init__(self, host, user, password, database):
		print("{}\n{}\n{}\n{}\n".format(host, user, password, database))
		MysqlConnection.__init__(self, host, database, user, password)
		
		self.__create_tables()
    
	def __create_tables(self):
	
		self.execute(DatabaseManager.CREATE_TABLE_NAUCZYCIELE)
		self.execute(DatabaseManager.CREATE_TABLE_KLASY)
		self.execute(DatabaseManager.CREATE_TABLE_UCZNIOWIE)
		self.execute(DatabaseManager.CREATE_TABLE_PRZEDMIOTY)
		self.execute(DatabaseManager.CREATE_TABLE_LEKCJE)
		self.execute(DatabaseManager.CREATE_TABLE_OCENY)

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
 		
		if course is not None:
			query += "WHERE OcenyUcznia.przedmiotId = {}".format(courseId) 			
		query += "\nORDER BY OcenyUcznia.data"
		
		result = self.query(query)
		if result is not None:
			return result
		return []
 
