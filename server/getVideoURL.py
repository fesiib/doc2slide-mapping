import os
from pytube import Playlist, YouTube
import pandas as pd

DATA_FILENAME = "dataset_chi2021"
OUTPUT_SUBTITLES = "__subtitles/"

# def xml_caption_to_srt(self, xml_captions: str) -> str:
#     """Convert xml caption tracks to "SubRip Subtitle (srt)".

#     :param str xml_captions:
#     XML formatted caption tracks.
#     """
#     segments = []
#     root = ElementTree.fromstring(xml_captions)
#     i=0
#     for child in list(root.iter("body"))[0]:
#         if child.tag == 'p':
#             caption = ''
#             if len(list(child))==0:
#                 # instead of 'continue'
#                 caption = child.text
#             for s in list(child):
#                 if s.tag == 's':
#                     caption += ' ' + s.text
#             caption = unescape(caption.replace("\n", " ").replace("  ", " "),)
#             try:
#                 duration = float(child.attrib["d"])/1000.0
#             except KeyError:
#                 duration = 0.0
#             start = float(child.attrib["t"])/1000.0
#             end = start + duration
#             sequence_number = i + 1  # convert from 0-indexed to 1.
#             line = "{seq}\n{start} --> {end}\n{text}\n".format(
#                 seq=sequence_number,
#                 start=self.float_to_srt_time_format(start),
#                 end=self.float_to_srt_time_format(end),
#                 text=caption,
#             )
#             segments.append(line)
#             i += 1
#     return "\n".join(segments).strip()

try :
    df = pd.read_csv(DATA_FILENAME + ".csv")
except :
    df = pd.DataFrame(columns=['title', 'paper_file', 'video_file', 'subtitle_file', 'video_url', 'data_imported'])

print(df)
# p = Playlist('https://www.youtube.com/playlist?list=PLqhXYFYmZ-VfKka9TC5zKdvWeFf8AWc6s') # chi2019
# p = Playlist('https://www.youtube.com/playlist?list=PLqhXYFYmZ-VctgnS59-jZt13-yC4DXvGm') # chi2020 
p = Playlist('https://www.youtube.com/playlist?list=PLqhXYFYmZ-Vez20PWol8EVmJDmpr9DdPG') # chi2021
cnt = 0

print(len(p.video_urls))

os.makedirs(OUTPUT_SUBTITLES, exist_ok=True)

for url in p.video_urls:
    if cnt < len(df.index) :
        cnt = cnt + 1
        continue

    video = YouTube(url)
    caption = video.captions

    print(cnt)
    #print("Downloading video...")

    # if not os.path.isfile('./video/' + str(cnt) + '.mp4') :
    video_file = video.streams.get_highest_resolution().download("./video", filename=str(cnt) + '.mp4')

    print("Downloading caption ...")
    
    for c in caption :
        if c.code.startswith("en"):
            print(c.name)
            srt_caption = c.generate_srt_captions()
            
            caption_file = open(os.path.join(OUTPUT_SUBTITLES, str(cnt) + ".srt"), "w")
            caption_file.write(srt_caption)
            break

    df=df.append({
            'title' : video.title, 
            'paper_file': '',
            'video_file': str(cnt) + '.mp4',
            'subtitle_file': str(cnt) +".srt",
            'video_url': url,
            'data_imported': 'N'
            },
        ignore_index=True)

    cnt = cnt + 1

    df.to_csv(DATA_FILENAME + ".csv")

