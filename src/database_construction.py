import sqlite3
import pandas as pd

def construct_db(name):
    conn=sqlite3.connect(name)
    cur=conn.cursor()

    # Create Series data table

    series = """ CREATE TABLE series (
                series_id VARCHAR(100) PRIMARY KEY,
                title VARCHAR(500),
                organism VARCHAR(200),
                experiment VARCHAR(200),
                summary VARCHAR(8000),
                design VARCHAR(2000),
                submission_date TEXT,
                last_update_date TEXT,
                contact_name VARCHAR(50),
                organization_name VARCHAR(500),
                department VARCHAR(200),
                address VARCHAR(500),
                city VARCHAR(100),
                zip INT,
                country VARCHAR(200)
            ); """

    publication_series= """ CREATE TABLE publication_series (
                series_id VARCHAR(100) NOT NULL,
                pmid INT NOT NULL,
                PRIMARY KEY (series_id, pmid),
                foreign key (series_id) references series(series_id),
                foreign key (pmid) references publication(pmid)
            ); """


    #Construct Author Table
    author = """ CREATE TABLE author (
                author_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name VARCHAR(50),
                last_name  VARCHAR(50),
                email VARCHAR(50),
                author_kw VARCHAR(500)
            ); """

    #Construct Linking Table for author and affiliation
    author_affiliation = """ CREATE TABLE author_affiliation (
                author_id INT NOT NULL,
                affil_id INT NOT NULL,
                PRIMARY KEY (author_id, affil_id),
                foreign key (author_id) references author(author_id),
                foreign key (affil_id) references affiliation(affil_id)
            ); """

    #Construct Affiliation Table
    affiliation = """ CREATE TABLE affiliation (
                affil_id INTEGER PRIMARY KEY AUTOINCREMENT,
                affil_name VARCHAR(1000)
            ); """

    #Construct publication Table
    publication = """ CREATE TABLE publication (
                pmid INTEGER PRIMARY KEY NOT NULL,
                pub_title VARCHAR(500),
                pub_date TEXT,
                journal_title VARCHAR(500)
            ); """

    #Construct linking table for author and publication table
    author_publication= """ CREATE TABLE author_publication (
                author_id INT NOT NULL,
                pmid INT NOT NULL,
                contact INT NOT NULL,
                PRIMARY KEY (author_id, pmid),
                foreign key (author_id) references author(author_id),
                foreign key (pmid) references publication(pmid)
            ); """
    
    #Construct linking table for author and series table
    author_series= """ CREATE TABLE author_series (
                author_id INT NOT NULL,
                series_id VARCHAR(100) NOT NULL,
                contact INT NOT NULL,
                PRIMARY KEY (author_id, series_id),
                foreign key (author_id) references author(author_id),
                foreign key (series_id) references series(series_id)
            ); """

    #Execute table creation
    cur.execute("DROP TABLE IF EXISTS series")
    cur.execute(series)
    cur.execute("DROP TABLE IF EXISTS publication_series")
    cur.execute(publication_series)
    cur.execute("DROP TABLE IF EXISTS publication")
    cur.execute(publication)
    cur.execute("DROP TABLE IF EXISTS author_publication")
    cur.execute(author_publication)
    cur.execute("DROP TABLE IF EXISTS author")
    cur.execute(author)
    cur.execute("DROP TABLE IF EXISTS author_affiliation")
    cur.execute(author_affiliation)
    cur.execute("DROP TABLE IF EXISTS affiliation")
    cur.execute(affiliation)
    cur.execute("DROP TABLE IF EXISTS author_series")
    cur.execute(author_series)


    conn.commit()
    cur.close()
    conn.close()


construct_db("sample.db")