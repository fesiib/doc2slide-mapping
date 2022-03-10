import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { addBoundary, NO_LABEL, removeBoundary, setLabel } from "../reducers/annotationState";
import GenericButton from "./GenericButton";

export const WIDTH = 500;
export const HEIGHT = WIDTH * 9 / 16;

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

function LabelSelector(props) {
    const dispatch = useDispatch();

    const valueTitle = props?.valueTitle;
    const sectionTitles = props?.sectionTitles;
    const boundary = props?.boundary;

    const options = [NO_LABEL, "Title", ...sectionTitles, "End"];

    const curValue = options.findIndex((val) => val === valueTitle);

    const handleLabelChange = (event) => {
        const idx = event.target.value;
        dispatch(setLabel({
            label: options[idx],
            boundary: boundary,
        }));
    }
    return (<div>
        <select onChange={(event) => handleLabelChange(event)} value={curValue}>
            {
                options.map((val, idx) => {
                    return (<option key={"labelOption_" + idx} value={idx}>
                        {val}
                    </option>)
                })
            }
        </select>
    </div>);
}

function AnnotationTable(props) {
    const dispatch = useDispatch();

    const enableBoundaries = props?.enableBoundaries;
    const presentationId = props?.presentationId;
    const slideInfo = props?.slideInfo ? props.slideInfo : [];
    const sectionTitles = props?.sectionTitles ? props.sectionTitles : [];

    const { labels } = useSelector(state => state.annotationState);

    const endIdxs = [ ...Object.keys(labels).map((val) => parseInt(val)).sort((p1, p2) => p1 - p2)];

    const getNextEndIdx = (target_idx) => {
        const label_idx = endIdxs.find((value, idx) => {
            if (value > target_idx) {
                return true;
            }
            return false;
        })
        return label_idx;
    }

    const transitionButtonClickHandler = (idx) => {
        if (labels.hasOwnProperty(idx)) {
            dispatch(removeBoundary({ boundary: idx }));
        }
        else {
            dispatch(addBoundary({ boundary: idx }));
        }
    }
    const outputTable = () => {
        return slideInfo.map((slide, idx) => {
            if (idx === 0) {
                return null;
            } 
            const script = slide.script === "" ? "<EMPTY>" : slide.script;
            const nextEndIdx = getNextEndIdx(idx - 1);
            return (<div key={idx}>
                <div>
                    {
                        enableBoundaries ?
                        (
                            <div>

                                {
                                    idx > 1 ?      
                                    <GenericButton
                                        title={ labels.hasOwnProperty(idx - 1) ? "Remove Transition" : "Transition Here" }
                                        onClick={() => transitionButtonClickHandler(idx - 1)}
                                        color={ labels.hasOwnProperty(idx - 1) ? "red" : "green" }
                                    />
                                    :
                                    null
                                }
                                {
                                    (labels.hasOwnProperty(idx - 1) || idx === 1) ?
                                    <LabelSelector
                                        sectionTitles={sectionTitles}
                                        valueTitle={labels[nextEndIdx]}
                                        boundary={nextEndIdx}
                                    />
                                    :
                                    null
                                }  
                            </div>
                        )
                        :
                        null
                    }
                    <hr/>
                </div>
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
                <div>
                    <hr/>
                    {
                        enableBoundaries && false ?
                        (
                            <div>
                                {
                                    labels.hasOwnProperty(idx) ?
                                    <LabelSelector
                                        sectionTitles={sectionTitles}
                                        valueTitle={labels[idx]}
                                        boundary={idx}
                                    />
                                    :
                                    null
                                }
                            </div>
                        )
                        :
                        null
                    }
                    
                </div>
            </div>)
        })
    }

    return (<div>
        <h3> Table: Slides(left) - Scripts(right) </h3>
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