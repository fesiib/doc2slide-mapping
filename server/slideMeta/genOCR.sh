mkdir slideImages/ocr/

cd slideImages/images/

for index in ./*.jpg
do
    echo $index

    python ../../ocr.py --image $index > ../ocr/$index.txt
done

cd ..
