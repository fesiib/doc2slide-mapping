import React, { useEffect, useState } from "react";
import axios from "axios";
import '../App.css';

import { useDispatch, useSelector } from "react-redux";
import { resetApp } from "../reducers";
import { NO_LABEL, setLabel, setPresentationid, setStep } from "../reducers/annotationState";

import GenericButton from "../components/GenericButton";
import { AfterSubmission, AnnotationTask0, AnnotationTask1 } from "../components/AnnotationTasks";
import Outline from "../components/Outline";
import ReactPlayer from "react-player";

const INTRO = 0;
const BROWSING = 1;
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

    presentationVideo = null;

    return (<div style={{
        display: collapsed ? "none" : "block", 
        textAlign: "left",
        marginTop: "1em",
        padding: "1em",
        background: "lightgray"
    }}>
        <h3> Instructions: </h3>

        <p>
            The goal of the annotation task is to generate an outline for a chosen presentation.
            Below, the presentation slides and script are given. They were extracted from the presentation video.
        </p>
        <p>
            In short, in <b> Browsing </b> you will be asked to skim through both slides & scripts, so in the <b> Task 1 </b>
            you could identify the transitions and label each resultant segment. <br/>
            The labels are section titles from the original paper of the presentation or default <i> Title Page and End Page </i>.
        </p>

        <ol start={0}>
            {step === BROWSING ? 
                <li> <b>  {" -> "} Browsing: </b> Skim through slides & scripts to get a general sense of the presentation</li>
                :
                <li> Browsing: Skim through slides & scripts to general sense of the presentation</li>
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
                        Label them with default TITLE & END, and below section titles from the paper:
                        <ul>
                            <li> TITLE </li>
                            {  
                                sectionTitles.map((val, idx) => {
                                    let title = val;
                                    return (<li key={"sectionTitle_" + idx}>
                                        {title}
                                    </li>);
                                })
                            }
                            <li> END </li>
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
                Project Doc2Slide (KIXLAB) is constructing a corpus of outlines of conference presentations.
                The aim is to evaluate the accuracy of our outline generation algorithm.
            </p>
            <p>
                There is no strict universal definition of an outline. 
                In our case, we are concerned about outlines of presentations, more specifically the slides.
            </p>
            <p>
                In other words, the outline is a segmentation of presentation slides that consist of:
            </p>
            <ul>
                <li> Labels of segments. </li>
                <li> Each segment's starting & ending points </li>
                <li> Time spent on each segment </li>
            </ul>
            <p>
                So for example, the below could have been an appropriate outline:
            </p>

            <ol>
                <li> Title Page (1 - 1) (30 seconds)</li>
                <li> Introduction (2 - 5) (1 minute)</li>
                <li> System (6 - 20) (5 minutes)</li>
                <li> Discussion (21 - 25) (3 minutes)</li>
                <li> End (26 - 26) (20 seconds )</li>
            </ol>
            <p>
                You will be given presentation slides, corresponding scripts, and labels.
                The task is to segment the slides by selecting appropriate transitions and annotating each segment with given labels.
            </p>
            <p>
                If you have any questions please email me to
                <a href={"mailto:tlekbay.b@gmail.com"}> tlekbay.b@gmail.com </a>
            </p>
        </div>
    </div>);
}

function TutorialVideo(props) {
    const TUTORIAL_VIDEO = "/annotationTutorials/tutorial_1.mp4";
    return (<div>
        <h2> Tutorial Video </h2>
        <ReactPlayer
            style={{
                margin: "auto"
            }}
            url={TUTORIAL_VIDEO}
            height={"500px"}
            controls={true}
        />
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
        dispatch(setStep({ step: BROWSING }));
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
                    label: "END"
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
        let noLabels = [];
        for (let endIdx in labels) {
            if (labels[endIdx] === NO_LABEL) {
                noLabels.push(endIdx);
            }
        }

        if (noLabels.length > 0) {
            return;
        }

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
            case BROWSING:
                return "Currently in " + "Browsing";
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
            case BROWSING:
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
                            disabled={step >= TASK_1 || step < BROWSING}
                        />
                    </div>
                </div>
                :
                null
            }
            {
                step < SUBMITTED && step > BROWSING ?
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
        <h2> Outline Construction for Presentations </h2>
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
            <div>            
                <Motivation/>
                <TutorialVideo/>
            </div>
            :
            null
        }
        {outputMainSection()}
    </div>)
}

export default Annotation;