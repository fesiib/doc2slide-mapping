import React, { useEffect, useState } from "react";
import axios from "axios";
import '../App.css';

import { useDispatch, useSelector } from "react-redux";
import { resetApp } from "../reducers";
import { addBoundary, NO_LABEL, setLabel, setPresentationid, setStep } from "../reducers/annotationState";

import AnnotationTable from "../components/AnnotationTable";
import GenericButton from "../components/GenericButton";
import SlideThumbnails from "../components/SlideThumbnails";
import Outline from "../components/Outline";

const INTRO = 0;
const WARM_UP = 1;
const TASK_1 = 2;
const TASK_2 = 3;
const TASK_3 = 44;
const SUBMITTED = 4;

const GOOGLE_FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSfMRNceok4P5pLvu9ofROTUcFr_AKYPBzv6lKu8CX3qBP3B9g/viewform?usp=sf_link"

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
            if (key <= 1 || key >= data?.slideInfo?.length - 1) {
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

    const { labels, submissionId } = useSelector(state => state.annotationState);

    const endIdxs = [ ...Object.keys(labels).map((val) => parseInt(val)).sort((p1, p2) => p1 - p2)];

    const totalNumSteps = endIdxs.length;

    const [subStep, setSubStep] = useState(0);

    let startIdx = 1
    let endIdx = data?.slideInfo?.length - 1;

    if (subStep > 0 && subStep < endIdxs.length) {
        startIdx = endIdxs[subStep - 1] + 1;
    }
    if (subStep < endIdxs.length) {
        endIdx = endIdxs[subStep];
    }

    const generateOutline = () => {
        let outline = [];

        for (let i = 0; i < endIdxs.length; i++) {
            const start = i > 0 ? endIdxs[i - 1] + 1 : 1;
            const end = endIdxs[i];
            outline.push({
                sectionTitle: labels[end],
                startSlideIndex: start,
                endSlideIndex: end,
            });
        }

        return outline;
    }

    const handleLabelChange = (event) => {
        dispatch(setLabel({
            label: event.target.value,
            boundary: endIdx,
        }));
    }

    const submitAnnotation = () => {
        axios.post('http://server.hyungyu.com:7777/annotation/submit_annotation', {
			presentationId: presentationId,
            submissionId: submissionId,
            outline: generateOutline(),
		}).then( (response) => {
			console.log(response);
		});
    };

    const _setStep = (new_step) => {
        window.scrollTo(0, 0);
        dispatch(setStep({ step: new_step }));
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
                    value={labels[endIdx] === NO_LABEL ? "" : labels[endIdx]}
                />
            </div>
        }
        <div>
            <SlideThumbnails 
                presentationId={presentationId}
                slideInfo={data?.slideInfo}
                startIdx={startIdx}
                endIdx={endIdx + 1}
            />
        </div>
        {
            subStep === totalNumSteps ?
            <div>
                <GenericButton
                    title={"Finish & Submit"}
                    onClick={() => {
                        submitAnnotation();
                        _setStep(SUBMITTED);
                    }
                    }
                />
            </div>
            :
            <div>
               
            </div>
        }
    </div>);
}

function Summary(props) {
    const presentationId = props?.presentationId;
    const data = props?.data;

    const { labels } = useSelector(state => state.annotationState);

    const endIdxs = [ ...Object.keys(labels).map((val) => parseInt(val)).sort((p1, p2) => p1 - p2)];

    const totalNumSteps = endIdxs.length;

    let startIdx = 1
    let endIdx = data?.slideInfo?.length - 1;

    let outline = [];

    for (let i = 0; i < endIdxs.length; i++) {
        const start = i > 0 ? endIdxs[i - 1] + 1 : 1;
        const end = endIdxs[i];
        outline.push({
            sectionTitle: labels[end],
            startSlideIndex: start,
            endSlideIndex: end,
        });
    }

    return (<div>
        <h4> Summary: You labeled {totalNumSteps} segments </h4>
        <div>
            <Outline
                isGenerated={false}
                outline={outline}
                slideInfo={data?.slideInfo}
            />
        </div>
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

function Instructions(props) {
    const presentationId = props?.presentationId;
    const presentationData = props?.presentationData;
    const step = props?.step;

    const { submissionId } = useSelector(state => state.annotationState);

    let presentationVideo = null;
    for (let key in presentationData) {
        if (presentationData[key].includes("youtube")) {
            presentationVideo = presentationData[key];
        }
    }

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
                return "Your work is recorded!"
            default:
                return null;
        }
    }

    return (<div>        
        <h2> Presentation {presentationId} </h2>
        <div style={{
            "textAlign": "left",
            "margin": "2em",
            "padding": "1em",
            "background": "lightgray"
        }}>
            <h3> Instructions: </h3>
            <ol start={0}>
                {step === WARM_UP ? 
                    <li> <b>  {" -> "} Warm-up: </b> Skim through slides & scripts to get a general sense of the presentation</li>
                    :
                    <li> Warm-up: Skim through slides & scripts to general sense of the presentation</li>
                }
                <ul> 
                    {
                        presentationVideo ? 
                        <li>
                            You can watch the entire presentation video here:{" "}
                            <a href={presentationVideo}>Youtube ~15 mins </a>
                            <i>(but just skimming slides & scripts should be faster)</i>
                        </li>
                        :
                        null
                    }
                </ul>

                {step === TASK_1 ?
                    <li> 
                        <b> {" -> "} Task: </b>
                        Identify main <a href={"section_transition_examples"}> section transitions </a> in slides
                    </li>
                    :
                    <li> Task: Identify main <a href={"section_transition_examples"}> section transitions </a>  in slides </li>
                }
                {step === TASK_2 ? 
                    <li> <b> {" -> "} Task: </b> Label produced segments of slides. Feel free to enter any label you find fitting.  </li>
                    :
                    <li> Task: Label produced segments of slides. Feel free to enter any label you find fitting. </li>
                }
                {/* {step === TASK_3 ?
                    <li> <b> {" -> "} Task: </b> Bonus </li>
                    :
                    <li> Task: Bonus </li>
                } */}
            </ol>
        </div>
        <div style={{
            margin: "1em"
        }}>
            <h2> {stepTitle(step)} </h2>
            {
                step === SUBMITTED ?
                <div>
                    <span> Your Submission Id (copy-paste it to the form): </span>
                    <h4> {submissionId} </h4>
                    <h3> <a href={GOOGLE_FORM_LINK}> Please Fill out the Form </a> </h3>
                </div>
                : 
                null
            }
        </div>
    </div>);
}


function Motivation(props) {
    return (<div>
        <div style={{
            "textAlign": "left",
            "margin": "2em",
            "padding": "1em",
            "background": "lightgray"
        }}>
            <h3> Motivation: </h3>
            <p>
                Project Doc2Slide (KIXLAB) is constructing a corpus of outlines for conference presentations.
                The aim is to evaluate our outline generation algorithm.
            </p>
            <p>
                If you have any questions please contact me through Slack DM or email to
                <a href={"mailto:tlekbay.b@gmail.com"}> tlekbay.b@gmail.com </a>
            </p>
        </div>
    </div>);
}

function PresentationGallery(props) {
    const dispatch = useDispatch();

    const summary = props?.summary;

    if (!summary) {
        return null;
    }

    const summaryData = summary?.summaryData;
    const presentationsData = summary?.presentationData;

    const validPresentationIds = summaryData?.valid_presentation_index;

    const handleButtonClick = (presentationId, presentationData) => {
        dispatch(setPresentationid({
            presentationId,
            presentationData,
        }));
        window.scrollTo(0, 0);
        dispatch(setStep({ step: WARM_UP }));
    }

    return (<div>
        {
            validPresentationIds.map((presentationId) => {
                const presentationData = presentationsData[presentationId];
                return (<GenericButton
                    key={"button" + presentationId.toString()}
                    title={"Presentation " + presentationId.toString()}
                    onClick={() => handleButtonClick(presentationId, presentationData)}
                />);
            })
        }
    </div>);
}

function Annotation(props) {
    const dispatch = useDispatch();
    
    const { step, presentationId, presentationData } = useSelector(state => state.annotationState);

    const [data, setData] = useState([]);

    const [summary, setSummary] = useState(null);

    useEffect(() => {
        if (step > INTRO) {
            axios.post('http://server.hyungyu.com:7777/mapping/presentation_data', {
                presentationId: presentationId,
            }).then( (response) => {
                console.log(response);
                setData(response.data.data);
                dispatch(setLabel({
                    boundary: response.data.data.slideCnt - 1,
                    label: "end"
                }));
            });
        }
	}, [presentationId]);

    useEffect(() => {
        if (step === INTRO) {
            axios.post('http://server.hyungyu.com:7777/mapping/summary_data', {
            }).then( (response) => {
                console.log(response);
                setSummary(response.data);
            });
        }
    }, [step])

    const _setStep = (new_step) => {
        window.scrollTo(0, 0);
        dispatch(setStep({ step: new_step }));
    }

    const outputMainSection = () => {
        switch(step) {
            case INTRO:
                return (<div>
                    <PresentationGallery
                        summary={summary}
                    />
                </div>);
            
            case WARM_UP:
                return (<div>
                    <Instructions
                        presentationId={presentationId}
                        presentationData={presentationData}
                        step={step}
                    />
                    <WarmUp presentationId={presentationId}  data={data}/>

                    <GenericButton
                        title={"Start Task 1"}
                        onClick={() => _setStep(TASK_1)}
                    />
                </div>);
            
            case TASK_1:
                return (<div>
                    <Instructions
                        presentationId={presentationId}
                        presentationData={presentationData}
                        step={step}
                    />
                    <Task1 presentationId={presentationId}  data={data}/>
                    <GenericButton
                        title={"Start Task 2"}
                        onClick={() => _setStep(TASK_2)}
                    />
                </div>);
            case TASK_2:
                return (<div>
                    <Instructions
                        presentationId={presentationId}
                        presentationData={presentationData}
                        step={step}
                    />
                    <Task2 presentationId={presentationId}  data={data}/>
                </div>);
            // case TASK_3:
            default:
                return <div>
                    <Instructions
                        presentationId={presentationId}
                        presentationData={presentationData}
                        step={step}
                    />
                    <Summary presentationId={presentationId}  data={data}/>
                </div>
        }
    }

    return (<div className="App">
        <h2> Ground Truth Construction for Presentation Outlines</h2>
        <div style={{
            textAlign: "right",
            marginRight: "1em"
        }}>
            <GenericButton
                title={"Restart"}
                onClick={() => dispatch(resetApp())}
            />
        </div>
        <Motivation/>
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
                step < TASK_2 && step >= WARM_UP ? 
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