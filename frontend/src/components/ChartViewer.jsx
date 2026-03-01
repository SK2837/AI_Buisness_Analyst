import React from 'react';
import Plot from 'react-plotly.js';

const ChartViewer = ({ chartJson }) => {
    if (!chartJson) return null;

    return (
        <div className="card" style={{ height: '520px' }}>
            <Plot
                data={chartJson.data}
                layout={{
                    ...chartJson.layout,
                    autosize: true,
                    margin: { t: 50, r: 20, l: 50, b: 50 },
                    font: { family: '"IBM Plex Sans", sans-serif' },
                }}
                useResizeHandler={true}
                style={{ width: '100%', height: '100%' }}
                config={{ responsive: true, displayModeBar: false }}
            />
        </div>
    );
};

export default ChartViewer;
