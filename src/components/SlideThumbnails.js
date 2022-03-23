import React from 'react';

const WIDTH = 500;
const HEIGHT = WIDTH * 9 / 16;

const COLORS_LIST = [
    '#91aaff',
    '#ff9e9e',
    '#8aff9c',
    '#ff80c5',
    '#7afbff',
];

function SlideThumbnails(props) {
    const presentationId = props?.presentationId;
    const slideInfo = props?.slideInfo;

    const startIdx = props?.startIdx;
    const endIdx = props?.endIdx;

    const outline = props?.outline;
    const slidesSegmentation = props?.slidesSegmentation;

    const output = slideInfo?.map((slide, idx) => {
        if (startIdx && startIdx > idx) {
            return null;
        }
        if (endIdx && endIdx <= idx) {
            return null;
        }

        const thumbnailPath = `http://server.hyungyu.com:7777/images/${presentationId}/${slide.index}.jpg`;
        const title = "Script:\n\n" + slide.script + "\n\n\n\n\nOCR Result:\n\n" + slide.ocrResult;

        const startTime = new Date(0);
        startTime.setSeconds(slide.startTime);

        const endTime = new Date(0);
        endTime.setSeconds(slide.endTime);

        // Outline
        let curSectionTitleIdx = -1;
        let curSegementIdx = -1

        if (outline) {
            for (let i = 0; i < outline.length; i++) {
                if (outline[i].startSlideIndex <= idx && outline[i].endSlideIndex >= idx) {
                    curSectionTitleIdx = i;
                }
            }
        }
        if (slidesSegmentation) {
            for (let i = 0; i < slidesSegmentation.length; i++) {
                if (slidesSegmentation[i].startSlideIndex <= idx && slidesSegmentation[i].endSlideIndex >= idx) {
                    curSegementIdx = i;
                }
            }
        }

        return (
            <div key={idx} 
                style={{
                    backgroundColor: (curSectionTitleIdx < 0 ? null : COLORS_LIST[curSectionTitleIdx % COLORS_LIST.length])
                }}
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
                    <img src={thumbnailPath} title={title} alt={"slide"} style={{
                        width: WIDTH,
                        objectFit: 'cover',
                    }}/>
                </div>
                <div> 
                    ({ curSegementIdx < 0 ? null : slidesSegmentation[curSegementIdx].sectionTitle } ) {" "}
                    Page {idx} {" "}
                    ({startTime.getMinutes()}:{startTime.getSeconds()} - {endTime.getMinutes()}:{endTime.getSeconds()}) {" "}
                    {curSectionTitleIdx < 0 ? null : outline[curSectionTitleIdx].sectionTitle}
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