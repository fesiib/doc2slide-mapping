import React from "react";
import GenericButton from "./GenericButton";

const WIDTH = 500;
const HEIGHT = WIDTH * 9 / 16;

function SingleSlideThumbnail(props) {
    const slide = props?.slide; // slideInfo element
    const idx = props?.idx; // key
    const presentationId = props?.presentationId; //presentationId

    const thumbnailsPath = '/slideData/' + presentationId + '/images/';
    const thumbnailPath = thumbnailsPath + slide.index.toString() + '.jpg';
    const title = "Script:\n\n" + slide.script + "\n\n\n\n\nOCR Result:\n\n" + slide.ocrResult;

    const startTime = new Date(0);
    startTime.setSeconds(slide.startTime);

    const endTime = new Date(0);
    endTime.setSeconds(slide.endTime);

    return (
        <div key={"thumbnail_" + idx.toString()}>
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
            <div style={{
                color: "gray",
                fontSize: "15px"
            }}> 
                Page {idx} {" "}
                ({startTime.getMinutes()}:{startTime.getSeconds()} - {endTime.getMinutes()}:{endTime.getSeconds()})
            </div>	
        </div>
    )
}

function AnnotationTable(props) {
    const enableBoundaries = props?.enableBoundaries;
    const presentationId = props?.presentationId;
    const slideInfo = props?.slideInfo;

    const outputTable = () => {
        if (!slideInfo) {
            return [];
        }
        return slideInfo.map((slide, idx) => {
            if (idx === 0) {
                return null;
            } 
            const script = slide.script === "" ? "<EMPTY>" : slide.script;
            return (<div key={idx}>
                <hr/>
                <div style={{
                    display: "flex",
                    flexDirection: "row",
                    textAlign: "left",
                    margin: 20,
                }}>
                    <div key={"thumbnail"} style={{
                        width: "50%",
                    }}>
                        <SingleSlideThumbnail presentationId={presentationId} slide={slide} idx={idx}/>
                    </div>
                    
                    <div key={"script"} style={{
                        width: "50%",
                    }}>
                        <div key={"script_" + idx.toString()} style={{
                            display:  "block",
                            gap: 10,
                            margin: 10,
                        }}>
                            <div>
                                {script}
                            </div>
                        </div>
                    </div>
                </div>
                {
                    (enableBoundaries && idx < slideInfo.length - 1) ?
                    (
                        <div>
                            <hr/>
                            <GenericButton
                                title={"Transition Here"}
                            />
                        </div>
                    )
                    :
                    null
                }
            </div>)
        })
    }

    return (<div>
        <h2> Table: Slides(left) - Scripts(right) </h2>
        <div style={{
            display: "flex",
            flexDirection: "column",
            margin: "1em",
        }}> 
            {outputTable()}
        </div>
    </div>)
}

export default AnnotationTable;