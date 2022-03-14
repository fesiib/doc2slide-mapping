import pytube 

urls = []

for i in range(211) :
    x = input()
    urls.append(x)

print(urls)

for i in range(len(urls)) :
    if i < 7 :
        continue
    
    successFlag = False

    while True :
        try :
            video = pytube.YouTube(urls[i]).streams.get_highest_resolution()

            video.download('./videos')

            successFlag = True
        except :
            successFlag = False

        if successFlag :
            break

    print(i)
    
