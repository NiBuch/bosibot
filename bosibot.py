#!/usr/bin/python2
# -*- encoding: utf-8 -*-

import socket
import ssl
import re
import random
import urllib2
import bitly_api
import pywapi
from wikipedia import summary
from config import *
from bosidb import *
from BeautifulSoup import BeautifulSoup
from pyfiglet import Figlet

# ==================
# Initializing Data
# ==================

NAMES = []

if __name__ == '__main__':
    
    # ==================
    # MAIN PROGRAM
    # ==================
    readbuffer = ""

    s=socket.socket( )
    s.connect((HOST, PORT))
    irc = ssl.wrap_socket(s)
    
    irc.send(bytes("PASS %s\r\n" % PASSWORD))
    irc.send(bytes("USER %s %s bla :%s\r\n" % (IDENT, USERHOST, REALNAME)))
    irc.send(bytes("NICK %s\r\n" % NICK))
    
    # Sending Chat
    # =========================
    def irc_send(bold, regular):
        global irc
        irc.send(bytes("PRIVMSG " + CHANNEL + " :\x02%s\x02%s \r\n" % (bold.replace('\n','').replace('\r',''),regular.replace('\n','').replace('\r',''))))

    # Rainbow Send
    # ============
    def col_send(chat):
        global irc
        sendstring = ""
        i = 0
        while (i < len(chat)):
            sendstring += ("\x03")
            sendstring += (str("%02d" % (random.randint(3,13))) + chat[i])
            i += 1
        irc.send(bytes("PRIVMSG " + CHANNEL + " :%s \r\n" % (sendstring)))

    
    # Figlet
    # ========================
    def send_fig(text):
        f = Figlet(font=FIGLETFONT)
        o = f.renderText(text)
        array = []
        for line in o.split('\n'):
            array.append(line)
        for line in array[:len(array) - 1]:
            if line == '':
                pass
            else:
                irc_send(" ", line.encode("ascii", "ignore"))

    # Send Moement
    # ============
    def send_moe(nick,text):
        opening = ['most people don\'t know this but...','you might be surprised to find out that...','did you know that...']
        num = random.randint(0,len(opening) -1)
        if len(text) > 350:
            i = 0
            for x in text[350:]:
                i += 1
                if x == " ":
                    break
            irc_send("", "Hey " + nick + " " + opening[num] + text[:350 + i])
            irc_send("", text[350 + i:])
        else:
            irc_send("", "Hey " + nick + " " + opening[num] + text)
          
    # Cards Against Humanity
    # ======================
    CARDS = []
    def cards_against_humanity(text):
        global CARDS
        if not CARDS:
            CARDS = urllib2.urlopen("http://www.cardsagainsthumanity.com/wcards.txt").read()
            CARDS = CARDS.split("cards=")[1]
            CARDS = re.split("[.?]?<>", CARDS)

        text = text.split()
        for ind,word in enumerate(text):
            if "_" in word:
                card = random.choice(CARDS)
                if (" " in card) and ("™" not in card):
                    card = card.split()
                    if (ind != 0 and card[0][0].isupper() and not card[1][0].isupper()):
                        card[0] = card[0].lower()
                    card = " ".join(card)
                text[ind] = card

        text = " ".join(text)

        while len(text) > 350:
            irc_send("", text[:text.index(" ", 350)])
            text = text[text.index(" ",350):]
        irc_send("", text)



    # Main Loop
    # =========
    while 1:
        try:
            # Retrieve, format, and print stream
            # ==================================
            readbuffer = readbuffer+irc.recv(1024)
            temp = str.split(readbuffer, "\n")
            if (len(temp) == 1) and (temp[0] == ''):
                print "Connection Issue"
                break
            else:
                print temp
                readbuffer = temp.pop( )
                for line in temp:
                    line = str.rstrip(line)
                    line = str.split(line)

                    # Ping Bullshit
                    # =============
                    if(line[0] == "PING"):
                        irc.send(bytes("PONG %s\n" % line[1]))#))

                    # Scrape for the Person Typing
                    # ============================
                    name = line[0].split("!")[0][1:]

                    # Waiting for MOTD to end to send JOIN
                    # ====================================
                    if (name == NICK and line[1] == "MODE"):
                        irc.send(bytes("JOIN %s\r\n" % CHANNEL))
                    if (len(line) > 3):
                        
                        # Build NAMES list
                        # ================
                        if (line[3] == "*" and line[4] == CHANNEL):
                            for nick in line[6:]:
                                if nick[0] in ['@','+']:
                                    NAMES.append(nick[1:])
                                else:
                                    NAMES.append(nick)
                        elif (line[1] in ['QUIT']):
                            NAMES.remove(name)
                        if (line[1] == "PRIVMSG" and line[2] == CHANNEL):

                            # Scrape for the Message
                            # ======================
                            L = line[3:]
                            message = ' '.join(str(x) for x in L)

                            # Detect any SWRX related keywords and warn for using
                            # ===================================================
                            if str.lower(L[0][1:]) in SWRXLIST:
                                irc_send("SWRX Keyword Detected", ": " + "No mention of the sweatshop that is SWRX will be tolerated here.")
                            for word in L[1:]:
                                if str.lower(word) in SWRXLIST:
                                    irc_send("SWRX Keyword Detected", ": " + "No mention of the sweatshop that is SWRX will be tolerated here.")

                            # Maintain SEEN Dictionary
                            # ========================
                            dbAddSeen(name,message[1:])

                            # URL Title Grabber
                            # =================
                            url = re.search("https?://[^\s]+\.[^\s]+", message)
                            if url:
                                try:
                                    page = BeautifulSoup(urllib2.urlopen(url.group(), timeout = 2), convertEntities="html")
                                    if page:
                                        title = str(page.title.string).strip()
                                        if (title and (len(title) < 100)):
                                            irc_send("", title)
                                except:
                                    pass

                            # Cards Against Humanity
                            # ======================
                            elif re.search("(^|\s)_+($|\s)", message):
                                try:
                                    cards_against_humanity(message)
                                except:
                                    pass

                            # ADMINISTRATIVE STUFF
                            # ====================
                            if (line[0] == MASTER and line[3][1] == TRIGGER and (len(line[3]) > 2)):
                                command = line[3][2:]

                                # This kills the bot.
                                # ===================
                                if (command == "die"):
                                    raise SystemExit(0)

                                # @addquote -- Adds a quote to the bot
                                # ====================================
                                elif (command == 'addquote'):
                                    # Make the line received a string
                                    L = line[4:]
                                    temp_str = ' '.join(str(x) for x in L)

                                    # Add the quote to db
                                    dbAddQuote(temp_str)

                                    # Confirm addition of quote
                                    irc_send("Quote Added", ": There are now " + dbGetQuoteCount() + " quotes!")

                            # REGULAR USER ACTIONS
                            # ====================
                            if (line[3][1] == TRIGGER):
                                command = line[3][2:]

                                # @help - Display a list of commands
                                # ==================================
                                if (command == "help"):
                                    irc_send("Commands", ": @quote; @quote (int); @search (string); @stats; @d (int); @figlet (string); @8ball; @bitly (url); @tell (nick); @git; @colsay (string); @seen (nick); @mumble")

                                # @git - Show the github URL
                                # ==========================
                                elif (command == "git"):
                                    irc_send("bosibot on github", ": https://github.com/iabosi/bosibot")

                                # @mumble -Show Mumble Info
                                # =========================
                                elif (command == "mumble"):
                                    irc_send("Server", MUMBLE_SERVER)
                                    irc_send("Password", MUMBLE_PASS)

                                # @moement - Send a moement
                                # =========================
                                elif (command == "moement"):
                                    send_moe(name,dbGetMoment())

                                # @quote - Display a random quote
                                # ===============================
                                elif (command == "quote" and len(line) == 4):
                                    randQuoteRow = dbGetRandomQuote()
                                    irc_send("Quote " + str(randQuoteRow[0]), ": " + randQuoteRow[1])

                                # @quote <int> - Display a specific quote
                                # =======================================
                                elif (command == "quote" and str.isdigit(line[4])):
                                    quotenum = str(abs(int(line[4])))
                                    try:
                                        quote = dbGetQuote(quotenum)
                                        irc_send("Quote " + quotenum, ": " + quote)
                                    except:
                                        irc_send("Quote not found", ": there are " + dbGetQuoteCount() + " quotes.")

                                # @stats - Overall bot statistics
                                # ================================
                                elif (command == 'stats'):
                                    irc_send("Number of Quotes", ": " + dbGetQuoteCount())

                                # @search <phrase> - Search for Quote
                                # ================================
                                elif (command == 'search' and len(line) > 4):
                                    query = ' '.join(str(x) for x in line[4:])
                                    raw_sql = dbSearchQuote(query)
                                    if len(raw_sql) == 0:
                                        irc_send("No matches.","")
                                    else:
                                        if len(raw_sql) == 1:
                                            irc_send("Quote " + str(raw_sql[0][0]), ": " + raw_sql[0][1])
                                        else:
                                            list = []
                                            for x in raw_sql:
                                                list.append(x[0])
                                            quote_idList = ','.join(str(x) for x in list)
                                            irc_send("Matches found", ": " + quote_idList)


                                # @d - Rolling Dice
                                # ===============================
                                elif (command == 'd' and str.isdigit(line[4])):
                                    die = abs(int(line[4]))
                                    if ((die > 1) and (die < 101)):
                                        irc_send(name,": a " + str(random.randint(1,die)) + " shows on the " + str(die) + "-sided die.")

                                # @8ball - 8 Ball Response Generator
                                # ==============================
                                elif (command == '8ball'):
                                    irc_send(name,  ": " + dbGet8ball())

                                # ==============================
                                # Figlet
                                # ======
                                elif (command == 'figlet'):
                                    L = (line[4:])
                                    temp_str = ' '.join(str.upper(x) for x in L)
                                    if (len(temp_str) < 12):
                                        send_fig(temp_str)

                                # @colsay - Generate Rainbow Text
                                # ===============================
                                elif (command == 'colsay'):
                                    L = (line[4:])
                                    temp_str = ' '.join(x for x in L)
                                    if (len(temp_str) < 100):
                                        col_send(temp_str)
                                
                                # @weather <city/zip> - Return weather
                                # ====================================
                                elif (command == 'weather' and len(line) > 4):
                                    yahooweather = pywapi.get_weather_from_yahoo(line[4], 'imperial')
                                    irc_send((yahooweather['condition']['title']).encode("utf-8"), (": " + yahooweather['condition']['temp'] + " degrees F and " + yahooweather['condition']['text']).encode("utf-8"))
                                
                                # @forecast <zip> - Return 4 day forecast
                                # ====================================
                                elif (command == 'forecast' and len(line) > 4):
                                    yahooweather = pywapi.get_weather_from_yahoo(line[4], 'imperial')
                                    [irc_send((x['day']).encode('utf-8') + ' ' + (x['date']).encode('utf-8'), ': ' + (x['high']).encode('utf-8') + 'F/' + (x['low']).encode('utf-8') + 'F - ' + (x['text']).encode('utf-8')) for x in yahooweather['forecasts'][1:]]


                                # @wiki <word> - Return wiki summary for term
                                # ===========================================
                                elif (command == 'wiki') and (len(line) > 4):
                                    L = (line[4:])
                                    temp_str = ' '.join(str.upper(x) for x in L)
                                    if (len(temp_str) < 12):
                                        try:
                                            wiki = (summary(temp_str, sentences=1)).encode('utf-8')
                                            irc_send(name, ": " + str(wiki))
                                        except:
                                            irc_send(name, ": Error retrieving wiki.")

                                # @bitly - URL Shortener
                                # ======================
                                elif (command == 'bitly' and len(line) > 4):
                                    url = re.search("https?://[^\s]+", line[4]).group()
                                    try:
                                        page = BeautifulSoup(urllib2.urlopen(url, timeout = 2), convertEntities="html")
                                        if page:
                                            title = str(page.title.string).strip()
                                            if (title and (len(title) < 100)):
                                                b = bitly_api.Connection(BAPI_USER, BAPI_KEY)
                                                short = str(b.shorten(url)['url'])
                                                irc_send(short, " " + title)
                                    except:
                                        try:
                                            b = bitly_api.Connection(BAPI_USER, BAPI_KEY)
                                            short = str(b.shorten(url)['url'])
                                            irc_send(short, "")
                                        except:
                                            irc_send(name,": There was a problem creating your bitly URL.")

                                # @tell - Leave a message for someone
                                # ===================================
                                elif (command == 'tell' and len(line) > 4):
                                    nick = line[4]
                                    if nick in NAMES:
                                        irc_send(nick, " is in the channel right now, tell them yourself!")
                                    else:
                                        raw_sql = dbGetTell(nick)
                                        if len(raw_sql) > 4:
                                            irc_send(name,": Mailbox for " + nick + " is full.")
                                        else:
                                            L = (line[5:])
                                            temp_str = ' '.join(x for x in L)
                                            dbAddTell(nick, name, temp_str)
                                            irc_send(name, ": I've saved your message for " + nick)

                                # @seen - Show last message for a user
                                # ====================================
                                elif (command == 'seen' and len(line) > 4):
                                    nick = line[4]
                                    raw_sql = dbGetSeen(nick)
                                    if (nick == NICK):
                                        irc_send(nick, ": was last seen in your mom.")
                                    elif raw_sql:
                                        irc_send(nick, ": was last seen in " + CHANNEL + " on " + raw_sql[1] + " - " + "<" + nick + "> " + raw_sql[0])
                                    else:
                                        irc_send(nick, ": has not been seen in " + CHANNEL + ".")
                                    
                    # Maintain NAMES list and tell
                    # ============================
                    elif (line[1] == "PART"):
                        NAMES.remove(name)
                    elif (line[1] == "JOIN"):
                        NAMES.append(name)
                        if name == "MF":
                            send_moe(name,dbGetMoment())
                        for row in dbGetTell(name):
                            irc_send(name, ": Message from " + row[0] + " left on " + row[2] + " - " + row[1])
                        dbCleanTell(name)
                    elif (line[1] == "NICK"):
                        NAMES.remove(name)
                        newNick = line[2][1:]
                        NAMES.append(newNick)
                        for row in dbGetTell(newNick):
                            irc_send(name, ": Message from " + row[0] + " left on " + row[2] + " - " + row[1])
                        dbCleanTell(newNick)

        except UnicodeDecodeError:
            print("UnicodeError")
        except Exception as ex:
            template = "An exception of type {0} occured. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print message
