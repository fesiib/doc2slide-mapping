import React, { useEffect, useState } from "react";
import axios from "axios";

import { useDispatch, useSelector } from "react-redux";
import { resetApp } from "../reducers";
import { NO_LABEL, setLabel, setStep } from "../reducers/annotationState";

import AnnotationTable from "../components/AnnotationTable";
import GenericButton from "../components/GenericButton";
import SlideThumbnails from "../components/SlideThumbnails";
import Outline from "../components/Outline";

const INTRO = 0;
const WARM_UP = 1;
const TASK_1 = 2;
const TASK_2 = 3;
const TASK_3 = 4;
const SUBMITTED = 5;

function WarmUp(props) {
    const presentationId = props?.presentationId;
    const data = props?.data;
    return (<div>
        <AnnotationTable
            presentationId={presentationId}
            slideInfo={data?.slideInfo}
            enableBoundaries={false}
        />
    </div>);
}

function Task1(props) {
    const presentationId = props?.presentationId;
    const data = props?.data;

    const { labels } = useSelector(state => state.annotationState);

    const printTransitionBoundaries = () => {
        let strTransitions = "";
        let firstTransition = true;
        for (let key in labels) {
            if (key <= 1) {
                continue;
            }
            if (!firstTransition) { 
                strTransitions += ", ";
            }
            strTransitions += key;
            firstTransition = false;
        }

        if (firstTransition) {
            strTransitions = "Please Select Transitions";
        }
        return " " + strTransitions;
    }

    return (<div>

        <div style={{
            fontSize: "20px",
            padding: "1em",
        }}>
            <i>
                Selected Transitions: 
            </i>
            <pre> 
                {printTransitionBoundaries()}
            </pre>
        </div>

        <AnnotationTable
            presentationId={presentationId}
            slideInfo={data?.slideInfo}
            enableBoundaries={true}
        />
    </div>);
}

function Task2(props) {
    const dispatch = useDispatch();

    const presentationId = props?.presentationId;
    const data = props?.data;

    const { labels } = useSelector(state => state.annotationState);

    const startIdxs = Object.keys(labels).map((val) => parseInt(val)).sort((p1, p2) => p1 - p2);

    const totalNumSteps = startIdxs.length;

    const [subStep, setSubStep] = useState(0);

    let startIdx = 1
    let endIdx = data?.slideInfo?.length;

    if (subStep < startIdxs.length) {
        startIdx = startIdxs[subStep];
    }
    if (subStep < startIdxs.length - 1) {
        endIdx = startIdxs[subStep + 1];
    }

    const generateOutline = () => {
        let outline = [];

        for (let i = 0; i < startIdxs.length; i++) {
            const start = startIdxs[i];
            const end = i + 1 < startIdxs.length ? startIdxs[i + 1] - 1 : data?.slideInfo?.length - 1;
            outline.push({
                sectionTitle: labels[start],
                startSlideIndex: start,
                endSlideIndex: end,
            });
        }

        return outline;
    }

    const handleLabelChange = (event) => {
        dispatch(setLabel({
            label: event.target.value,
            boundary: startIdx,
        }));
    }

    return (<div>
        {
            subStep === totalNumSteps ?
            <h4> Summary: You annotated {totalNumSteps} segments </h4>
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
            subStep === totalNumSteps ?
            <div>
                <Outline
                    isGenerated={false}
                    outline={generateOutline()}
                    slideInfo={data?.slideInfo}
                />
            </div>
            :
            <div>
                <label htmlFor={"labelInput"}> Label: </label>
                <input
                    id={"labelInput"}
                    autoFocus={true}
                    type={"text"} 
                    onChange={handleLabelChange}
                    value={labels[startIdx] === NO_LABEL ? "" : labels[startIdx]}
                />
            </div>
        }
        <div>
            <SlideThumbnails 
                presentationId={presentationId}
                slideInfo={data?.slideInfo}
                startIdx={startIdx}
                endIdx={endIdx}
            />
        </div>
    </div>)

}

function Introduction(props) {
    const step = props?.step;

    const stepTitle = (step) => {
        switch (step) {
            case WARM_UP:
                return "Currently in " + "Warm-up";
            case TASK_1:
                    return "Currently in " + "Task 1";
            case TASK_2:
                return "Currently in " + "Task 2";
            case TASK_3:
                return "Currently in " + "Task 3";
            case SUBMITTED:
                return "Your work is recorded! Thank You for Participation!"
            default:
                return null;
        }
    }

    return (<div>
        <div style={{
            "textAlign": "left",
            "margin": "2em",
            "padding": "1em",
            "background": "lightgray"
        }}>
            <h3> Motivation: </h3>
            <p> Project  </p>
        </div>
        
        <div style={{
            "textAlign": "left",
            "margin": "2em",
            "padding": "1em",
            "background": "lightgray"
        }}>
            <h3> Instructions: </h3>
            <ol start={0}>
                {step === WARM_UP ? 
                    <li> <b>  {" -> "} Warm-up: </b> Scim through slides & scripts to general sense of the presentation</li>
                    :
                    <li> Warm-up: Scim through slides & scripts to general sense of the presentation</li>
                }
                <ul> 
                    <li>
                        You can watch the entire presentation video here:{" "}
                        <a href={"https://www.youtube.com/watch?v=oFRiEZO_5Dk,N"}>Youtube ~15 mins </a>
                        <i>(but just skimming slides & scripts should be faster)</i>
                    </li>
                </ul>

                {step === TASK_1 ?
                    <li> <b> {" -> "} Task: </b> Detect main section transitions in slides </li>
                    :
                    <li> Task: Detect main section transitions in slides </li>
                }
                {step === TASK_2 ? 
                    <li> <b> {" -> "} Task: </b> Label produced segments of slides with an appropriate label </li>
                    :
                    <li> Task: Label produced segments of slides with an appropriate label </li>
                }
                {step === TASK_3 ?
                    <li> <b> {" -> "} Task: </b> Bonus </li>
                    :
                    <li> Task: Bonus </li>
                }
            </ol>
        </div>
        <div style={{
            margin: "1em"
        }}>
            <h2> {stepTitle(step)} </h2>
        </div>
    </div>);
}

function Annotation(props) {
    const dispatch = useDispatch();
    
    const presentationId = props?.presentationId;
    const { step } = useSelector(state => state.annotationState);

    const [data, setData] = useState([]);

    useEffect(() => {
		axios.post('http://localhost:7777/mapping/presentation_data', {
			presentationId: presentationId,
		}).then( (response) => {
			console.log(response);
			setData(response.data.data);
		});

	}, [presentationId]);

    const _setStep = (new_step) => {
        window.scrollTo(0, 0);
        dispatch(setStep({ step: new_step }));
    }

    const outputMainSection = () => {
        switch(step) {
            case INTRO:
                return (<div>
                    <GenericButton
                        title={"Start Warm-up!"}
                        onClick={() => _setStep(WARM_UP)}
                    />
                </div>);
            
            case WARM_UP:
                return (<div>
                    <WarmUp presentationId={presentationId}  data={data}/>

                    <GenericButton
                        title={"Start Task 1"}
                        onClick={() => _setStep(TASK_1)}
                    />
                </div>);
            
            case TASK_1:
                return (<div>
                    <Task1 presentationId={presentationId}  data={data}/>
                    <GenericButton
                        title={"Start Task 2"}
                        onClick={() => _setStep(TASK_2)}
                    />
                </div>);
            case TASK_2:
                return (<div>
                    <Task2 presentationId={presentationId}  data={data}/>
                    <GenericButton
                        title={"Start Task 3"}
                        onClick={() => _setStep(TASK_3)}
                    />
                </div>);
            case TASK_3:
                return (<div>
                    <GenericButton
                        title={"Finish & Submit"}
                        onClick={() => _setStep(SUBMITTED)}
                    />
                </div>);
            default:
                return <div>
                    <GenericButton
                        title={"Restart"}
                        onClick={() => dispatch(resetApp())}
                    />
                </div>
        }
    }

    return (<div>
        <h2> Ground Truth Construction for Presentation Outlines</h2>
        <Introduction step={step} />
        <div style={{
            display: "flex",
            justifyContent: "space-between",
            margin: "1em"
        }}>
            {
                step >= TASK_1 ? 
                <GenericButton
                    title={"<- Previous Task"}
                    onClick={() => _setStep(step - 1)}
                    color="black"
                />
                :
                <div> </div>
            }
            {
                step < SUBMITTED ? 
                <GenericButton
                    title={"Next Task ->"}
                    onClick={() => _setStep(step + 1)}
                    color="black"
                />
                :
                null
            }
        </div>
        {outputMainSection()}
    </div>)
}

export default Annotation;