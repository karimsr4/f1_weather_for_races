import React from 'react';
import Plot from 'react-plotly.js';

const TimeSeriesChart = ({ data, unit, title, start_time, end_time }) => {
    // Check if data is empty or null
    if (!data || !data.time || !data.values || data.time.length === 0 || data.values.length === 0) {
        return null;
    }

    // Extract labels (time) and data points (variable values) from the data object
    const labels = data.time;
    const values = data.values;

    // Create the trace for the line chart
    const trace = {
        x: labels,
        y: values,
        mode: 'lines+markers', // Add markers to the line chart
        type: 'scatter',
        line: { color: 'rgb(255,0,0)' },
        name: title,
    };

    // Define layout options for the chart
    const layout = {
        title: title,
        xaxis: {
            title: 'Date/Time',
            type: 'date',
        },
        yaxis: {
            title: unit,
        },
        shapes: [
            // Highlight the period between start time and end time using a rectangle
            {
                type: 'rect',
                xref: 'x',
                yref: 'paper',
                x0: start_time,
                y0: 0,
                x1: end_time,
                y1: 1,
                fillcolor: '#d3d3d3',
                opacity: 0.2,
                line: { width: 0 },
            },
        ],
        height: 500,
        width: 500,
    };

    // Create the data array containing the trace
    const chartData = [trace];

    return <Plot data={chartData} layout={layout} />;
};

export default TimeSeriesChart;
