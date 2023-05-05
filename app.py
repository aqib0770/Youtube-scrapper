from flask import Flask,render_template,jsonify,request
from flask_cors import CORS,cross_origin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import logging
import csv
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

app=Flask(__name__,template_folder='template')
@cross_origin
@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")
@cross_origin
@app.route('/review',methods=['POST','GET'])
def scrap():
    searchString = request.form['content'].replace(" ","")
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(f'https://www.youtube.com/@{searchString}/videos')
    body=driver.find_element(By.TAG_NAME,'body')
    for i in range(20):
        body.send_keys(Keys.PAGE_DOWN)
    video_links=driver.find_elements(By.CSS_SELECTOR,'a[href*="/watch?v="]')
    video_title=driver.find_elements(By.CSS_SELECTOR,'a[id*="video-title-link"]')
    thumbnail_elements = driver.find_elements(By.XPATH, '//a[@id="thumbnail"]//yt-image//img')
    video_views=driver.find_elements(By.XPATH,'//*[@id="metadata-line"]/span[1]')
    video_time = driver.find_elements(By.XPATH,'//*[@id="metadata-line"]/span[2]')

    links=[]
    titles=[]
    views=[]
    time=[]
    thumbnails=[]
    for i in video_links:
        #extracting links
        href=i.get_attribute('href')
        links.append(href)
    for i in video_title:
        #extracting titles
        id=i.get_attribute('title')
        titles.append(id)
    for i in video_views:
        #extracting views
        view=i.text
        if 'views' in view:
            views.append(view)
        #extracting time
    for i in video_time:
        times=i.text
        if 'ago' in times:
            time.append(times)
    for i in thumbnail_elements:
        src=i.get_attribute('src')
        thumbnails.append(src)
        
    driver.quit()
    main_list=[]
    for i,j,k,l,m in zip(titles,links,thumbnails,views,time):
        mydict={"title":i,"links":j,"thumbnails":k,"views":l,"time":m}
        main_list.append(mydict)
    logging.info("Successfully executed")

    with open(f'{searchString}.csv','w',encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Link', 'Thumbnail', 'Views', 'Time'])
        for i, j, k, l, m in zip(titles, links, thumbnails, views, time):
            writer.writerow([i, j, k, l, m])
    
    return render_template('result.html',main_list=main_list)
if __name__=='__main__':
    app.run(host="0.0.0.0")
