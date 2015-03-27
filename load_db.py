#!/usr/bin/python2

#CREATE TABLE quotes
#(quote text, datetm text);

#CREATE TABLE seen
#(nick text, message text, datetm text);

#CREATE TABLE ball
#(message text);

import sqlite3

conn = sqlite3.connect('bosibot.db')
conn.text_factory = str
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS moments (moment text);")

BALL = []

def read_ball():

    f = open('facts.txt', 'r')
    for x in f.readlines():
        line = x.split('\n')
        BALL.append(line[0])

# QUOTES is list of {"quote": str, "added_on": str, "added_by": str, "times_quoted": str} Wed Feb  4 20:50:01 2015

read_ball()

for ball in BALL:
    c.execute("INSERT INTO moments (moment) VALUES (?);", (ball,))
    print "added quote " + ball

conn.commit()
conn.close()
