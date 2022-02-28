import React from "react";

function ModelConfig(props) {
    const similarityType = props?.similarityType;
    const outliningApproach = props?.outliningApproach;
    const applyThresholding = props?.applyThresholding;

    return (<div style={{
        textAlign: "left",
        fontSize: "12pt",
        margin: "2em"
    }}>
        <h2> Model: </h2>
        <p> Similarity: {similarityType} </p>
        <p> Outlining: {outliningApproach} </p>
        <p> Thresholding: {applyThresholding ? "True" : "False"} </p>
    </div>);
}

export default ModelConfig;