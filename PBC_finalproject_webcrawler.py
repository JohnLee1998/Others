#透過Python取得streetvoice排行資料
#使用requests套件的requests.get()方法
import requests
from bs4 import BeautifulSoup
from lxml import etree
import re
# from selenium import webdriver
# import time
import pandas as pd


u_list = []
for i in range(8):
	u = 'https://streetvoice.com/music/charts/' + str(i) + '/'
	u_list.append(u)
url_24hr = 'https://streetvoice.com/music/charts/24hr/'



def get_html(url):
	#模擬訪問頁面的函數
	try:
		user_agent = 'Mozilla/5.0'
		resp = requests.get(url, headers={'User-Agent': user_agent}, timeout = 30) #回傳為一個request.Response的物件
		resp.endcodding = 'utf8'
		response = resp.content.decode()
		return response 
	except:
		return 'ERROR'

#print(resp.status_code)
#物件的statu_code屬性取得server回覆的狀態碼(200表示正常,404表示找不到網頁,之前一直503???)
#print(resp.text)

def get_url(url):
	#函數用來找出單一網頁的歌手連結
	html = get_html(url)
	singers = []
	tree = etree.HTML(html)
	#result = etree.tostring(tree, pretty_print = True, method = "html")
	for i in tree.xpath('//*[@id="item_box_list"]/table/tbody/tr/td[2]/a'):
		singer = i.xpath('string(.)')
		singer_url = i.xpath('@href')
		for i in singer_url:#處理莫名的[]
			singers.append(i)
	return singers

def singer_list(num):
	#爬取2018所有類型排行榜上所有不重複的歌手連結
	url_list = []
	singer_set = set()
	for j in u_list:
		for i in range(num):
			url = j + '2018/' + str(i+1) + '/'
			k = set(get_url(url)) #各週的排行榜不重複歌手連結
			singer_set.update(k) 
		#print(singer_set)檢查正確
	singer_set = list(singer_set)
	singer_list = []
	for eachsinger in singer_set: #把前面爬的變成網址形式
		eachsinger = 'https://streetvoice.com' + eachsinger + 'songs/'
		singer_list.append(eachsinger)
	return singer_list

def get_content(url):
	#函數用來取得想要的數據
	html = get_html(url)
	tree = etree.HTML(html)
	count_songs = 0
	songs_like_list = []
	new_like_list = []
	#每個歌手的名字
	#//*[@id="inside_box"]/div[2]/div[1]/div/div[2]/div[1]/div[1]/h1
	singer_name = tree.xpath('//*[@id="inside_box"]/div[2]/div[1]/div/div[2]/div[1]/div[1]/h1/text()')[0]

	#把每個歌手每首歌的like數找出來相加
	for i in tree.xpath('//*[@id="item_box_list"]/div/div[2]/div/button/text()'):
		eachsong_like = i.strip()#但這裡會有空的被append進去
		if eachsong_like == '':
			continue
		songs_like_list.append((eachsong_like))
		count_songs += 1
	
	for i in range(len(songs_like_list)):#處理文字是幾k的問題
		if songs_like_list[i][-1] == 'k':
			new_like_list.append(float(songs_like_list[i][:-1]) * 1000)
		else:
			new_like_list.append(float(songs_like_list[i]))
	total_like = int(sum(new_like_list)) #完成相加

	#//*[@id="countup-follower"]
	#//*[@id="inside_box"]/div[2]/div[1]/div/div[2]/div[3]/div[1]/ul/li[2]/
	#//*[@id="inside_box"]/div[2]/div[1]/div/div[2]/div[3]/div[1]/ul/li[2]
	singer_follower = tree.xpath('//*[@id="pjax-container"]/script/text()')[0].strip() #返回list
	all_imformation = re.findall("\d+", singer_follower)
	singer_follower_count = int(all_imformation[1])
	count_songs = int(all_imformation[0])


	try:
		#找出歌手網頁中第一首歌的網址，訪問且拿到發布日期
		page = (count_songs//24) + 1
		num = (count_songs % 24)
		if num == 0:
			page -= 1
			num = 24
		path = '//*[@id="item_box_list"]/div[' + str(num) + ']/div[2]/h4/a'
		singer_song_url = url + '?page=' + str(page)
		singer_song_html = get_html(singer_song_url)
		singer_song_tree = etree.HTML(singer_song_html)
		for i in singer_song_tree.xpath(path):
			first_song_partial_url1 = i.xpath('@href') #用完xpath出來的都是list,要變str
		first_song_partial_url = first_song_partial_url1[0]
		first_song_url =  'https://streetvoice.com' + first_song_partial_url
		

		
		#拿到url，開始訪問並拿發布日期
		first_song_html = get_html(first_song_url)
		first_song_tree = etree.HTML(first_song_html)
		count_tr = 0
		for i in first_song_tree.xpath('//*[@id="inside_box"]/div[1]/div/div/div/div/div[2]/table/tbody/tr/td'):
			count_tr += 1 #檢查count_tr沒錯
		path1 = '//*[@id="inside_box"]/div[1]/div/div/div/div/div[2]/table/tbody/tr[' + str(count_tr) + ']/td/text()'
		first_song_date1 = first_song_tree.xpath(path1)
		#//*[@id="inside_box"]/div[1]/div/div/div/div/div[2]/table/tbody/tr[2]/td
		#上面的date在一個list裡面，要取出來
		first_song_date = str()
		for i in first_song_date1:
			first_song_date += i
	except:
		first_song_date = 'ERROR'
	return [singer_name, str(singer_follower_count), str(count_songs), str(total_like), str(first_song_date)]
	
	
num = 1 #這裡表示要爬取到2018開始的第幾週
singer_list = singer_list(num)
output = []
for url in singer_list:
    solution = get_content(url)
    output.append(solution)
    print(solution)
# 轉成csv
column_name = ['Name', 'Followers', 'Songs', 'Total_like', 'First_song_date']
test = pd.DataFrame(columns = column_name, data = output)
test.to_csv('/Users/tu/Desktop/result.csv', encoding = 'utf_8_sig') # encoding解決亂碼問題，前面自己設路徑






