import React from 'react';
import styled from 'styled-components';
import { useTable, useExpanded } from 'react-table';
import { Link } from 'react-router-dom';
import Outline from './Outline';
import PipelineAccuracy from './PipelineAccuracy';


const TableStyles = styled.div`
  padding: 1rem;

  table {
    border-spacing: 0;
    border: 1px solid black;

    tr {
      :last-child {
        td {
          border-bottom: 0;
        }
      }
    }

    th,
    td {
      margin: 0;
      padding: 0.5rem;
      border-bottom: 1px solid black;
      border-right: 1px solid black;

      :last-child {
        border-right: 0;
      }
    }
  }
`;

const MODEL_NAME = 'modelName';

function Table(props) {

    const columns = props.columns;
    const data = props.data;
    const renderRowSubComponent = props.renderRowSubComponent;

    const {
        getTableProps,
        getTableBodyProps,
        headerGroups,
        rows,
        prepareRow,
        visibleColumns,
        state: { expanded },
    } = useTable(
        {
            columns,
            data,
        },
        useExpanded // We can useExpanded to track the expanded state
        // for sub components too!
    );

    return (
        <TableStyles>
            <table {...getTableProps()}>
                <thead>
                    {headerGroups.map(headerGroup => (
                        <tr {...headerGroup.getHeaderGroupProps()}>
                            {headerGroup.headers.map(column => (
                                <th {...column.getHeaderProps()}>{column.render('Header')}</th>
                            ))}
                        </tr>
                    ))}
                </thead>
                <tbody {...getTableBodyProps()}>
                    {rows.map((row, i) => {
                        prepareRow(row)
                        const rowKey = (row.getRowProps()).key;
                        return (
                            // Use a React.Fragment here so the table markup is still valid
                            <React.Fragment key={rowKey}>
                                <tr>
                                    {row.cells.map(cell => {
                                        if (cell.column.id === MODEL_NAME) {
                                            const evaluationResult = cell.row.original.evaluationResult;
                                            const modelConfig = evaluationResult.modelConfig;
                                            return (
                                                <td
                                                    {...cell.getCellProps({
                                                    })}
                                                >
                                                    <Link to={{
                                                        search: `?mode=${1}`
                                                            + `&similarityType=${modelConfig.similarityType}`
                                                            + `&outliningApproach=${modelConfig.outliningApproach}`
                                                            + `&applyThresholding=${modelConfig.thresholding}`,
                                                        state: null,
                                                    }}>
                                                        {cell.render('Cell')}
                                                    </Link>
                                                </td>
                                            )
                                        }
                                            console.log();
                                        return (
                                            <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
                                        )
                                    })}
                                </tr>
                                {/*
                                If the row is in an expanded state, render a row with a
                                column that fills the entire length of the table.
                                */}
                                {row.isExpanded ? (
                                    <tr>
                                        <td colSpan={visibleColumns.length}>
                                            {/*
                                                Inside it, call our renderRowSubComponent function. In reality,
                                                you could pass whatever you want as props to
                                                a component like this, including the entire
                                                table instance. But for this example, we'll just
                                                pass the row
                                            */}
                                            {renderRowSubComponent({ row })}
                                        </td>
                                    </tr>
                                ) : null}
                            </React.Fragment>
                        )
                    })}
                </tbody>
            </table>
            <br />
            <div>Showing the first 20 results of {rows.length} rows</div>
        </TableStyles>
    );
}

function EvaluationTable(props) {
    const evaluationResults = props?.evaluationResults;

    const presentationsCnt = 0;

    const presentationIds = React.useMemo(() => {
        let retList = []
        for (let presentationId = 1; presentationId <= presentationsCnt; presentationId++){
            retList.push(presentationId);
        }
        return retList;
    }, [presentationsCnt]);

    const columns = React.useMemo(() => {
        const generateInnerColumns = (header, accessor) => {
            let innerColumns = presentationIds.map((presentationId, idx) => {
                return {
                    Header: header + presentationId.toString(),
                    accessor: accessor + "_" + presentationId.toString(),
                };
            });
            innerColumns.push({
                Header: header + "avg",
                accessor: accessor + "_avg",
            });
            return innerColumns;
        }
        return [
            {
                // Make an expander cell
                Header: () => null, // No header
                id: 'expander', // It needs an ID
                Cell: ({ row }) => (
                    // Use Cell to render an expander for each row.
                    // We can use the getToggleRowExpandedProps prop-getter
                    // to build the expander.
                    <span {...row.getToggleRowExpandedProps()}>
                        {row.isExpanded ? '👇' : '👉'}
                    </span>
                ),
            },{
                Header: 'Model Name',
                accessor: MODEL_NAME,
            }, {
                Header: 'Video Overview',
                columns: generateInnerColumns("", "boundariesAccuracy"),
            }, {
                Header: 'Time Accuracy',
                columns: generateInnerColumns("", "timeAccuracy"),
            }, {
                Header: 'Structural Accuracy',
                columns: generateInnerColumns("", "structureAccuracy"),
            }, {
                Header: 'Mapping Accuracy',
                columns: generateInnerColumns("", "mappingAccuracy"),
            },
        ];
    }, [presentationIds]);

    const data = evaluationResults ? evaluationResults.map((evaluationResult, idx) => {
        let modelName = "";
        for (let feature in evaluationResult.modelConfig) {
            modelName += evaluationResult.modelConfig[feature] + ", "
        }

        const generateInnerData = (arr, accessor) => {
            const presentationData = arr[0];
            const innerData = {};
            for (let i = 0; i < presentationIds.length; i++) {
                const key = accessor + "_" + presentationIds[i].toString();
                innerData[key] = presentationData[i];
            }

            const avg = arr[1];
            innerData[accessor + "_avg"] = avg;
            return innerData;
        }

        let dataObject = {
            idx,
            modelName,
            evaluationResult,
        };

        for (let accessor in evaluationResult.result) {
            dataObject = {
                ...dataObject,
                ...(generateInnerData(evaluationResult.result[accessor], accessor)),
            };
        }

        return dataObject;
    }) : [];

    // Create a function that will render our row sub components
    const renderRowSubComponent = React.useCallback(
        ({ row }) => {        
            return <div>
                {JSON.stringify(row.original.evaluationResult, null, 2)}
            </div>
        },[]
    );

    return (
        <Table
        columns={columns}
        data={data}
        renderRowSubComponent={renderRowSubComponent}
        />
    );
}

export default EvaluationTable;
export {
    Table
};
