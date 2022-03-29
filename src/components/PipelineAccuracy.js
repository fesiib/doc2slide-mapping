import React from "react";

function PipelineAccuracy(props) {
    const boundariesAccuracy = props?.evaluationData?.boundariesAccuracy;
    const timeAccuracy = props?.evaluationData?.timeAccuracy;
    const structureAccuracy = props?.evaluationData?.structureAccuracy;
    const overallAccuracy = props?.evaluationData?.overallAccuracy;
    const mappingAccuracy = props?.evaluationData?.mappingAccuracy;
    const separateAccuracy = props?.evaluationData?.separateAccuracy;

    return (<div style={{
        textAlign: "left",
        fontSize: "12pt",
        margin: "2em"
    }}>
        <h2> Accuracy: </h2>
        <p> Overall F1-score: {overallAccuracy} </p>
        <ul>
            <li> Beginning score: {separateAccuracy[0]} </li>
            <li> Middle score: {separateAccuracy[1]} </li>
            <li> Ending score: {separateAccuracy[2]} </li>
        </ul>
        <p> Mapping Accuracy: {mappingAccuracy}% </p> 
        {/* <p> Video Overview (Boundaries): {boundariesAccuracy}% </p>
        <p> Presentation Structure (Order): {structureAccuracy}% </p>*/}
    </div>);
}

export default PipelineAccuracy;