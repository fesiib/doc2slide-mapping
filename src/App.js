import logo from './logo.svg';
import axios from 'axios'
import {useState, useEffect} from 'react';
import './App.css';

function App() {
  const [presentationIndex, setPresentationIndex] = useState(-1);
  const [statement, setStatement] = useState([]);
  const [script, setScript] = useState([]);
  const [similarity, setSimilarity] = useState([]);
  const [curStatement, setCurStatement] = useState(-1);
  const [mapping, setMapping] = useState([]);
  const [heatmapShow, setHeatmapShow] = useState(false);

  useEffect( () => {
    console.log("GO");

    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);

    const presentationID = parseInt(urlParams.get('presentationid'));
    console.log(presentationID);

    axios.post('http://localhost:3555/getData', {
      username: 'blabla',
      name: 'blabla'
    }).then( (response) => {
      console.log(response);


      for(var i=0;i<response.data.length;i++) {
        if (response.data[i].id == presentationID) {
          var myMapping = getMappingFromSimilarity(response.data[i].similarity)
          setMapping(myMapping);
          setPresentationIndex(response.data[i].id);
          setStatement(response.data[i].paper);
          setScript(response.data[i].script);
          setSimilarity(response.data[i].similarity);

          return;
        }
      }
    });

  }, [])

  function getMappingFromSimilarity(sim) {
    var threshold = 1;
    var returnValue = [];

    var tmp1 = JSON.parse(JSON.stringify(sim));
    var tmp2 = JSON.parse(JSON.stringify(sim));
    var final = JSON.parse(JSON.stringify(sim));

    for(var i=0;i<tmp1.length;i++) {
      var values = [];

      for(var j=0;j<sim[i].length;j++) values.push(sim[i][j]);

      values.sort();
      var thres_value = values[values.length-threshold]

      for(var j=0;j<sim[i].length;j++) {
        if(sim[i][j] < thres_value) 
          tmp1[i][j] = 0;
      }
    }

    for(var i=0;i<sim[0].length;i++) {
      var values = [];

      for(var j=0;j<sim.length;j++) values.push(sim[j][i]);

      values.sort();
      var thres_value = values[values.length-threshold]

      for(var j=0;j<sim.length;j++) {
        if(sim[j][i] < thres_value) 
          tmp2[j][i] = 0;
      }
    }

    for(var i=0;i<sim.length;i++) {
      for(var j=0;j<sim[i].length;j++) 
        final[i][j] = Math.min(tmp1[i][j], tmp2[i][j])
    }

    console.log(final);
    
    return final;
  }

  function getSlides() {
    if(presentationIndex == -1) return '';

    var returnValue = [];

    for(var i=0;i<script.length;i++) {
      returnValue.push(<div class="slideImageDiv" index={i}>
        <img class="slideImage" src={"./capture/" + presentationIndex + "/" + i + ".jpg"} />

      </div>)
    }

    return returnValue;
  }

  function getStmtWeight(idx) {
    var value = 0;

    for(var i=0;i<mapping.length;i++) {
      value = Math.max(value, mapping[i][idx]);
    }

    // console.log(value);

    return value;
  }

  function getStatements() {
    var retValue = [];

    // console.log(JSON.parse(JSON.stringify(mapping)));
    // console.log(JSON.parse(JSON.stringify(statement)));

    for(var i=0;i<statement.length;i++) {
      retValue.push(<tr className='statementTableRow' style={{backgroundColor: "rgba(0, 255, 0, " + getStmtWeight(i) + ")"}}  onClick={handleStatementClicked} index={i}>
        <td> {i} </td>
        <td> {statement[i]} </td>
      </tr>)
    }

    return retValue;
  }

  function handleStatementClicked(e) {
    console.log(e.target);

    var p = e.target.parentNode;

    var index = parseInt(p.getAttribute("index"));
    console.log(index);
    
    var highlightedSlides = document.querySelectorAll('.stmtHighlighted');

    for(var i=0;i<highlightedSlides.length;i++) {
      highlightedSlides[i].classList.remove("stmtHighlighted");
    }

    var slideObj = document.querySelectorAll('.statementTableRow[index="' + index + '"]')[0];

    console.log(slideObj);

    slideObj.classList.add("stmtHighlighted");

    setCurStatement(index);
  }

  function getScripts() {
    var returnValue = [];

    console.log(mapping);
    console.log(curStatement);
    console.log(script);

    if(curStatement != -1)
      console.log(mapping[0][curStatement]);

    for(var i=0;i<script.length;i++) {
      returnValue.push(<tr style={{backgroundColor: "rgba(0, 255, 0, " + (curStatement == -1 ? 0 : mapping[i][curStatement]) + ")"}} onClick={handleScriptClicked} index={i}>
        <td> {i} </td>
        <td> {script[i]} </td>
      </tr>
      )
    }

    return returnValue;
  }

  function handleScriptClicked(e) {
    console.log(e.target);

    var p = e.target.parentNode;

    var index = parseInt(p.getAttribute("index"));
    console.log(index);

    var highlightedSlides = document.querySelectorAll('.highlighted');

    for(var i=0;i<highlightedSlides.length;i++) {
      highlightedSlides[i].classList.remove("highlighted");
    }

    var slideObj = document.querySelectorAll('.slideImageDiv[index="' + index + '"]')[0];

    console.log(slideObj);

    slideObj.classList.add("highlighted");

    slideObj.scrollIntoView();
  }

  function handleHeatmapBtnClicked() {
    setHeatmapShow(!heatmapShow);
  }

  function showHeatmap() {
    var returnValue = [];

    for(var i=0;i<mapping.length;i++) {
      var inner = [];

      for(var j=0;j<mapping[i].length;j++) {
        inner.push(<td style={{backgroundColor: "rgba(0, 255, 0, " + mapping[i][j] + ")"}} script={i} stmt={j}> </td>)
      }

      returnValue.push(<tr> {inner} </tr>)
    }

    return <table className='heatmapTable'> {returnValue} </table>;
  }

  return (
    <div className="App">
      {
        heatmapShow ? 
          <div className='heatmapDiv'> 
            <div style={{margin: "10px"}}> y-axis: script, x-axis: paper </div>
            {showHeatmap()}
          </div>
          :
          ''
      }

      <div className='topBar'>
        <button id='heatmapBtn' onClick={handleHeatmapBtnClicked}> Show heatmap </button>
      </div>
      <div className='statementDiv'>
        <table className='statementTable'>
          <tr>
            <th className='index'> idx </th>
            <th> statement </th>
          </tr>
          {getStatements()}
        </table>
      </div>
      <div className='scriptDiv'>
        <table className='scriptTable'>
          <tr>
            <th className='index'> idx </th>
            <th> statement </th>
          </tr>
          {
            getScripts()
          }
        </table>
      </div>

      <div className='slideDiv'>
        {getSlides()}
      </div>

    </div>
  );
}

export default App;
