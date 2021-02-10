from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
import re
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from datetime import date
import sys
import re
import os
import yaml

team_name_map = { 
                "Men's 1s": "Men's 1s",
                "Men's 2s": "Men's 2s",
                "Men's 3s": "Men's 3s",
                "Ladies 1st XI": "Ladies 1s",
                "Ladies 2nd XI": "Ladies 2s",
                "Mixed 1s": "Mixed" 
                }



def set_chrome_options() -> None:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    print("Setting chrome options")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--incognito')
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options


def get_table(driver):
    url = "https://w.fixtureslive.com/club/826/whats-on/Chertsey-Thames-Valley"
    print("Getting driver for url - {}".format(url))

    driver.get(url)
    page_source = driver.page_source

    fl_layout_body = driver.find_element_by_class_name("fl_layout_body")
    table_src = fl_layout_body.get_attribute('innerHTML')

    print("Getting BS4 for page")
    soup = BeautifulSoup(table_src, 'lxml')
    table = soup.table
    table_rows = table.find_all('tr')

    return table_rows


def get_data(table, teams=None):
    games = dict()
    for tr in table:
        row = [ i.text for i in tr.find_all('td')]

        # If the row is too short ignore 
        if len(row) < 3: 
            continue

        # If fixture type and the 6th row is empty (\xa0) meaning no game played yet 
        if image_type == 'fixtures' and row[5]=='\xa0':

            # If the 6th column is not empty (\xa0) meaning result not in yet, ignore
            #if row[5] != '\xa0':
            #    continue

            # Get the meaningful data
            # 0 = Time
            # 1 = Home or Away
            # 4 = Team (e.g. Mens 2s)
            # 7 = Opposition
            inf = list(row[i] for i in [0, 1, 4, 7])

            # Only use teams playing this week
            if inf[2] not in teams or inf[2] not in team_name_map.keys():
                continue

            # Put the data into a dictionary
            k = dict()
            k['time'] = inf[0]
            k['home_away'] = inf[1][0]
            k['team'] = team_name_map[inf[2]]
            k['opposition'] = re.split(' Men| Ladi',inf[3])[0]

        # If result type and 6th row is not empty (\xa0) meaning there is a result
        elif image_type == 'results' and row[5] != '\xa0':

            # Get the meaningful data
            # 4 = Team (e.g. Mens 2s)
            # 5 = Result 
            # 7 = Opposition
            inf = list(row[i] for i in [4, 5, 7])

            # Ignore colts teams
            if inf[0] not in team_name_map.keys():
                continue

            k = dict()
            k['team'] = team_name_map[inf[0]]
            k['score'] = inf[1]
            k['opposition'] = re.split(' Men| Ladi',inf[2])[0]
        else:
            # Else loop to next row in table
            continue

        # Ignore where there is multiple games for one team
        if k['team'] in games:
            continue

        # Add the data to the list of games
        games[k['team']] = k

    return games

def order_data(data):
    list_order = [ "Men's 1s",
                   "Men's 2s",
                   "Men's 3s",
                   "Ladies 1s",
                   "Ladies 2s",
                   "Mixed" 
                 ]
    # Order the games based on the list
    a = []
    for k in list_order:
        if k in data:
            a.append(data[k])
    return a


def make_image(data, image_type):

    # Set variables
    valid = False
    W = H = 1080
    max_width = W - 80
    font_size = 120
    margin = 30
    top_of_text = H / 2
    text_color = (255, 255, 255)
    font_loc = "./fonts/AppleSymbols.ttf"

    # Create a new folder to save the images to
    today = date.today()
    dir_name = '/output/{}'.format(today.strftime("%d-%m-%y"))
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    
    # Remove the Mens / Ladies part of the opposition Team to only leave the club
    for r in data:
        r['opposition'] = re.split(' Men| Ladi', r['opposition'])[0]

    # Create Column like strings of text
    ctvhc_teams = '\n'.join([r['team'] for r in data])
    opposition = '\n'.join([r['opposition'] for r in data])
    dashes = '\n'.join('-' for _ in data)
    if image_type == 'fixtures':
        time = '\n'.join([r['time'] for r in data])
        home_away = '\n'.join([r['home_away'] for r in data])
    else:
        scores = '\n'.join([r['score'] for r in results])

    # If a template env variable is set only use this template
    # Else render all so the user can pick
    templates = [ os.getenv('TEMPLATE') ]
    if not templates:
        templates = os.listdir('./templates')

    print("Creating {} image for templates: {}".format(image_type, templates))

    for filename in templates:
        print("Creating image - {}".format(filename))

        if not (filename.endswith(".png") or filename.endswith(".jpg")):
            print("File {} not an image, ignoring".format(filename))
            continue
    
        in_file = 'templates/{}'.format(filename) #1080 by 1080
        out_file = '{}/{}'.format(dir_name, filename)

        # Create the image object from the file
        img = Image.open(in_file)
        draw = ImageDraw.Draw(img)

        # Work out the largest possible font size possible with the data
        # So that the text does not exceed the value set in the max_wodht variable
        while not valid:
            font = ImageFont.truetype(font_loc, font_size)

            if image_type == 'fixtures':
                # All heightd are the same, not worried about that
                time_width, height = draw.textsize(time, font=font) 
                home_away_width, height = draw.textsize(home_away, font=font)
                dash_width, height = draw.textsize(dashes, font=font)
                teams_width, height = draw.textsize(ctvhc_teams, font=font)
                opposition_width, height = draw.textsize(opposition, font=font)
                total = sum([time_width, home_away_width, dash_width, teams_width, opposition_width])
            else:
                teams_width, th = draw.textsize(ctvhc_teams, font=font)
                scores_width, sh = draw.textsize(scores, font=font)
                opposition_width, ph = draw.textsize(opposition, font=font)
                total = sum([teams_width, scores_width, opposition_width])

            if total < max_width:
                valid = True
            else:
                font_size -= 1

        # Sets a 50 pixel margin at the bottom of the page
        top = (H-height)-50

        # Otg width = On the go width
        # Calculate the width as each text column is added, starting with a 20 pixel margin on the left
        otg_width = 20

        if image_type == 'fixtures':
            # Add the Home / Away Text
            draw.text((otg_width, top), home_away, text_color, font=font, align='right')
            # Update OTG width with a margin of 2 px
            otg_width += (home_away_width + 2)
            # Add a dashes column
            draw.text((otg_width, top), dashes, text_color, font=font)
            otg_width += (dash_width + 2)
            # Add the fixture time columm
            draw.text((otg_width, top), time, text_color, font=font)
            otg_width += (time_width + 20)
            # Add the team column
            draw.text((otg_width, top), ctvhc_teams, text_color, font=font, align='right')
            otg_width += (teams_width + 2)
            # Add a dashes column
            draw.text((otg_width, top), dashes, text_color, font=font)
            otg_width += (dash_width + 2)
            # Add the opposition column
            draw.text((otg_width, top), opposition, text_color, font=font)
        else:
            # Add team column
            draw.text((otg_width, top), ctvhc_teams, text_color, font=font, align='right')
            otg_width += (teams_width + 20)
            # Add Scores Column
            draw.text((otg_width, top), scores, text_color, font=font)
            otg_width += (scores_width + 20)
            # Add opposition column
            draw.text((otg_width, top), opposition, text_color, font=font)

        # Save the image
        img.save(out_file)

def this_week_teams(path='/teams.yml'):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        teams = yaml.load(f, Loader=yaml.FullLoader)
    return teams['teams']

if __name__ == "__main__":

    # Set the chrome options
    chrome_options = set_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)
    
    # Get Environment variables
    # Fixtures or results
    image_type = os.getenv('TYPE')
    if not image_type or image_type not in ['fixtures', 'results']:
        print("The TYPE environment variable must be set to one of [ fixtures, results ]")
        raise SystemExit

    # Get a list of the teams playing this week
    # Mounted to the dockerfile manually, find a way to automate with dates
    this_week_teams = this_week_teams()

    table = get_table(driver)
    games = get_data(table, this_week_teams)
    data = order_data(games)
    make_image(data, image_type)
