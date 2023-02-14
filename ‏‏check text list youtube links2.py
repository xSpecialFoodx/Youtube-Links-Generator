from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from unidecode import unidecode
from selenium.webdriver.chrome.options import Options
import Levenshtein

from fuzzywuzzy import fuzz
import time
import os

import os, io
import webbrowser
from urllib import request
import math

overwrite_database = False
create_playlists = True

file_path = r"C:\sometextfile.txt"
editted_file_path = r"C:\sometextfile-links.txt"
database_file_path = r"C:\database-links.txt"

search_additional_text = ' ' + "gameplay"
special_words = {"gameplay": 90, "walkthrough": 75, "playthrough": 75, "game": 40}


names_with_links_database = []
names_with_links = []
names = []
with open(file_path) as file:
    for line in file: 
        line = unidecode(line.strip()) #or some other preprocessing
        names.append(line) #storing everything in memory!
        
if os.path.isfile(editted_file_path) is True:
    with open(editted_file_path) as file:
        for line in file:
            names_with_links.append(line.split("\t")) #storing everything in memory!
        
if os.path.isfile(database_file_path) is True:
    with open(database_file_path) as file:
        for line in file:
            names_with_links_database.append(line.split("\t")) #storing everything in memory!

link_index_score = 30
link_name_score = 20
link_name_partial_score = 15
link_special_words_score = 35
min_links_amount = 11  # max is 20

links = []
links_database = []
    
for name_with_links in names_with_links:
    if len(name_with_links) > 1:
        links.append(name_with_links)
    
for name_with_links_database in names_with_links_database:
    if len(name_with_links_database) > 1:
        links_database.append(name_with_links_database)
        
method_found = False

for link in links:
    item_search = link[0] + search_additional_text
    
    for link_database in links_database:
        if link_database[0] == item_search:
            method_found = True

            break
        
    if method_found is True:
        method_found = False
    else:
        links_database.append([item_search, link[1], link[2], link[len(link) - 1]])
    
def create_playlist(videos_ids):
    # returns the playlist's id
    playlist_link = "http://www.youtube.com/watch_videos?video_ids=" + ",".join(videos_ids)

    response = request.urlopen(playlist_link)
    
    return response.geturl().split('list=')[1]

def check_playlist_edit(playlist_id):
    # edit playlist with this URL
    return "https://www.youtube.com/playlist?list=" + playlist_id + "&disable_polymer=true"

def check_playlist_watch(item_link_link_id, playlist_id):
    # or start playing from first to last with this one
    return "https://www.youtube.com/watch?v=" + item_link_link_id + "&list=" + playlist_id


def calculate_logarithmic_scaling(percentage, scale_up):
    # used "https://www.dcode.fr/function-equation-finder" in order to make a logarithmic equation
    # with the points (1, 94), (100, 0)
    # used 94 because we want it to be close to 100 at x = 0
    #
    # this way we obtained the equation:
    # 238.309 - 29.2138 * ln(33.8317 * x + 105.902)
    #
    # fixing the number to be 100 at 0:
    #
    # y = 238.309 - 29.2138 * ln(33.8317 * x + 105.902)
    #
    # y = 29.2138 * ln(33.8317 * 0 + 105.902)
    # y = 29.2138 * ln(105.902)
    # y = 136.209
    #
    # using the first part as the guiding point (238.309)
    #
    # x - 136.209 = 100
    # x = 236.209
    #
    # the new equation:
    # 236.209 - 29.2138 * ln(33.8317 * x + 105.902)
    #
    # now checking when it's 0:
    #
    # 236.209 - 29.2138 * ln(33.8317 * x + 105.902) = 0
    # 29.2138 * ln(33.8317 * x + 105.902) = 236.209
    # ln(33.8317 * x + 105.902) = 236.209 / 29.2138
    # e ^ (236.209 / 29.2138) = 33.8317 * x + 105.902
    # e ^ (236.209 / 29.2138) - 105.902 =  33.8317 * x
    # x = (e ^ (236.209 / 29.2138) - 105.902) / 33.8317
    # x = 92.848
    #
    # since it gets to 0 fast (a logarithmic function) we can round it to 92
    #
    # so the range is between 0 to 92
    
    current_percentage = (
        236.209
        - 29.2138 * math.log(
            33.8317 * (percentage * 92 / 100)
            + 105.902
        )
    )
    
    if scale_up is True:
        current_percentage = 100 - current_percentage
    
    return current_percentage

opt = Options()
opt.add_argument("--incognito")

driver = webdriver.Chrome(executable_path=r'C:\chromedriver.exe', chrome_options=opt)

driver.get("http://youtube.com")
    
for item in names:
    method_found = False
    
    item_search = item + search_additional_text
    
    for link in links:
        if item == link[0]:
            method_found = True
            
            break
            
    if method_found is True:
        method_found = False
    else:
        links_database_index = 0
        
        while links_database_index < len(links_database):
            link_database = links_database[links_database_index]

            if item_search == link_database[0]:
                if overwrite_database is True:
                    links_database.pop(links_database_index)
                else:
                    method_found = True

                    link = [item, link_database[1], link_database[2], link_database[3]]
                    links.append(link)

                    f = open(editted_file_path, "w" if os.path.isfile(editted_file_path) is False else "a")
                    f.write("\t".join(link))
                    f.close()

                    break
            else:
                links_database_index += 1

        if method_found is True:
            method_found = False
        else:
            while method_found is False:
                error_found = False
                
                item_links=[]

                driver_element = driver.find_element("name", "search_query")
                driver_element.send_keys(Keys.CONTROL, 'a')
                driver_element.send_keys(item_search)
                driver.find_element("id", "search-icon-legacy").click()
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.ID, "video-title")))
                time.sleep(1)
                found_links = ''
                sleeping_amount = 0
                while len(found_links) < min_links_amount and sleeping_amount < 30:
                    found_links = driver.find_elements("xpath", "//a[@id='video-title']")
                    time.sleep(0.3)
                    sleeping_amount += 1

                current_link_index_score = link_index_score
                index = 0
                for x in found_links:
                    try:
                        item_link_link = unidecode(x.get_attribute("href").strip())
                        item_link_link_watch_location = item_link_link.find("watch")
                        
                        if item_link_link_watch_location > 0:
                            item_link_link_ampersent_location = item_link_link.find("&")

                            if item_link_link_ampersent_location > 0:
                                item_link_link = item_link_link[:item_link_link_ampersent_location]

                            item_link_title = unidecode(x.get_attribute("title").strip())
                            item_link_name_partial_score = fuzz.partial_ratio(item.upper(), item_link_title.upper()) * link_name_partial_score / 100
                            bigger_length = len(item_search) if len(item_search) > len(item_link_title) else len(item_link_title)
                            item_link_name_score = fuzz.partial_ratio(item.upper(), item_link_title.upper()) * (100 - Levenshtein.distance(item_search.upper(), item_link_title.upper()) / bigger_length * 100) / 100 * link_name_score / 100
                            item_link_name_total_score = (item_link_name_score + item_link_name_partial_score)
                            item_link_title_splitted = item_link_title.split(" ")
                            max_item_link_special_words_score = 0
                            current_item_link_special_words_score = 0
                            for item_link_title_splitted_cell in item_link_title_splitted:
                                for special_word in special_words:
                                    bigger_length = len(special_word) if len(special_word) > len(item_link_title_splitted_cell) else len(item_link_title_splitted_cell)
                                    smaller_length = len(special_word) if len(special_word) < len(item_link_title_splitted_cell) else len(item_link_title_splitted_cell)
                                    
                                    current_item_link_special_words_score = (
                                        (100 - Levenshtein.distance(special_word.upper(), item_link_title_splitted_cell.upper()) / bigger_length * 100)
                                        * smaller_length / bigger_length
                                        * special_words[special_word] / 100
                                        * link_special_words_score / 100
                                    )
                                    
                                    if current_item_link_special_words_score > max_item_link_special_words_score:
                                        max_item_link_special_words_score = current_item_link_special_words_score

                            item_link_special_words_score = max_item_link_special_words_score
                            item_link_score = current_link_index_score + item_link_name_score + item_link_name_partial_score + item_link_special_words_score
                            item_link = {"index": index, "link": item_link_link, "title": item_link_title, "score": item_link_score}
                            item_links.append(item_link)
                    except:
                        error_found = True
                        
                        break

                    index += 1
                    current_link_index_score = link_index_score * calculate_logarithmic_scaling(index / len(found_links) * 100, False) / 100
                    
                if error_found is True:
                    error_found = False
                else:
                    method_found = True
                  
            method_found = False
                
            item_links = (
                sorted(
                    item_links
                    , key=lambda item_link: (
                        item_link["score"]
                    )
                    , reverse=True
                )
            )
            
            link = [item, item_links[0]["title"], item_links[0]["link"], str("%.3f" % item_links[0]["score"]) + '\n']
            links.append(link)
            
            f = open(editted_file_path, "w" if os.path.isfile(editted_file_path) is False else "a")
            f.write("\t".join(link))
            f.close()
            
            link = [item_search, link[1], link[2], link[3]]
                
            f = open(database_file_path, "w" if os.path.isfile(database_file_path) is False else "a")
            f.write("\t".join(link))
            f.close()

if len(links_database) > 0:
    links_database = (
        sorted(
            links_database
            , key=lambda link_database: (
                link_database[0]
            )
        )
    )

    links_database_index = 1
    link_database_last = links_database[0]

    while links_database_index < len(links_database):
        link_database = links_database[links_database_index]
        
        if link_database[0] == link_database_last[0]:
            links_database.pop(links_database_index)
        else:
            link_database_last = link_database
            
            links_database_index += 1
  
f = open(database_file_path, "w")  

for link_database in links_database:
    link = [link_database[0], link_database[1], link_database[2], link_database[3]]

    f.write("\t".join(link))

f.close()
        
if create_playlists is True:
    item_link_link_ids = []

    for link_index_a in range(0, len(links)):
        link_a = links[link_index_a]
        
        item_link_link = link_a[2]
        
        item_link_link_id = item_link_link[item_link_link.find("?v=") + 3:]
        item_link_link_ids.append(item_link_link_id)
        
        if len(item_link_link_ids) == 50:
            playlist_id_found = None
            error_found = False

            for link_index_b in range(link_index_a - 50 + 1, link_index_a + 1):
                link_b = links[link_index_b]

                if len(link_b) == 5:
                    playlist_watch_link = link_b[3]
                    playlist_id = playlist_watch_link.split("&list=")[1]
                    
                    if playlist_id_found is None:
                        playlist_id_found = playlist_id
                    elif playlist_id != playlist_id_found:
                        error_found = True
                else:
                    error_found = True
                    
                if error_found is True:
                    break
                
            if error_found is True:
                error_found = False

                playlist_id = create_playlist(item_link_link_ids)

                for link_index_b in range(link_index_a - 50 + 1, link_index_a + 1):
                    link_b = links[link_index_b]

                    item_link_link_id = item_link_link_ids[50 - (link_index_a - link_index_b) - 1]
                    playlist_watch_link = check_playlist_watch(item_link_link_id, playlist_id)
                    
                    if len(link_b) == 5:
                        link_b.pop(3)

                    link_b.insert(3, playlist_watch_link)
                    
            item_link_link_ids = []

    if len(item_link_link_ids) > 0:
        playlist_id_found = None
        error_found = False

        for link_index_b in range(link_index_a - len(item_link_link_ids) + 1, link_index_a + 1):
            link_b = links[link_index_b]

            if len(link_b) == 5:
                playlist_watch_link = link_b[3]
                playlist_id = playlist_watch_link.split("&list=")[1]
                
                if playlist_id_found is None:
                    playlist_id_found = playlist_id
                elif playlist_id != playlist_id_found:
                    error_found = True
            else:
                error_found = True
                
            if error_found is True:
                break
                
        if error_found is True:
            error_found = False

            playlist_id = create_playlist(item_link_link_ids)

            for link_index_b in range(link_index_a - len(item_link_link_ids) + 1, link_index_a + 1):
                link_b = links[link_index_b]

                item_link_link_id = item_link_link_ids[len(item_link_link_ids) - (link_index_a - link_index_b) - 1]
                playlist_watch_link = check_playlist_watch(item_link_link_id, playlist_id)
                
                if len(link_b) == 5:
                    link_b.pop(3)

                link_b.insert(3, playlist_watch_link)
                
            item_link_link_ids = []

    f = open(editted_file_path, "w")

    for link in links:
        f.write("\t".join(link))

    f.close()