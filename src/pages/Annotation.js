import React, { useEffect, useState } from "react";
import axios from "axios";
import '../App.css';

import { useDispatch, useSelector } from "react-redux";
import { resetApp } from "../reducers";
import { setLabel, setPresentationid, setStep } from "../reducers/annotationState";

import GenericButton from "../components/GenericButton";
import { AfterSubmission, AnnotationTask0, AnnotationTask1 } from "../components/AnnotationTasks";
import Outline from "../components/Outline";

const INTRO = 0;
const WARM_UP = 1;
const TASK_1 = 2;
const TASK_2 = 33;
const TASK_3 = 44;
const SUBMITTED = 3;

const GOOGLE_FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSfMRNceok4P5pLvu9ofROTUcFr_AKYPBzv6lKu8CX3qBP3B9g/viewform?usp=sf_link"

export const ANNOTATION_PRESENTATION_IDS = [4, 6, 7, 9, 19];

function Instructions(props) {
    const presentationData = props?.presentationData;
    const sectionTitles = props?.sectionTitles;
    const step = props?.step;
    const collapsed = props?.collapsed;

    let presentationVideo = null;
    let presentationPaper = null;
    for (let key in presentationData) {
        if (presentationData[key].includes("youtube")) {
            presentationVideo = presentationData[key];
        }
        if (presentationData[key].endsWith(".pdf")) {
            const link = presentationData[key].replace(".pdf", "");
            presentationPaper = "https://dl.acm.org/doi/pdf/10.1145/" + link;
        }
    }

    return (<div style={{
        display: collapsed ? "none" : "block", 
        textAlign: "left",
        marginTop: "1em",
        padding: "1em",
        background: "lightgray"
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
                    </li>
                    :
                    null
                }
                {
                    presentationPaper ? 
                    <li>
                        You can read the original paper here:{" "}
                        <a href={presentationPaper}> PDF </a>
                    </li>
                    :
                    null
                }
            </ul>

            <li>
                {step === TASK_1 ?
                    <b> {" -> "} Task: </b>
                    :
                    <span> Task </span>
                }
                <ul>
                    <li>
                        Identify main <a href={"section_transition_examples"}> section transitions </a> in slides
                    </li>
                    <li>
                        Label them with below section titles from the paper:
                        <ul>
                            {  
                                sectionTitles.map((val, idx) => {
                                    let title = val;
                                    return (<li key={"sectionTitle_" + idx}>
                                        {title}
                                    </li>);
                                })
                            }
                        </ul>
                    </li>
                </ul>
            </li>
            {/* {step === TASK_2 ? 
                <li> <b> {" -> "} Task: </b> Label produced segments of slides  </li>
                :
                <li> Task: Label produced segments of slides. </li>
            } */}
            {/* {step === TASK_3 ?
                <li> <b> {" -> "} Task: </b> Bonus </li>
                :
                <li> Task: Bonus </li>
            } */}
        </ol>
        {/* <ul>

            <li>
                You can jump back & forth between Tasks 1 and 2 <i>
                    (just press on the <span style={{color: "darkBlue"}}> blue </span> buttons above)
                </i>
            </li>
        </ul> */}
    </div>); 
}


function Motivation() {
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

    const validPresentationIds = summaryData?.valid_presentation_index.filter(
        presentationId => ANNOTATION_PRESENTATION_IDS.includes(presentationId)
    );

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
    
    const { step,
        presentationId,
        presentationData,
        submissionId,
        labels
    } = useSelector(state => state.annotationState);

    const [data, setData] = useState([]);
    const [summary, setSummary] = useState(null);
    const [collapsed, setCollapsed] = useState(false);

    let outline = [];
    const endIdxs = [ ...Object.keys(labels).map((val) => parseInt(val)).sort((p1, p2) => p1 - p2)];

    for (let i = 0; i < endIdxs.length; i++) {
        const start = i > 0 ? endIdxs[i - 1] + 1 : 1;
        const end = endIdxs[i];
        outline.push({
            sectionTitle: labels[end],
            startSlideIndex: start,
            endSlideIndex: end,
        });
    }

    useEffect(() => {
        if (step > INTRO) {
            axios.post('http://server.hyungyu.com:7777/mapping/presentation_data', {
                presentationId: presentationId,
            }).then( (response) => {
                console.log(response);
                setData(response.data.data);
                dispatch(setLabel({
                    boundary: response.data.data.slideCnt - 1,
                    label: "End"
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
    }, [step]);


    const _setStep = (new_step) => {
        window.scrollTo(0, 0);
        dispatch(setStep({ step: new_step }));
    }

    const submitAnnotation = () => {
        _setStep(SUBMITTED);
        axios.post('http://server.hyungyu.com:7777/annotation/submit_annotation', {
            presentationId: presentationId,
            submissionId: submissionId,
            outline: outline,
        }).then( (response) => {
            console.log(response);
        });
    };

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

    const outputMainSection = () => {
        let instructions = false;
        let middleSection = null;
        let lastButton = null;

        switch(step) {
            case INTRO:
                middleSection = (<PresentationGallery
                    summary={summary}
                />);
                break;
            case WARM_UP:
                instructions = true;
                middleSection = (<AnnotationTask0
                    presentationId={presentationId}
                    data={data}
                />);
                lastButton = (<GenericButton
                    title={"Start Task 1"}
                    onClick={() => _setStep(TASK_1)}
                    color="darkBlue"
                />);
                break;
            case TASK_1:
                instructions = true;
                middleSection = (<AnnotationTask1
                    presentationId={presentationId}
                    data={data}
                />);
                lastButton = (<GenericButton
                    title={"Submit"}
                    onClick={submitAnnotation}
                    color="darkBlue"
                />);
                break;
            case TASK_2:
            case TASK_3:
            default:
                middleSection = (<AfterSubmission
                    presentationId={presentationId}
                    data={data}
                    formLink={GOOGLE_FORM_LINK}
                    outline={outline}
                />);

                lastButton = (<GenericButton
                    title={"Start new Annotation"}
                    onClick={() => dispatch(resetApp())}
                    color="darkBlue"
                />);
        }
        return (<div>
            {
                presentationId < 0 ?
                    <h2> Please choose a Presentation </h2>
                :
                    <h2> Presentation {presentationId} </h2>
            }
            {instructions ?
                <div>
                    <Instructions
                        presentationData={presentationData}
                        presentationId={presentationId}
                        sectionTitles={data?.sectionTitles ? data.sectionTitles : []}
                        step={step}
                    />
                    <div style={{
                        display: "flex",
                        justifyContent: "space-between",
                        marginLeft: "1em",
                        marginRight: "1em"
                    }}> 
                        <GenericButton
                            title={"<- Previous"}
                            onClick={() => _setStep(step - 1)}
                            color="darkBlue"
                            disabled={step < TASK_1 || step >= SUBMITTED}
                        />
                        <h3> {stepTitle(step)} </h3>
                        <GenericButton
                            title={"Next ->"}
                            onClick={() => _setStep(step + 1)}
                            color="darkBlue"
                            disabled={step >= TASK_1 || step < WARM_UP}
                        />
                    </div>
                </div>
                :
                null
            }
            {
                step < SUBMITTED && step > WARM_UP ?
                (
                    <div style={{
                        position: "-webkit-sticky",
                        position: "sticky",
                        top: "0px",
                        paddingTop: "1em",
                        background: "white",
                    }}> 
                        <GenericButton
                            title={collapsed ? "Expand Summary" : "Collapse"}
                            onClick={() => setCollapsed(!collapsed)}
                        />    
                        {
                            collapsed ?
                                null
                            :
                            <Outline
                                title={"Annotation Summary"}
                                outline={outline}
                                slideInfo={data?.slideInfo}
                            />
                            
                        }
                        <hr/>
                    </div>
                )
                :
                <hr/>
            }
            {middleSection}
            {lastButton}
        </div>);
    }

    return (<div className="App">
        <h2> Ground Truth Construction for Presentation Outlines</h2>
        <div style={{
            textAlign: "right",
            marginRight: "1em"
        }}>
            {
                step < SUBMITTED ?      
                <GenericButton
                    title={"Restart"}
                    onClick={() => dispatch(resetApp())}
                />
                :
                null
            }
        </div>
        {
            step === INTRO ?
            <Motivation/>
            :
            null
        }
        {outputMainSection()}
    </div>)
}

export default Annotation;