import React, { useState } from 'react'

import SingleValue from '@splunk/visualizations/SingleValue'
import Line from '@splunk/visualizations/Line'
import Area from '@splunk/visualizations/Area'
import Column from '@splunk/visualizations/Column'
import Pie from '@splunk/visualizations/Pie'
import Bar from '@splunk/visualizations/Bar'
import Scatter from '@splunk/visualizations/Scatter'
import Bubble from '@splunk/visualizations/Bubble'
import Table from '@splunk/visualizations/Table'
import Events from '@splunk/visualizations/Events'
import Punchcard from '@splunk/visualizations/Punchcard'
import LinkGraph from '@splunk/visualizations/LinkGraph'

import { render } from 'react-dom'
import { SplunkThemeProvider } from '@splunk/themes';

import VizSelector from './components'
import styled from 'styled-components'

const StyledDiv = styled.div`
@font-face {
    font-family: Splunk Platform Sans;
    src: local('Arial');
} 
`

function VizViewer({data, backgroundColor, initialVizType, visualizationOptions}) {

    let initialType = "events"
 
    if (initialVizType !== undefined) {
        initialType = initialVizType
    }

    let options = {"backgroundColor": backgroundColor}

    if (visualizationOptions !== undefined) {
        options = {options, ...visualizationOptions}
    }

    const [vizType, setVizType] = useState(initialType)

    const dataSources = {
        primary: {
            requestParams: {
                offset: 0,
                count: 1
            },
            data: {
                columns: [["test"]],
                fields: [{"name": "host"}],
                meta: {
                    totalCount: 1
                }
            }
        }
    }

    dataSources.primary.data.fields = data["fields"]
    dataSources.primary.data.columns = data["columns"]
    dataSources.primary.data.meta.totalCount = data["columns"].length

    console.log(dataSources)
    
    const handleChangeVizType = (value) => {
        setVizType(value)
    };

    let viz = <SingleValue
    dataSources={dataSources}
    height={100}
    options={options}
    ></SingleValue>

    if (vizType == "line") {
        viz = <Line dataSources={dataSources} height={300}></Line>
    } else if (vizType == "area") {
        viz = <Area dataSources={dataSources} height={300}></Area>
    } else if (vizType == "column") {
        viz = <Column dataSources={dataSources} height={300}></Column>
    } else if (vizType == "bar") {
        viz = <Bar dataSources={dataSources} height={300}></Bar>
    } else if (vizType == "pie") {
        viz = <Pie dataSources={dataSources} height={300}></Pie>
    } else if (vizType == "scatter") {
        viz = <Scatter dataSources={dataSources} height={300}></Scatter>
    } else if (vizType == "bubble") {
        viz = <Bubble dataSources={dataSources} height={300}></Bubble>
    } else if (vizType == "table") {
        viz = <Table dataSources={dataSources} height={400}></Table>
    } else if (vizType == "punchcard") {
        viz = <Punchcard dataSources={dataSources} height={300}></Punchcard>
    } else if (vizType == "link") {
        viz = <LinkGraph dataSources={dataSources} height={400}></LinkGraph>
    } else if (vizType == "events") {
        viz = <Events dataSources={dataSources} options={{...options, "showFieldSummary": false}} height={400}></Events>
    }

    return (
        <div>
        <VizSelector isCollapsed={initialVizType !== undefined} onChange={handleChangeVizType} value={vizType} style={{"paddingBottom": "10px"}}></VizSelector>

        {viz}
        
        </div>
    )
}

export const activate= (_) => ({
    renderOutputItem(data, element){
        console.log("Activating Viz Renderer")
        const {results, _meta} = data.json()

        const visualizationPreference = _meta.cellMeta?.splunk?.visualizationPreference
        const visualizationOptions = _meta.cellMeta?.splunk?.visualizationOptions

        console.log(visualizationOptions)
        //element.innerText = "H" + JSON.stringify(data.json())

        let colorScheme = "dark"
        if (_meta["colorMode"] == "light" || _meta["colorMode"] == "high contrast light" || _meta["colorMode"] == 1) {
            colorScheme = "light"
        }

        render(
            <SplunkThemeProvider family="prisma" colorScheme={colorScheme} density="compact">
                <StyledDiv>
                <VizViewer visualizationOptions={visualizationOptions} initialVizType={visualizationPreference} data={results} backgroundColor={_meta["backgroundColor"]}></VizViewer>
                </StyledDiv>
        </SplunkThemeProvider>, element)
    },
})