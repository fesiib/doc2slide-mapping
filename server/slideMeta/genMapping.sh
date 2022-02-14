cnt=1

for q in ./*.mp4
do
    echo mv "$q" $cnt.mp4
    mv "$q" $cnt.mp4

    cnt=$((cnt+1))

    echo $cnt
done
