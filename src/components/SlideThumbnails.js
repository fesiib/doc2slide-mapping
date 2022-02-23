import React from 'react';

const WIDTH = 500;
const HEIGHT = WIDTH * 9 / 16;

function SlideThumbnails(props) {
    const presentationId = props?.presentationId;
    const slideInfo = props?.slideInfo;

    const thumbnailsPath = '/slideData/' + presentationId + '/images/';
    const output = slideInfo?.map((slide, idx) => {
        const thumbnailPath = thumbnailsPath + slide.index.toString() + '.jpg';
        const title = "Script:\n\n" + slide.script + "\n\n\n\n\nOCR Result:\n\n" + slide.ocrResult;

        const startTime = new Date(0);
        startTime.setSeconds(slide.startTime);

        const endTime = new Date(0);
        endTime.setSeconds(slide.endTime);

        return (
            <div key={idx} 
            >
                <div style={{
                    overflow: "hidden",
                    width: WIDTH,
                    height: HEIGHT,
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                    marginRight: 5,
                }}>
                    <img src={thumbnailPath} title={title} style={{
                        width: WIDTH,
                        objectFit: 'cover',
                    }}/>
                </div>
                <div> 
                    {idx} {" "}
                    ({startTime.getMinutes()}:{startTime.getSeconds()} - {endTime.getMinutes()}:{endTime.getSeconds()})
                </div>	
            </div>
        )
    });
    return (<div style={{
        display: "flex",
        flexWrap: "nowrap",
        overflowX: "scroll",
        margin: 20,
    }}>
        {output}
    </div>);
}

export default SlideThumbnails;