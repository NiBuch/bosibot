#!/usr/bin/python2
# -*- encoding: utf-8 -*-

import sqlite3
import time

conn = sqlite3.connect('babbygrill.db')
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS quotes (quote text, datetm text);")
c.execute("CREATE TABLE IF NOT EXISTS seen (nick text, message text, datetm text);")
c.execute("CREATE TABLE IF NOT EXISTS tell (tonick text, fromnick text, message text, datetm text);")
c.execute("CREATE TABLE IF NOT EXISTS moments (moment text);")
c.execute("CREATE TABLE IF NOT EXISTS ball (message text);")

def dbAddTell(tonick, fromnick, message):
    time_string = time.strftime("%c")
    c.execute("INSERT INTO tell (tonick, fromnick, message, datetm) VALUES (?, ?, ? , ?);", (tonick, fromnick, message, time_string))
    conn.commit()

def dbGetTell(nick):
    c.execute("SELECT fromnick, message, datetm FROM tell WHERE tonick = ?;", (nick,))
    tells = [x.encode("utf-8") for x in c.fetchall()]
    return tells

def dbCleanTell(nick):
    c.execute("DELETE FROM tell WHERE tonick = ?;", (nick,))
    conn.commit()

def dbAddSeen(nick, message):
    time_string = time.strftime("%c")
    c.execute("DELETE FROM seen WHERE nick = ?;", (nick,))
    c.execute("INSERT INTO seen (nick, message, datetm) VALUES (?,?,?);", (nick, message, time_string))
    conn.commit()

def dbGetSeen(nick):
    c.execute("SELECT message, datetm FROM seen WHERE nick = ?;", (nick,))
    select = c.fetchone()
    if select:
        message,datetm = select
        return message.encode("utf-8"),datetm.encode("utf-8")

def dbAddQuote(text):
    time_string = time.strftime("%c")
    c.execute("INSERT INTO quotes (quote, datetm) VALUES (?, ?);", (text, time_string))
    conn.commit()

def dbGetQuoteCount():
    c.execute("SELECT COUNT(*) FROM quotes;")
    return str(c.fetchone()[0])

def dbGetRandomQuote():
    c.execute("SELECT id, quote FROM quotes ORDER BY RANDOM() LIMIT 1;")
    id,quote = c.fetchone()
    return id,quote.encode("utf-8")

def dbGetQuote(id):
    c.execute("SELECT quote FROM quotes WHERE id = ?;", (id,))
    quote = c.fetchone()[0]
    return quote.encode("utf-8")

def dbSearchQuote(searchString):
    c.execute("SELECT id, quote FROM quotes WHERE LOWER(quote) LIKE ?;", (('%'+str.lower(searchString)+'%'),));
    output = []
    raw = c.fetchall()
    for x in raw:
        temp = []
        temp.append(x[0])
        temp.append(x[1].encode("utf-8"))
        output.append(temp)
    return output

def dbGet8ball():
    c.execute("SELECT message FROM ball ORDER BY RANDOM() LIMIT 1;")
    return str(c.fetchone()[0]).encode("utf-8")

def dbGetMoment():
    c.execute("SELECT moment FROM moments ORDER BY RANDOM() LIMIT 1;")
    return str(c.fetchone()[0])
