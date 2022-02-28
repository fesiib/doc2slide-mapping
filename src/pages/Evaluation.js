import axios from 'axios'
import {useState, useEffect} from 'react';
import EvaluationTable from '../components/EvaluationTable';

function Evaluation() {
	const [evaluationResults, setEvaluationResults] = useState([]);
	
	useEffect(() => {
		axios.post('http://localhost:3555/get_evaluation_results', {
		}).then( (response) => {
			console.log("Evaluation", response);
            setEvaluationResults(response.data.evaluationResults)
		});
	}, []);

	if (!evaluationResults) {
		return <div> LOADING !!! </div>
	}

	return (
		<div className="EvaluationResult">
            <EvaluationTable evaluationResults={evaluationResults}/>
		</div>
	);
}

export default Evaluation;
