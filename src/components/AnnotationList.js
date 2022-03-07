import { useState } from "react";
import Outline from "./Outline";

const NO_SELECTION_ID = "no_selection";

function AnnotationList(props) {
    const slideInfo = props?.slideInfo;
    const annotations = props?.annotations;
    const annotationIds = Object.keys(annotations);
    
    const [selectedAnnotationId, setSelectedAnnotationId] = useState(NO_SELECTION_ID);
    
    const handleSelectChange = (event) => {
        console.log(event.target);
        setSelectedAnnotationId(event.target.value);
    }

    if (annotationIds.length === 0) {
        return (<div>
            No annotations Yet!!!
        </div>);
    }
    return (<div>
        <label htmlFor="annotation"> Annotation: </label>
        <select 
            id="annotation"
            name="annotation"
            onChange={handleSelectChange}
            value={selectedAnnotationId}
        >
            <option value={NO_SELECTION_ID}> No selection </option>
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
            selectedAnnotationId === NO_SELECTION_ID ?
            <div>
                Please select annotation
            </div>
            :
            <Outline isGenerated={false} outline={annotations[selectedAnnotationId]} slideInfo={slideInfo} />
        }
    </div>);
}

export default AnnotationList;