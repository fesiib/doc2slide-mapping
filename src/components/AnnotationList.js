import { useState } from "react";
import Outline from "./Outline";
import PipelineAccuracy from "./PipelineAccuracy";

const GT_ID = "groundTruth";

function AnnotationList(props) {
    const gtOutline = props?.gtOutline;
    const slideInfo = props?.slideInfo;
    const annotations = props?.annotations;
    const evaluationData = props?.evaluationData;
    const annotationIds = Object.keys(annotations);
    
    const [selectedAnnotationId, setSelectedAnnotationId] = useState(GT_ID);
    
    const handleSelectChange = (event) => {
        setSelectedAnnotationId(event.target.value);
    }
    return (<div>
        <label htmlFor="annotation"> Annotation: </label>
            <select 
                id="annotation"
                name="annotation"
                onChange={handleSelectChange}
                value={selectedAnnotationId}
            >
                <option value={GT_ID}> Paper-based Ground Truth </option>
                {
                    annotationIds.map((annotationId, idx) => {
                        return (<option 
                                key={"annotation_" + idx.toString()}
                                value={annotationId}
                            > {annotationId} </option>);
                    })
                }
        </select>
        <div style={{
            display: "flex",
            flexDirection: "row",
            justifyContent: "space-evenly"
        }}>
            <div>
                {
                    selectedAnnotationId === GT_ID ?
                    (
                        gtOutline.length > 0 ? 
                        <Outline isGenerated={false} outline={gtOutline} slideInfo={slideInfo} />
                        :
                        <p> No Paper-based Ground Truth </p>
                    )
                    :
                    <Outline isGenerated={false} outline={annotations[selectedAnnotationId]} slideInfo={slideInfo} />
                }
            </div>
            <div>
                <PipelineAccuracy
                    evaluationData={evaluationData[selectedAnnotationId]}
                />
            </div>
        </div>
    </div>);
}

export default AnnotationList;