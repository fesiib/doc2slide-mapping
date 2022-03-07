import { useState } from "react";
import Outline from "./Outline";

const GT_ID = "ground-truth";

function AnnotationList(props) {
    const gtOutline = props?.gtOutline;
    const slideInfo = props?.slideInfo;
    const annotations = props?.annotations;
    const annotationIds = Object.keys(annotations);
    
    const [selectedAnnotationId, setSelectedAnnotationId] = useState(GT_ID);
    
    const handleSelectChange = (event) => {
        console.log(event.target);
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
        {
            selectedAnnotationId === GT_ID ?
            (
                gtOutline ? 
                <Outline isGenerated={false} outline={gtOutline} slideInfo={slideInfo} />
                :
                <div> No Paper-based Ground Truth </div>
            )
            :
            <Outline isGenerated={false} outline={annotations[selectedAnnotationId]} slideInfo={slideInfo} />
        }
    </div>);
}

export default AnnotationList;