# Retro Winnipeg Weather Channel
# By probnot





from tkinter import *
import time
import datetime
# from datetime import datetime
import asyncio # for env_canada
import textwrap # used to format forecast text
from env_canada import ECWeather
import feedparser # for RSS feed
import requests # for RSS feed
import json # for RSS feed
import pygame # for background music
import random # for background music
import os # for background music
import re # for word shortener

prog = "wpg-weather."
ver = "2.0.4"
# 2.0.4 [2023-06-06]
# - Line 89 humidex typo
# - Line 203 fixed high/low yesterday temp - added check for nonetype
# 2.0.3
# - Updated channel listings
# 2.0.1
# - Changed forecast time to use current time when updating weather - the date and time from forecast_time in env_canada returns odd results
# - Changed UV INDEX to show -- instead of blank if no index is present

# DEF clock Updater
def clock():

    current = time.strftime("%I %M %S").rjust(8, " ")
    timeText.configure(text=current)
    root.after(1000, clock) # run every 1sec
    
# DEF main weather pages 
def weather_page(PageColour, PageNum):

    # pull in current seconds and minutes -- to be used to cycle the middle section every 30sec
    
    time_sec = time.localtime().tm_sec
    time_min = time.localtime().tm_min
    
    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    months = [" ", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]    
    linebreak = ['\n']

    PageTotal = 8

    if (PageNum == 1):
        
        # ===================== Screen 1 =====================
        # Today's day/date + specific weather conditions
        #print(time.strftime("%H:%M.") + prog + ver + ".WEATHER_PAGE-display page " + str(PageNum))            
        
        # get local timezone to show on screen
        local_tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
        
        # weather data
        temp_cur = str(ec_en_wpg.conditions["temperature"]["value"])
        temp_high = str(ec_en_wpg.conditions["high_temp"]["value"])
        temp_low = str(ec_en_wpg.conditions["low_temp"]["value"])
        humidity = str(ec_en_wpg.conditions["humidity"]["value"])
        condition = ec_en_wpg.conditions["condition"]["value"]
        pressure = str(ec_en_wpg.conditions["pressure"]["value"])   
        tendency = ec_en_wpg.conditions["tendency"]["value"]
        dewpoint = str(ec_en_wpg.conditions["dewpoint"]["value"])
        uv_index = str(ec_en_wpg.conditions["uv_index"]["value"]) if ec_en_wpg.conditions["uv_index"] and ec_en_wpg.conditions["uv_index"]["value"] != None else "--"
        pop = str(ec_en_wpg.conditions["pop"]["value"]) if ec_en_wpg.conditions["pop"] and ec_en_wpg.conditions["pop"]["value"] != None else "0"
        
        # check severity of uv index
        if ec_en_wpg.conditions["uv_index"]["value"] != None:
            if ec_en_wpg.conditions["uv_index"]["value"] <= 2:
                uv_cat = "LOW"
            elif ec_en_wpg.conditions["uv_index"]["value"] > 2 and ec_en_wpg.conditions["uv_index"]["value"] <= 5:
                uv_cat = "MODERT"
            elif ec_en_wpg.conditions["uv_index"]["value"] > 5 and ec_en_wpg.conditions["uv_index"]["value"] <= 7:
                uv_cat = "HIGH"
            elif ec_en_wpg.conditions["uv_index"]["value"] > 7 and ec_en_wpg.conditions["uv_index"]["value"] <= 10:
                uv_cat = "V.HIGH"
            elif ec_en_wpg.conditions["uv_index"]["value"] > 10:
                uv_cat = "EXTRM"
        else:
            uv_cat = ""
        
        # check if windchill or humidex is present, if neither leave area blank
        if ("value" in ec_en_wpg.conditions["wind_chill"] and ec_en_wpg.conditions["wind_chill"]["value"] != None):
            windchill = str(ec_en_wpg.conditions["wind_chill"]["value"])
            windchildex = "WIND CHILL " + windchill + " C"
        elif ("value" in ec_en_wpg.conditions["humidex"] and ec_en_wpg.conditions["humidex"]["value"] != None):
            humidex = str(ec_en_wpg.conditions["humidex"]["value"])
            windchildex = "HUMIDEX " + humidex + " C       "
        else:
            windchildex = ""
        
        # check if there is wind - if not, display NO WIND
        if ("value" in ec_en_wpg.conditions["wind_dir"] and ec_en_wpg.conditions["wind_dir"]["value"] != None):        
            wind_dir = ec_en_wpg.conditions["wind_dir"]["value"]
            wind_spd = str(ec_en_wpg.conditions["wind_speed"]["value"])
            windstr = "WIND " + wind_dir + " " + wind_spd + " KMH"
        else:
            windstr = "NO WIND"
                
        # check visibility, if no data then show --
        if ("value" in ec_en_wpg.conditions["visibility"] and ec_en_wpg.conditions["visibility"]["value"] != None):
            visibility = str(ec_en_wpg.conditions["visibility"]["value"])
            visibstr = "VISBY " + visibility.rjust(5," ") + " KM         "
        else:
            visibstr = "VISBY    -- KM         "
     
        # create 8 lines of text     
        s1 = ("CORNWALL " + real_forecast_time + " " + str(local_tz) + "  " + real_forecast_date.upper()).center(35," ")
        s2 = "TEMP  " + temp_cur.rjust(5," ") + " C                "
        s2 = s2[0:24] + " HIGH " + temp_high.rjust(3," ") + " C"
        s3 = word_short(condition,24) + "                         "
        s3 = s3[0:24] + "  LOW " + temp_low.rjust(3," ") + " C"
        s4 = ("CHANCE OF PRECIP. " + pop + " %").center(35," ")
        s5 = "HUMID  " + humidity.rjust(5," ") + " %         "
        s5 = s5[0:18] + windstr.rjust(17," ")
        s6 = visibstr[0:18] + windchildex.rjust(17," ")
        s7 = "DEW   " + dewpoint.rjust(5," ") + " C         " 
        s7 = s7[0:18] + ("UV INDEX " + uv_index + " " + uv_cat).rjust(17," ")
        s8 = ("PRESSURE " + pressure + " KPA AND " + tendency.upper()).center(35," ")

    elif (PageNum == 2):
    
        # ===================== Screen 2 =====================
        # text forecast for 5 days - page 1 of 3
        #print(time.strftime("%H:%M.") + prog + ver + ".WEATHER_PAGE-display page " + str(PageNum))   

        # pull text forecasts from env_canada
        wsum_day1 = textwrap.wrap(ec_en_wpg.conditions["text_summary"]["value"].upper(), 35)
        wsum_day2 = textwrap.wrap(ec_en_wpg.daily_forecasts[1]["period"].upper() + ".." + ec_en_wpg.daily_forecasts[1]["text_summary"].upper(), 35)
        wsum_day3 = textwrap.wrap(ec_en_wpg.daily_forecasts[2]["period"].upper() + ".." + ec_en_wpg.daily_forecasts[2]["text_summary"].upper(), 35)
        wsum_day4 = textwrap.wrap(ec_en_wpg.daily_forecasts[3]["period"].upper() + ".." + ec_en_wpg.daily_forecasts[3]["text_summary"].upper(), 35)    
        wsum_day5 = textwrap.wrap(ec_en_wpg.daily_forecasts[4]["period"].upper() + ".." + ec_en_wpg.daily_forecasts[4]["text_summary"].upper(), 35)
        wsum_day6 = textwrap.wrap(ec_en_wpg.daily_forecasts[5]["period"].upper() + ".." + ec_en_wpg.daily_forecasts[5]["text_summary"].upper(), 35)   
        
        # build text_forecast string
        global text_forecast
        text_forecast = wsum_day1 + linebreak + wsum_day2 + linebreak + wsum_day3 + linebreak + wsum_day4 + linebreak + wsum_day5 + linebreak + wsum_day6
    
        # create 8 lines of text
        s1 = "CORNWALL CITY FORECAST".center(35," ")
        s2 = (text_forecast[0]).center(35," ") if len(text_forecast) >= 1 else " "
        s3 = (text_forecast[1]).center(35," ") if len(text_forecast) >= 2 else " "
        s4 = (text_forecast[2]).center(35," ") if len(text_forecast) >= 3 else " "
        s5 = (text_forecast[3]).center(35," ") if len(text_forecast) >= 4 else " "
        s6 = (text_forecast[4]).center(35," ") if len(text_forecast) >= 5 else " "
        s7 = (text_forecast[5]).center(35," ") if len(text_forecast) >= 6 else " "
        s8 = (text_forecast[6]).center(35," ") if len(text_forecast) >= 7 else " "

    elif (PageNum == 3):
    
        # ===================== Screen 3 =====================
        # text forecast for 5 days - page 2 of 3
        # Screen 1 must run first as it sets up variables
        #print(time.strftime("%H:%M.") + prog + ver + ".WEATHER_PAGE-display page " + str(PageNum))    
        
        # create 8 lines of text
        s1 = "CORNWALL CITY FORECAST CONT'D".center(35," ")
        s2 = (text_forecast[7]).center(35," ") if len(text_forecast) >= 8 else " "
        s3 = (text_forecast[8]).center(35," ") if len(text_forecast) >= 9 else " "
        s4 = (text_forecast[9]).center(35," ") if len(text_forecast) >= 10 else " "
        s5 = (text_forecast[10]).center(35," ") if len(text_forecast) >= 11 else " "
        s6 = (text_forecast[11]).center(35," ") if len(text_forecast) >= 12 else " "
        s7 = (text_forecast[12]).center(35," ") if len(text_forecast) >= 13 else " "
        s8 = (text_forecast[13]).center(35," ") if len(text_forecast) >= 14 else " " 

    elif (PageNum == 4):
 
        # ===================== Screen 4 =====================
        # text forecast for 5 days - page 3 of 3 -- optional
        # Screen 1 must run first as it sets up variables        
        
        # check if this page is needed
        if len(text_forecast) <= 14:
            #print(time.strftime("%H:%M.") + prog + ver + ".WEATHER_PAGE-display page " + str(PageNum) + " skipped!") 
            PageNum = PageNum + 1 #skip this page
        else:
            #print(time.strftime("%H:%M.") + prog + ver + ".WEATHER_PAGE-display page " + str(PageNum))    
        
            # create 8 lines of text       
            s1 = "CORNWALL CITY FORECAST CONT'D".center(35," ")
            s2 = (text_forecast[14]).center(35," ") if len(text_forecast) >= 15 else " "       
            s3 = (text_forecast[15]).center(35," ") if len(text_forecast) >= 16 else " "        
            s4 = (text_forecast[16]).center(35," ") if len(text_forecast) >= 17 else " "
            s5 = (text_forecast[17]).center(35," ") if len(text_forecast) >= 18 else " "
            s6 = (text_forecast[18]).center(35," ") if len(text_forecast) >= 19 else " "
            s7 = (text_forecast[19]).center(35," ") if len(text_forecast) >= 20 else " "
            s8 = (text_forecast[20]).center(35," ") if len(text_forecast) >= 21 else " "                  
    
    elif (PageNum == 5):
    
        # ===================== Screen 5 =====================
        # Weather States
        #print(time.strftime("%H:%M.") + prog + ver + ".WEATHER_PAGE-display page " + str(PageNum))            
 
        # weather data 
        temp_cur = str(ec_en_wpg.conditions["temperature"]["value"]) 
        temp_high = str(ec_en_wpg.conditions["high_temp"]["value"])
        temp_low = str(ec_en_wpg.conditions["low_temp"]["value"])
       
        if ("value" in ec_en_wpg.conditions["high_temp_yesterday"] and ec_en_wpg.conditions["high_temp_yesterday"]["value"] != None):    
            temp_yest_high =str(round(ec_en_wpg.conditions["high_temp_yesterday"]["value"]))
        else:
            temp_yest_high = ""
        
        if ("value" in ec_en_wpg.conditions["low_temp_yesterday"] and ec_en_wpg.conditions["low_temp_yesterday"]["value"] != None):    
            temp_yest_low =str(round(ec_en_wpg.conditions["low_temp_yesterday"]["value"]))
        else:
            temp_yest_low = ""       
        
        temp_norm_high =str(ec_en_wpg.conditions["normal_high"]["value"])
        temp_norm_low =str(ec_en_wpg.conditions["normal_low"]["value"])      

        # create 8 lines of text   
        s1 = ("TEMPERATURE STATISTICS FOR CORNWALL").center(35," ")
        s2 = "       CURRENT " + temp_cur.rjust(5," ") + " C  "
        s3 = ""
        s4 = "                 LOW    HIGH"
        s5 = "        TODAY   " + temp_low.rjust(3," ") + " C  " + temp_high.rjust(3," ") + " C"
        s6 = "    YESTERDAY   " + temp_yest_low.rjust(3," ") + " C  " + temp_yest_high.rjust(3," ") + " C"
        s7 = "       NORMAL   " + temp_norm_low.rjust(3," ") + " C  " + temp_norm_high.rjust(3," ") + " C"
        s8 = ""
    
    elif (PageNum == 6):    
    
        
        # ===================== Screen 10 =====================
        # static channel listing page 1
        #print(time.strftime("%H:%M.") + prog + ver + ".WEATHER_PAGE-display page " + str(PageNum))         
      
        # create 8 lines of text
        s1 = "======= WHAT'S ON TONIGHT ======="
        s2 = ""
        s3 = "6PM        Cornwal Transit Tales"    
        s4 = "7PM  No Bones About It Wing Show" 
        s5 = "8PM               London Calling"         
        s6 = "9PM             Karaoke with Kam"
        s7 = "10PM     Stacey Case Presents..."
        s8 = "11PM         Cornwall Night Live"

    elif (PageNum == 7):    
        
        # ===================== Screen 11 =====================
        # static channel listing page 2
        #print(time.strftime("%H:%M.") + prog + ver + ".WEATHER_PAGE-display page " + str(PageNum))         
      
        # create 8 lines of text   
        s1 = "=======CHANNEL LISTING CONT'D======="
        s2 = ""      
        s3 = "10   CBC    (CBWT)  [ANALOG]" 
        s4 = "13.1 CITY-TV(CHMI)  [DIGITAL-HD]"
        s5 = "14   Cartoons       [ANALOG]"       
        s6 = "16   80s Sitcoms    [ANALOG]"
        s7 = "22   90s Sitcoms    [ANALOG]"
        s8 = "24   GLOBAL (CKND)  [ANALOG]" 

        
    elif (PageNum == 8):    
        
        # ===================== Screen 12 =====================
        # static channel listing page 3
        #print(time.strftime("%H:%M.") + prog + ver + ".WEATHER_PAGE-display page " + str(PageNum))         
      
        # create 8 lines of text   
        s1 = "=======CHANNEL LISTING CONT'D======="   
        s2 = ""
        s3 = "30   Music Videos   [ANALOG-ST]"   
        s4 = "35.1 FAITH  (CIIT)  [DIGITAL-HD]"
        s5 = "50   British TV     [ANALOG]"    
        s6 = "54   WEATHER        [ANALOG]"
        s7 = ""
        s8 = "             ©ßÖRTHØLÈ CABLE SYSTEMS"        

    # create the canvas for middle page text

    weather = Canvas(root, height=290, width=720, bg=PageColour)
    weather.place(x=0, y=95)
    weather.config(highlightbackground=PageColour)
    
    # place the 8 lines of text
    weather.create_text(80, 12, anchor='nw', text=s1, font=('VCR OSD Mono', 21, "bold"), fill="white")
    weather.create_text(80, 49, anchor='nw', text=s2, font=('VCR OSD Mono', 21,), fill="white")
    weather.create_text(80, 81, anchor='nw', text=s3, font=('VCR OSD Mono', 21,), fill="white")
    weather.create_text(80, 112, anchor='nw', text=s4, font=('VCR OSD Mono', 21,), fill="white")
    weather.create_text(80, 145, anchor='nw', text=s5, font=('VCR OSD Mono', 21,), fill="white")
    weather.create_text(80, 177, anchor='nw', text=s6, font=('VCR OSD Mono', 21,), fill="white")
    weather.create_text(80, 209, anchor='nw', text=s7, font=('VCR OSD Mono', 21,), fill="white") 
    weather.create_text(80, 241, anchor='nw', text=s8, font=('VCR OSD Mono', 21,), fill="white") 
    
    # Toggle Page Colour between Red & Blue
    if (PageColour == "#0000A5"): # blue
        PageColour = "#BC0000" # red
    else:
        PageColour = "#0000A5" # blue
        
    # Increment Page Number or Reset
    if (PageNum < PageTotal):
        PageNum = PageNum + 1
    elif (PageNum >= PageTotal):
        PageNum = 1
    
    root.after(15000, weather_page, PageColour, PageNum) # re-run every 10sec from program launch

# DEF update weather for all cities
def weather_update(group):

        global real_forecast_time
        global real_forecast_date
        global real_forecast_month
        global real_forecaste_year

        # used to calculate update time
        t1 = datetime.datetime.now().timestamp() # record current timestamp
        timechk = t1 - updt_tstp[group] # compare timestamp vs last update time -- not used for group 0 (initialize mode)
        
        if (timechk  > 1800) or (group == 0): #check if 30min has elapsed since last group update, but always allow group 0 updates (initial refresh)
            # update weather for cities, depending on group number requested. 0 == initial refresh on launch
            if (group == 0 or group == 1):
                asyncio.run(ec_en_wpg.update())
                asyncio.run(ec_en_brn.update()) 
                asyncio.run(ec_en_thm.update()) 
                asyncio.run(ec_en_tps.update()) 
                asyncio.run(ec_en_fln.update()) 
                asyncio.run(ec_en_chu.update()) 
                asyncio.run(ec_en_ken.update()) 
                asyncio.run(ec_en_tby.update())
                real_forecast_time = time.strftime("%I %p") # this is used as the forecast time when showing the weather. for some reason the dictionary was always reporting 22:00 for forecast time
                if real_forecast_time == "12 PM": 
                    real_forecast_time = "NOON" # just to add some fun
                real_forecast_date = datetime.datetime.now().strftime("%a %b %d/%Y")# this is used as the forecast time when showing the weather. dictionary from env_canada reports weird (GMT maybe?)
                    
                if group == 0:
                    updt_tstp[1] = datetime.datetime.now().timestamp() # record timestamp to update
                    updt_tstp[2] = datetime.datetime.now().timestamp() # record timestamp to update
                    updt_tstp[3] = datetime.datetime.now().timestamp() # record timestamp to update
                else:
                    updt_tstp[group] = datetime.datetime.now().timestamp() # record timestamp to update
                
            if (group == 0 or group == 2):
                asyncio.run(ec_en_vic.update()) 
                asyncio.run(ec_en_van.update()) 
                asyncio.run(ec_en_edm.update()) 
                asyncio.run(ec_en_cal.update()) 
                asyncio.run(ec_en_ssk.update()) 
                asyncio.run(ec_en_reg.update()) 
                asyncio.run(ec_en_wht.update()) 
                real_forecast_date = datetime.datetime.now().strftime("%a %b %d/%Y")# this is used as the forecast time when showing the weather. dictionary from env_canada reports weird (GMT maybe?)
                if group == 0:
                    updt_tstp[1] = datetime.datetime.now().timestamp() # record timestamp to update
                    updt_tstp[2] = datetime.datetime.now().timestamp() # record timestamp to update
                    updt_tstp[3] = datetime.datetime.now().timestamp() # record timestamp to update
                else:
                    updt_tstp[group] = datetime.datetime.now().timestamp() # record timestamp to update
        
            if (group == 0 or group == 3):
                asyncio.run(ec_en_tor.update()) 
                asyncio.run(ec_en_otw.update()) 
                asyncio.run(ec_en_qbc.update()) 
                asyncio.run(ec_en_mtl.update()) 
                asyncio.run(ec_en_frd.update()) 
                asyncio.run(ec_en_hal.update()) 
                asyncio.run(ec_en_stj.update()) 
                real_forecast_date = datetime.datetime.now().strftime("%a %b %d/%Y")# this is used as the forecast time when showing the weather. dictionary from env_canada reports weird (GMT maybe?)
                if group == 0:
                    updt_tstp[1] = datetime.datetime.now().timestamp() # record timestamp to update
                    updt_tstp[2] = datetime.datetime.now().timestamp() # record timestamp to update
                    updt_tstp[3] = datetime.datetime.now().timestamp() # record timestamp to update
                else:
                    updt_tstp[group] = datetime.datetime.now().timestamp() # record timestamp to update

            # calculate time it took to update
            t = datetime.datetime.now().timestamp() - t1 # used to report how long update took for debug print lines
            print(time.strftime("%H:%M.") + prog + ver + ".WEATHER_UPDATE-weather group " + str(group) + " updated in " + str(round(t,2)) + " seconds")
        else:
            print(time.strftime("%H:%M.") + prog + ver + ".WEATHER_UPDATE-weather group " + str(group) + " not updated. only ~" + str(round(timechk//60)) + " minutes elapsed out of required 30")

# DEF bottom marquee scrolling text
def bottom_marquee(grouptotal):

    group = 1

    # scrolling text canvas
    marquee = Canvas(root, height=120, width=720, bg="green")
    marquee.config(highlightbackground="green")
    marquee.place(x=0, y=390)

    # read in RSS data and prepare it
    width = 35
    pad = ""
    for r in range(width): #create an empty string of 35 characters
        pad = pad + " " 

    url = "http://cornwalltourism.com/feed"
    wpg = feedparser.parse(url)
    print(time.strftime("%H:%M.") + prog + ver + ".BOTTOM_MARQUEE-RSS feed refreshed")

    # use the first 8 entries on the wpg news RSS feed
    wpg_desc = wpg.entries[0]["description"] + pad + wpg.entries[1]["description"] + pad + wpg.entries[2]["description"] + pad + wpg.entries[3]["description"] + pad + wpg.entries[4]["description"] + pad + wpg.entries[5]["description"] + pad + wpg.entries[6]["description"] + pad + wpg.entries[7]["description"]
    mrq_msg = wpg_desc.upper()

    # use the length of the news feeds to determine the total pixels in the scrolling section
    marquee_length = len(mrq_msg)
    if (marquee_length * 24)<31000:
        pixels = marquee_length * 24 # roughly 24px per char
    else:
        pixels = 31000

    # setup scrolling text
    text = marquee.create_text(1, 2, anchor='nw', text=pad + mrq_msg + pad + pad, font=('VCR OSD Mono', 25,), fill="white")

    restart_marquee = True # 
    while restart_marquee:
        restart_marquee = False
        print(time.strftime("%H:%M.") + prog + ver + ".BOTTOM_MARQUEE-starting RSS display")
        for p in range(pixels+730):
            marquee.move(text, -1, 0) #shift the canvas to the left by 1 pixel
            marquee.update()
            time.sleep(0.005) # scroll every 5ms
            if (p == pixels+729): # once the canvas has finished scrolling
                restart_marquee = True
                marquee.move(text, pixels+729, 0) # reset the location
                if (group <= grouptotal):
                    print(time.strftime("%H:%M.") + prog + ver + ".BOTTOM_MARQUEE-refreshing weather info")
                    weather_update(group) # update weather information between RSS scrolls
                    print(time.strftime("%H:%M.") + prog + ver + ".BOTTOM_MARQUEE-weather info refreshed")
                    group = group + 1
                else:
                    print(time.strftime("%H:%M.") + prog + ver + ".BOTTOM_MARQUEE-refreshing weather info")
                    group = 1
                    weather_update(group) # update weather information between RSS scrolls
                    print(time.strftime("%H:%M.") + prog + ver + ".BOTTOM_MARQUEE-weather info refreshed")
                    group = group + 1
                    
                p = 0 # keep the for loop from ending

# DEF generate playlist from folder
def playlist_generator(musicpath):

    # this code from https://thispointer.com/python-how-to-get-list-of-files-in-directory-and-sub-directories/
    # create a list of file and sub directories 
    # names in the given directory 

    print(time.strftime("%H:%M.") + prog + ver + ".PLAYLIST_GENERATOR-searching for music files...")
    filelist = os.listdir(musicpath)
    allFiles = list()
    # Iterate over all the entries    
    for entry in filelist:
        # Create full path
        fullPath = os.path.join(musicpath,entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + playlist_generator(fullPath)
        else:
            allFiles.append(fullPath)
    print(time.strftime("%H:%M.") + prog + ver + ".PLAYLIST_GENERATOR-found " + str(len(allFiles)))
    return allFiles

# DEF play background music
def music_player(songNumber, playlist, musicpath):

    # make sure musicpath ONLY contains playable mp3 files. this does not check if files are valid and will crash if it tries to play something else

    if ((pygame.mixer.music.get_busy() == False) and (songNumber < len(playlist))):
        print(time.strftime("%H:%M.") + prog + ver + ".MUSIC_PLAYER-playing song " + playlist[songNumber])  
        pygame.mixer.music.load(playlist[songNumber])
        pygame.mixer.music.play(loops = 0)
        songNumber = songNumber + 1
    elif ((pygame.mixer.music.get_busy() == False) and (songNumber >= len(playlist))):
        print(time.strftime("%H:%M.") + prog + ver + ".MUSIC_PLAYER-playlist complete,re-shuffling... ")
        songNumber = 0
        random.shuffle(playlist)   

    root.after(2000, music_player, songNumber, playlist, musicpath) # re-run every 2sec from program launch

# DEF Word Shortner 5000
def word_short(phrase, length):
    
    # dictionary of shortened words
    dict = {                    
        "BECOMING" : "BCMG",
        "SCATTERED" : "SCTD",
        "PARTLY" : "PTLY",
        "SHOWER" : "SHWR",
        "CLOUDY" : "CLDY",
        "DRIZZLE" : "DRZLE",
        "FREEZING" : "FRZG",
        "THUNDERSHOWER" : "THNDSHR",
        "THUNDERSTORM" : "THNDSTM",
        "PRECIPITATION" : "PRECIP",
        "CHANCE" : "CHNCE",
        "DEVELOPING" : "DVLPNG",
        "WITH" : "W",
        "SHOWER" : "SHWR",
        "LIGHT" : "LT",
        "HEAVY" : "HVY",
        "BLOWING" : "BLWNG"
    }

    phrase = str(phrase).upper()  # convert to upper case for convenience and for later
    # ... rest of the code

    
    if len(phrase) > length:    # check if phrase is too long
        
        if phrase == "A MIX OF SUN AND CLOUD":  # just for this specific condition
            phrase = "SUN CLOUD MIX"
        
        for key, value in dict.items():     # replace words using dictionary dict
            phrase = (re.sub(key, value, phrase))  
            
        #print(prog + ver + ".WORD_SHORT-phrase shortened to " + phrase)
        return phrase
        
    else:
        return phrase       # if length is fine, do nothing and send it back

# ROOT main stuff

# setup root
root = Tk()
root.attributes('-fullscreen',False)
root.geometry("720x480") # this must be 720x480 for a proper filled out screen on composite output. 640x480 will have black bar on RH side. use 720x576 for PAL.
root.config(cursor="none", bg="green")
root.wm_title("wpg-weatherchan")

# Clock - Top RIGHT
# this got complicated due to the new font (7-Segment Normal), which doesn't have proper colon(:) char, 
# so I've removed the colon from the time string and added them on top using VCR OSD Mono
print(time.strftime("%H:%M.") + prog + ver + ".ROOT-placing clock")
timeText = Label(root, text="", font=("7-Segment Normal", 22), fg="white", bg="green")
timeText.place(x=403, y=42)
timeColon1 = Label(root, text=":", font=("VCR OSD Mono", 32), fg="white", bg="green")
timeColon1.place(x=465, y=36)
timeColon2 = Label(root, text=":", font=("VCR OSD Mono", 32), fg="white", bg="green")
timeColon2.place(x=560, y=36)
print(time.strftime("%H:%M.") + prog + ver + ".ROOT-launching clock updater")
clock()

# Title - Top LEFT
print(time.strftime("%H:%M.") + prog + ver + ".ROOT-placing Title Text")
Title = Label(root, text="CORNWALL SCENE TV", font=("VCR OSD Mono", 22, "bold"), fg="white", bg="green")
Title.place(x=80, y=50)

# use ECWeather to gather weather data, station_id is from the csv file provided with ECDada -- homepage: https://github.com/michaeldavie/env_canada

# group 1
ec_en_wpg = ECWeather(station_id='ON/s0000071', language='english')
ec_en_brn = ECWeather(station_id='MB/s0000492', language='english')
ec_en_thm = ECWeather(station_id='MB/s0000695', language='english')
ec_en_tps = ECWeather(station_id='MB/s0000644', language='english')
ec_en_chu = ECWeather(station_id='MB/s0000779', language='english')
ec_en_fln = ECWeather(station_id='MB/s0000015', language='english')
ec_en_ken = ECWeather(station_id='ON/s0000651', language='english')
ec_en_tby = ECWeather(station_id='ON/s0000411', language='english')

# group 2
ec_en_vic = ECWeather(station_id='BC/s0000775', language='english')
ec_en_van = ECWeather(station_id='BC/s0000141', language='english')
ec_en_edm = ECWeather(station_id='AB/s0000045', language='english')
ec_en_cal = ECWeather(station_id='AB/s0000047', language='english')
ec_en_ssk = ECWeather(station_id='SK/s0000797', language='english')
ec_en_reg = ECWeather(station_id='SK/s0000788', language='english')
ec_en_wht = ECWeather(station_id='YT/s0000825', language='english')

# group 3
ec_en_tor = ECWeather(station_id='ON/s0000458', language='english')
ec_en_otw = ECWeather(station_id='ON/s0000430', language='english')
ec_en_mtl = ECWeather(station_id='QC/s0000635', language='english')
ec_en_qbc = ECWeather(station_id='QC/s0000620', language='english')
ec_en_frd = ECWeather(station_id='NB/s0000250', language='english')
ec_en_hal = ECWeather(station_id='NS/s0000318', language='english')
ec_en_stj = ECWeather(station_id='NL/s0000280', language='english')

# total number of groups broken up to update sections of weather data, to keep update time short
grouptotal = 3 

# create time check updated list for weather_udpdate
updt_tstp = [0,0,0,0]

# create string to store hour that weather was updated. Use this to show "forecast time" since ec_en_wpg.forecast_time always reports the same time!! Date is also weird
real_forecast_time = ""
real_forecast_date = ""

# Update Weather Information
print(time.strftime("%H:%M.") + prog + ver + ".ROOT-launching weather update")
weather_update(0) # update all cities

# Middle Section (Cycling weather pages, every 30sec)
print(time.strftime("%H:%M.") + prog + ver + ".ROOT-launching weather_page")
PageColour = "Blue"
PageNum = 1
weather_page(PageColour, PageNum)

# Generate background music playlist
print(time.strftime("%H:%M.") + prog + ver + ".ROOT-launching playlist generator")
musicpath = "C:\\Users\\scampbell\\Desktop\\weather\\stermusic" # must show full path
playlist = playlist_generator(musicpath) # generate playlist array
random.shuffle(playlist) # shuffle playlist

# Play background music on shuffle using pygame
print(time.strftime("%H:%M.") + prog + ver + ".ROOT-launching background music")
songNumber = 1
pygame.mixer.init()
music_player(songNumber, playlist, musicpath)

# Bottom Scrolling Text (City of Winnipeg RSS Feed)
print(time.strftime("%H:%M.") + prog + ver + ".ROOT-launching bottom_marquee")
bottom_marquee(grouptotal)

# loop program  
root.mainloop()

