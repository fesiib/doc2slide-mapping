import pysrt
from datetime import datetime

subtitle = pysrt.open("subtitle.srt")

f = open("slideImages/frameTimestamp.txt", "r")

timestamp = []
subtitleResult = []

while True :
    line = f.readline()
    if not line :
        break

    timestamp.append([float(line.split('\t')[0]), float(line.split('\t')[1])])

f = open("slideImages/scriptData.txt", "w")

for i in range(len(timestamp)) :
    tmp = ''

    for j in range(len(subtitle)) :
        startTime = subtitle[j].start.to_time()
        dt_obj = ''

        if len(str(startTime).split('.')) > 1 :
            dt_obj = datetime.strptime(str(startTime),'%H:%M:%S.%f')
        else :
            dt_obj = datetime.strptime(str(startTime),'%H:%M:%S')

        a_timedelta = dt_obj - datetime(1900, 1, 1)

        curTime = a_timedelta.total_seconds()

        if timestamp[i][0] <= curTime and curTime <= timestamp[i][1] :
            tmp = tmp + ' ' + subtitle[j].text.strip().replace('\n', ' ').strip()

    subtitleResult.append(tmp)

    f.write(tmp)
    f.write('\n')

print(subtitleResult)
