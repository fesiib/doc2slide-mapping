import React from "react";

function PipelineAccuracy(props) {
    const boundariesAccuracy = props?.evaluationData?.boundariesAccuracy;
    const timeAccuracy = props?.evaluationData?.timeAccuracy;
    const structureAccuracy = props?.evaluationData?.structureAccuracy;
    const mappingAccuracy = props?.evaluationData?.mappingAccuracy;

    return (<div style={{
        textAlign: "left",
        fontSize: "12pt",
        margin: "2em"
    }}>
        <h2> Accuracy: </h2>
        <p> Overall F1-score: {timeAccuracy}% </p>
        <p> Mapping Accuracy: {mappingAccuracy}% </p> 
        {/* <p> Video Overview (Boundaries): {boundariesAccuracy}% </p>
        <p> Presentation Structure (Order): {structureAccuracy}% </p>*/}
    </div>);
}

export default PipelineAccuracy;