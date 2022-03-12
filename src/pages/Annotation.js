import React, { useEffect, useState } from "react";
import axios from "axios";
import '../App.css';

import { useDispatch, useSelector } from "react-redux";
import { resetApp } from "../reducers";
import { NO_LABEL, setLabel, setPresentationid, setStep } from "../reducers/annotationState";

import GenericButton from "../components/GenericButton";
import { AfterSubmission, AnnotationTask0, AnnotationTask1, AnnotationVerify } from "../components/AnnotationTasks";
import Outline from "../components/Outline";
import ReactPlayer from "react-player";

const INTRO = 0;
const BROWSING = 1;
const TASK_1 = 2;
const TASK_2 = 3;
const TASK_3 = 44;
const SUBMITTED = 4;

const GOOGLE_FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSfMRNceok4P5pLvu9ofROTUcFr_AKYPBzv6lKu8CX3qBP3B9g/viewform?usp=sf_link"

export const LONG_PRESENTATION_IDS = [147, 202, 185, 135, 142, 94, 175, 118, 27, 92];

const USER_PRESENTATION_IDS = [
    [
        142,
        202,
        94
    ],
    [
        175,
        92,
        202
    ],
    [
        202,
        92,
        185
    ],
    [
        175,
        147,
        118
    ],
    [
        94,
        118,
        147
    ],
    [
        135,
        185,
        92
    ],
    [
        142,
        27,
        175
    ],
    [
        27,
        175,
        92
    ],
    [
        175,
        185,
        92
    ],
    [
        27,
        147,
        92
    ]
];

function randomlyChoose(presentationIds, cnt) {
    if (presentationIds.length <= cnt) {
        return presentationIds;
    }

    let chosen = [];
    while (cnt > 0) {
        const randIdx = Math.floor(Math.random() * presentationIds.length);
        chosen.push(presentationIds[randIdx]);
        presentationIds.splice(randIdx, 1);
        cnt--;
    }
    return chosen;
}

function assignPresenationIds(presentationIds, perPresentationCnt, userCnt, perUserCnt) {
    let unassigned = {};
    if (perPresentationCnt > 0) {
        for (let presentationId of presentationIds) {
            unassigned[presentationId] = perPresentationCnt;
        }
    }
    else {
        presentationIds = [];
    }

    let assignment = [];
    for (let userId = 0; userId < userCnt; userId++) {
        assignment.push([]);
        let curUserCnt = perUserCnt;
        let curPresentationIds = [ ...presentationIds ];
        while (curUserCnt > 0 && curPresentationIds.length > 0) {
            const randIdx = Math.floor(Math.random() * curPresentationIds.length);
            const presentationId = (curPresentationIds.splice(randIdx, 1))[0];
            unassigned[presentationId]--;
            if (unassigned[presentationId] === 0) {
                presentationIds.splice(randIdx, 1);
            }
            assignment[userId].push(presentationId);
            curUserCnt--;
        }
    }
    return assignment;
}

function Instructions(props) {
    const presentationData = props?.presentationData;
    const sectionTitles = props?.sectionTitles;
    const step = props?.step;
    const collapsed = props?.collapsed;

    let presentationVideo = null;
    let presentationPaper = null;

    if (presentationData.hasOwnProperty("video")) {
        presentationPaper = presentationData["video"];
    }

    if (presentationData.hasOwnProperty("paper")) {
        presentationPaper = presentationData["paper"];
    }
    
    // for (let key in presentationData) {
    //     if (presentationData[key].includes("youtube")) {
    //         presentationVideo = presentationData[key];
    //     }
    //     if (presentationData[key].endsWith(".pdf")) {
    //         const link = presentationData[key].replace(".pdf", "");
    //         presentationPaper = "https://dl.acm.org/doi/pdf/10.1145/" + link;
    //     }
    // }

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
            <li>
                {step === TASK_2 ? 
                        <span> <b> {" -> "} Verification: </b> Verify Segments and Labels   </span>
                    :
                        <span> Verification: Verify Segments and Labels </span>
                }
                <ul>
                    <li> You can go to Task 1 by clicking <b> {" <- "} Previous </b>  button. </li>
                </ul>
            </li>
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
                The aim is to evaluate the accuracy of our outline generation algorithm.
            </p>
            <p>
                There is no universal definition of an outlines for presentations. 
                In our case, we define the outline as a segmentation of slides in the presentation.
            </p>
            <p>
                In other words, the outline consist of:
            </p>
            <ul>
                <li> Set of segments that cover all presentation slides; </li>
                <li> Labels of segments; </li>
                <li> Each segment's starting & ending points; </li>
                <li> Time spent on each segment; </li>
            </ul>
            <p>
                So for example, the below could have been an appropriate outline:
            </p>
            <p style={{textIndent: "2em", fontSize: "0.8em"}}>
                Format: [Label] ([Start Slide] - [End Slide]) ([Time Spent])
            </p>
                

            <ol>
                <li> Title Page (1 - 1) (30 seconds)</li>
                <li> Introduction (2 - 5) (1 minute)</li>
                <li> System (6 - 20) (5 minutes)</li>
                <li> Discussion (21 - 25) (3 minutes)</li>
                <li> End (26 - 26) (20 seconds )</li>
            </ol>

            <div style={{color: "red"}}>
                <p>
                    You will be given 3 different presentations, and you can proceed in any order you prefer. 
                </p>
                <p>
                    For each presentation, the slides, corresponding scripts, and labels are given. <br/>
                    The task is to segment the slides by selecting appropriate transitions and annotating each segment with given labels.
                </p>
            </div>
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
                margin: "auto",
            }}
            url={TUTORIAL_VIDEO}
            controls={true}
        />
    </div>);
}

function PresentationGallery(props) {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
	let userId = parseInt(urlParams.get('userId'));

    if (!(userId >= 0 && userId < USER_PRESENTATION_IDS.length)) {
        userId = 0;
    }

    const dispatch = useDispatch();

    const summary = props?.summary;

    if (!summary) {
        return null;
    }

    const summaryData = summary?.summaryData;

    const validPresentationIds = summaryData?.all_presentation_index.filter(
        presentationId => USER_PRESENTATION_IDS[userId].includes(presentationId)
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
                const presentationData = {
                    "paper": `http://server.hyungyu.com:7777/papers/${presentationId}/paper.pdf`,
                };
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
    //console.log(randomlyChoose(ALL_PRESENTATION_IDS_LONG, 10));
    //console.log(assignPresenationIds([147, 202, 185, 135, 142, 94, 175, 118, 27, 92], 3, 10, 3));

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

    const verifyOutline = () => {
        let noLabels = [];
        for (let endIdx in labels) {
            if (labels[endIdx] === NO_LABEL) {
                noLabels.push(endIdx);
            }
        }

        return noLabels.length === 0;
    }

    const submitAnnotation = () => {
        if (!verifyOutline()) {
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
                return "Currently in " + "Verification";
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
                    title={"Finish"}
                    onClick={() => {
                        if (!verifyOutline()) {
                            return;
                        }
                        _setStep(TASK_2);
                    }}
                    color="darkBlue"
                />);
                break;
            case TASK_2:
                instructions = true;
                middleSection = (<AnnotationVerify
                    presentationId={presentationId}
                    data={data}
                    outline={outline}
                />)
                lastButton = (<GenericButton
                    title={"Verify & Submit"}
                    onClick={submitAnnotation}
                    color="darkBlue"
                />);
                break;
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
                step > INTRO && step < SUBMITTED ?  
                <div>
                    <GenericButton
                        title={"Restart"}
                        onClick={() => dispatch(resetApp())}
                    />
                    <p style={{color: "red", margin: 0}}>
                        By restarting, you will <br/>
                        <b> destroy the annotation </b> done <br/>
                        for presentation {presentationId} <br/>
                        and will <b> go to the first page. </b>
                    </p>
                </div>    
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