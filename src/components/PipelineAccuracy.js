import React from "react";

function PipelineAccuracy(props) {
    const title = props?.title ? props.title : "Accuracy"
    const boundariesAccuracy = props?.evaluationData?.boundariesAccuracy;
    const timeAccuracy = props?.evaluationData?.timeAccuracy;
    const structureAccuracy = props?.evaluationData?.structureAccuracy;

    const overallTimeAccuracy = props?.evaluationData?.overallTimeAccuracy;
    const separateTimeAccuracy = props?.evaluationData?.separateTimeAccuracy;
    
    const mappingAccuracy = props?.evaluationData?.mappingAccuracy;
    const separateMappingAccuracy = props?.evaluationData?.separateMappingAccuracy;
    


    const overallSlidesAccuracy = props?.evaluationData?.overallSlidesAccuracy;
    const separateSlidesAccuracy = props?.evaluationData?.separateSlidesAccuracy;
    
    return (<div style={{
        textAlign: "left",
        fontSize: "12pt",
        margin: "2em"
    }}>
        <h2> {title}: </h2>
        <p> Overall Time F1-score: {overallTimeAccuracy} </p>
        <ul>
            <li> Beginning score: {separateTimeAccuracy[0]} </li>
            <li> Middle score: {separateTimeAccuracy[1]} </li>
            <li> Ending score: {separateTimeAccuracy[2]} </li>
        </ul>
        <p> Overall Slides F1-score: {overallSlidesAccuracy} </p>
        <ul>
            <li> Beginning score: {separateSlidesAccuracy[0]} </li>
            <li> Middle score: {separateSlidesAccuracy[1]} </li>
            <li> Ending score: {separateSlidesAccuracy[2]} </li>
        </ul>
        <p> Mapping Accuracy: {mappingAccuracy}% </p>
        <ul>
            <li> Beginning score: {separateMappingAccuracy[0]}% </li>
            <li> Middle score: {separateMappingAccuracy[1]}% </li>
            <li> Ending score: {separateMappingAccuracy[2]}% </li>
        </ul>
        {/* <p> Video Overview (Boundaries): {boundariesAccuracy}% </p>
        <p> Presentation Structure (Order): {structureAccuracy}% </p>*/}
    </div>);
}

export default PipelineAccuracy;