import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { NO_LABEL, setLabel } from "../reducers/annotationState";
import AnnotationTable from "./AnnotationTable";
import GenericButton from "./GenericButton";
import Outline from "./Outline";
import SlideThumbnails from "./SlideThumbnails";

function AnnotationTask0(props) {
    const presentationId = props?.presentationId;
    const data = props?.data;
    return (<div>
        <AnnotationTable
            presentationId={presentationId}
            slideInfo={data?.slideInfo}
            enableBoundaries={false}
            sectionTitles={data?.sectionTitles}
        />
    </div>);
}

function AnnotationTask1(props) {
    const presentationId = props?.presentationId;
    const data = props?.data;

    return (<div>
        <AnnotationTable
            presentationId={presentationId}
            slideInfo={data?.slideInfo}
            enableBoundaries={true}
            sectionTitles={data?.sectionTitles}
        />
    </div>);
}


function AfterSubmission(props) {
    const presentationId = props?.presentationId;
    const data = props?.data;
    const outline = props?.outline;
    const formLink = props?.formLink;

    const { submissionId } = useSelector(state => state.annotationState);

    return (<div>
        <div>
            <h3> Your Submission Id <small> (copy-paste it to the form) </small>: </h3>
            <h4> {submissionId} </h4>
            <h3> <a href={formLink}> Please Fill out the Form </a> </h3>
        </div>
        <div>
            <Outline
                title="Annotation Summary"
                outline={outline}
                slideInfo={data?.slideInfo}
            />
        </div>
        <div>
            <SlideThumbnails 
                presentationId={presentationId}
                slideInfo={data?.slideInfo}
                startIdx={1}
                endIdx={data?.slideCnt}
            />
        </div>
    </div>);
}

function AnnotationTask2(props) {
    const dispatch = useDispatch();
    
    const { labels } = useSelector(state => state.annotationState);
    const [subStep, setSubStep] = useState(0);

    const presentationId = props?.presentationId;
    const data = props?.data;

    const endIdxs = [ ...Object.keys(labels).map((val) => parseInt(val)).sort((p1, p2) => p1 - p2)];

    const totalNumSteps = endIdxs.length;

    let startIdx = 1
    let endIdx = data?.slideInfo?.length - 1;

    if (subStep > 0 && subStep < endIdxs.length) {
        startIdx = endIdxs[subStep - 1] + 1;
    }
    if (subStep < endIdxs.length) {
        endIdx = endIdxs[subStep];
    }
    const handleLabelChange = (event) => {
        dispatch(setLabel({
            label: event.target.value,
            boundary: endIdx,
        }));
    }

    return (<div>
        {
            subStep === totalNumSteps ?
            <h4> Summary: You labeled {totalNumSteps} segments. </h4>
            :
            <h4> Segment {subStep + 1}: ({startIdx} - {endIdx}) </h4>
        }
        <div style={{
            display: "flex",
            justifyContent: "space-between",
            margin: "1em"
        }}>
            {
                subStep > 0 ? 
                <GenericButton
                    title={"<- Segment " + (subStep).toString()}
                    onClick={() => setSubStep(subStep - 1)}
                    color="brown"
                />
                :
                <div> </div>
            }
            {
                subStep < totalNumSteps - 1 ? 
                <GenericButton
                    title={" -> Segment " + (subStep + 2).toString()}
                    onClick={() => setSubStep(subStep + 1)}
                    color="brown"
                />
                :
                (
                    subStep === totalNumSteps - 1 ?
                    <GenericButton
                        title={" Summary "}
                        onClick={() => setSubStep(subStep + 1)}
                        color="darkGreen"
                    />
                    :
                    null
                )
            }
        </div>
        {
            subStep < totalNumSteps ?
            <div>
                <label htmlFor={"labelInput"}> Label: </label>
                <input
                    id={"labelInput"}
                    autoFocus={true}
                    type={"text"} 
                    onChange={handleLabelChange}
                    value={labels[endIdx] === NO_LABEL ? "" : labels[endIdx]}
                />
            </div>
            :
            null
        }
        <div>
            <SlideThumbnails 
                presentationId={presentationId}
                slideInfo={data?.slideInfo}
                startIdx={startIdx}
                endIdx={endIdx + 1}
            />
        </div>
    </div>);
}

export {
    AnnotationTask0,
    AnnotationTask1,
    AnnotationTask2,
    AfterSubmission,
};
