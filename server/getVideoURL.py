import os
from pytube import Playlist, YouTube
import pandas as pd

try :
	df = pd.read_csv("__data.csv")
except :
	df = pd.DataFrame(columns=['title', 'paper_file', 'video_file', 'subtitle_file', 'video_url', 'data_imported'])

print(df)
p = Playlist('https://www.youtube.com/playlist?list=PLqhXYFYmZ-VfKka9TC5zKdvWeFf8AWc6s')
cnt = 0

for url in p.video_urls:
	if cnt < len(df.index) :
		cnt = cnt + 1
		continue

	video = YouTube(url)
	caption = video.captions

	print(cnt)
	print("Downloading video...")

	try :
		if not os.path.isfile('./video/' + str(cnt) + '.mp4') :
			video_file = video.streams.get_highest_resolution().download("./video", filename=str(cnt) + '.mp4')
	except :
		break

	print("Downloading caption ...")

	for c in caption :
		if c.name == "English - Default" :
			srt_caption = c.generate_srt_captions()
			
			caption_file = open("__subtitles/" + str(cnt) + ".srt", "w")
			caption_file.write(srt_caption)

			break

	df=df.append({
			'title' : video.title, 
			'paper_file': '',
			'video_file': "./video/" + str(cnt) + '.mp4',
			'subtitle_file': "./__subtitles/" + str(cnt) +".srt",
			'video_url': url,
			'data_imported': 'N'
			},
		ignore_index=True)

	cnt = cnt + 1

	df.to_csv('__data.csv')

