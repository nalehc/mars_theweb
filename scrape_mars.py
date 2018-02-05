
#Dependencies
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from bs4 import BeautifulSoup
import pandas as pd
import requests
import pymongo
from flask import Flask, render_template


def scrape():
#News   
    url = 'https://mars.nasa.gov/news/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    result = soup.find('div', class_='content_title')
    title = result.a.text.strip()
    p_result = soup.find('div', class_='rollover_description_inner')
    p_text = p_result.text.strip()
#Image
    browser = Browser('chrome', headless=True)
    base_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(base_url)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    photo = soup.find('a', class_='button fancybox')
    photo_url = "https://www.jpl.nasa.gov/" + photo["data-fancybox-href"]
#Weather
    url = 'https://twitter.com/marswxreport?lang=en'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    result = soup.find('div', class_='js-tweet-text-container')
    weather = result.p.text.strip()
#Facts
    url = 'http://space-facts.com/mars/'
    tables = pd.read_html(url, header=0)
    facts = tables[0].to_html()
#Hemispheres
    hemisphere_image_urls = [
        {"title": "Valles Marineris Hemisphere", "img_url": "https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/valles_marineris_enhanced.tif/full.jpg"},
        {"title": "Cerberus Hemisphere", "img_url": "https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/cerberus_enhanced.tif/full.jpg"},
        {"title": "Schiaparelli Hemisphere", "img_url": "https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/schiaparelli_enhanced.tif/full.jpg"},
        {"title": "Syrtis Major Hemisphere", "img_url": "https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/syrtis_major_enhanced.tif/full.jpg"},
    ]
    mars_data = {
        "news": [title, p_text], "image": photo_url, "weather": weather, 
        "facts": str(facts), "hemispheres": hemisphere_image_urls
    }
    return mars_data

app = Flask(__name__)
conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)
mars_data = scrape()
db = client.marsDB
collection = db.mars_data
if collection.count() > 0:
    collection.drop()
collection.insert_one(mars_data)
mars_data =  list(db.mars_data.find())

@app.route("/")
def index():
    scrape()
    mars_data =  list(db.mars_data.find())
    return render_template("index.html", mars_data = mars_data[0])

@app.route("/references")
def reference():
    mars_data = list(db.mars_data.find())
    return render_template("reference.html", mars_data = mars_data[0])

if __name__ == "__main__":
    app.run(debug=True)
