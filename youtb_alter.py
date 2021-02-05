"""Youtube video scrapper or downloader based on reversing youtube ,

i find only way of reversing youtube by embedding the youtube url , 
but there is drawback this script , this script can't download to those videos which can't be embedded.
you can see some video on youtube app are can't be save offline ,
i mean youtube change their url text into cipher text of those videos , cracking those is kind a difficult task
because they keep changing their algo. so this script can't download those videos😁 

i removed the unnessery headers and data call from script 
i am not sure whether it will still be working or not 
but now its working fine.
only used request library for get post request"""

import requests
import re
import subprocess

class YoutubeRev(object):

	__slots__ = ('videoId' , 'baseUrl', 'headers' , 'key' , 'payloadData' , 'jsonData' , 'filter' , 'title')

	def __init__(self , videoId):
		self.videoId = self.__urlFilter(videoId)
		self.baseUrl = "https://www.youtube.com/youtubei/v1/player"
		self.headers = {
		'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
		'content-type': 'application/json',
		'referer': 'https://www.youtube.com/embed/'+self.videoId
		}
		"""This api key was generated by broswer , i think its reusable
			this worked for me lol not sure whether it will for you or not xD""" 
		self.key = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
		self.payloadData = {
			"videoId":self.videoId,
			"context": {
			    "client": {
				    #I literally don't know what shit is this , i tried filtering out this but did't worked out so i leave it at it is
				    #I think its dynamic not sure though maybe worked out for you too :)
			      "visitorData": "CgtRQ1VwRWtZTm9YayiG3OCABg%3D%3D",
			      "clientName": "WEB_EMBEDDED_PLAYER", #Too fool google that this is just a embedded video xD
			      "clientVersion": "20210126",
			    },
			},

			"cpn": "79JIqSkI_5iSwavl" #Another shit leave it at it is 
		}
		self.jsonData = dict(self.__retriveJson())
		self.filter = dict(self.__filteredData())
		self.title = self.__title(self.jsonData["videoDetails"]['title'])

	def __retriveJson(self):
		res = requests.post(self.baseUrl , headers=self.headers , params={"key":self.key} , json=self.payloadData)
		if res.status_code != 200:
			raise Exception("Failed to retrive data , check url or this script is dead lol")
		else:
			return res.json()

	def __urlFilter(self , url):
		res = re.search(r"/(.+)=|/(.+)/", url)
		if res != None:
			n = res.span()[-1]
			return url[res.span()[-1]:]
		return url

	def __title(self , title):
		return re.sub('[^A-Za-z0-9]+', ' ', title)

	def __streamData(self):
		arr = [self.jsonData['streamingData']["adaptiveFormats"] , self.jsonData['streamingData']["formats"]]
		for data in arr:
			for obj in data:
				yield obj

	def __filteredData(self):
		junkFiltered = {
		"adaptiveVideos":[],
		"audios":[],
		"videos": self.jsonData['streamingData']['formats']
		}
		for obj in self.jsonData['streamingData']["adaptiveFormats"]:
			if "qualityLabel" in obj.keys():
				junkFiltered["adaptiveVideos"].append(obj)
			else:
				junkFiltered["audios"].append(obj)
		return junkFiltered

	def __getExtension(self , obj):
		extension_ = self.filter[""][0]["mimeType"]
		res = re.search(r"/(.+);", extension_)
		extension_ = res.group(1)

	def videoData(self):
		try:
			return self.jsonData['streamingData']
		except Exception:
			raise KeyError("Failed to retrive video is not downloadable")

	def videoInfo(self):
		try:
			return self.jsonData["videoDetails"]
		except Exception:
			raise KeyError("Failed to retrive ")

	def downloadParams(self , itag=None , audio=False):
		if itag != None:
			userObj = dict()
			for obj in self.__streamData():
				if int(obj["itag"]) == itag:
					userObj = obj
					break
			#Finding Extension

			extension_ = userObj["mimeType"]
			res = re.search(r"/(.+);", extension_)
			extension_ = res.group(1)
			print("[ Downloading Video File ]")
			vidUrl = userObj["url"]
			videoName = f"{self.title}.{extension_}"
			with open(f"{self.title}.{extension_}" , "wb") as v:
				vid = requests.get(vidUrl , stream=True)
				totalSize = int(vid.headers["Content-Length"])
				maxSize = totalSize//1024
				size = 0
				for vidContent in vid.iter_content(chunk_size=1024):
					size += len(vidContent)
					downloadedSize = (size/totalSize)*100
					v.write(vidContent)
					print("[ {:.2f}% downloaded of {} MB ]".format(round(downloadedSize, 2) , maxSize//1024) , end="\r")
				print("\n[ Video File Downloaded ]")
		if audio and itag > 50:
			"""Retriving highest quality audio"""
			audioObj = self.filter["audios"][0]
			audioUrl = audioObj["url"]

			extension_ = audioObj["mimeType"]
			res = re.search(r"/(.+);", extension_)
			extension_ = res.group(1)
			print("[ Downloading Audio File ]")
			audioName = f"{self.title}.{extension_}"
			with open(f"{self.title}.{extension_}" , "wb") as a:
				aud = requests.get(audioUrl , stream=True)
				totalSize = int(aud.headers["Content-Length"])
				maxSize = totalSize//1024
				size = 0
				for audContent in aud.iter_content(chunk_size=1024):
					size += len(audContent)
					downloadedSize = (size/totalSize)*100
					a.write(audContent)

					print("[ {:.2f}% downloaded of {}MB ]".format(round(downloadedSize, 2) , maxSize//1024) , end="\r")
				print("\n[ Audio File Downloaded ]")

		if itag != None and audio:
			"""Added ffmpeg feature for encoding"""
			try:
				print("[ Merging Audio And Video File ]")
				subprocess.run(["ffmpeg" , "-i" ,videoName, "-i" , audioName, "-c" , "copy" , self.title+".mkv"])
				# os.remove(videoName)
				# os.remove(audioName)
			except:
				raise Exception("ffmpeg error: check if ffmpeg is installed or not or is it on your path ?")

	def formatedViewer(self):
		adaptiveVideos = []
		audios = []
		videos = []
		for obj in self.filter["adaptiveVideos"]:
			temp = ["Video" , obj["itag"] , obj["qualityLabel"] , "False"]
			adaptiveVideos.append(temp)
			
		for obj in self.filter["audios"]:
			temp = ["Audio" , obj["itag"] ,obj["quality"] , "True" ]
			audios.append(temp)

		for obj in self.filter["videos"]:
			temp = ["Video" , obj["itag"] ,obj["qualityLabel"] , "True" ]
			videos.append(temp)

		#Writing data in tabular format
		print("Type     Itag     Quality  Audio")
		print("-"*32)
		for arr in adaptiveVideos+audios+videos:
			for data in arr:
				text = "{}{}".format(data , " "*9)
				print(text[:9] , end="")
			print()
			
			
#Instantiate an object by passing videoId of youtube video
# y1 = YoutubeRev("youtube_url")

#y1.videoData() #Return all the video json data
#y1.videoInfo() #Return all the video meta data such as title description 
#y1.jsonData() #Return all the json data without filtering and formatting

#This can filter the json data accoriding to your choice
#(y1.filter["adaptiveVideos"])#This contain video url of highest quality video but audio are absent
#(y1.filter["audios"])#This contain audio link of that video do note youtube Audio are in webm format you have to encode in mp3
#(y1.filter["videos"])#This contain link of that video in which both audio and video is available

#y1.formatViewer() return details in tabular format , there you can find itag quality 
#Added feature of downloading videos
#y1.download() #This will download that video which have both audio and video
#y1.downloadParams(itag=itag_value , audio=True/False) #This will download the file which itag is provided , audio is optional , True value download the highest available audio quality

#If both value are provided , script will download both file and merge in mkv using ffmpeg
#More Feature will be added later 


