import React, { useEffect } from 'react'
import ForceGraph from 'force-graph';
import ForceGraph3D from '3d-force-graph';
import graphData from '../dependency_graph.json';

const Graph2D = () => {
    useEffect(() => {
        const graphElement = document.getElementById('graph');
        if (graphElement) {
            const graph = new ForceGraph(graphElement)
                .graphData(graphData)
                .nodeId('id')
                .linkSource('source')
                .linkTarget('target')
                .nodeLabel((node) => node.id)
                .linkWidth(2)
                .nodeAutoColorBy('id')
                .nodeRelSize(5);
            return () => graph._destructor && graph._destructor();
        }
    }, []);

    return (
        <div id="graph"
            style={{
                width: '100%',
                height: '100vh',
                border: '2px solid #4CAF50',
                borderRadius: '10px',
                boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
                backgroundColor: '#f9f9f9',
                overflow: 'hidden',
            }}
        >
            {/* Graph */}
        </div>
    );
};

const Graph3D = () => {
    useEffect(() => {
        const graphElement = document.getElementById('3d-graph');
        if (graphElement) {
            const graph = new ForceGraph3D(graphElement)
                .graphData(graphData)
                .nodeId('id')
                .linkSource('source')
                .linkTarget('target')
                .nodeLabel((node) => node.id)
                .nodeAutoColorBy('id')
                .nodeRelSize(8)
                .linkWidth(2)
                .linkDirectionalArrowLength(5)
                .linkDirectionalArrowRelPos(1);
            return () => graph._destructor && graph._destructor();

        }
    }, []);

    return (
        <div
            id="3d-graph"
            style={{
                width: '100%',
                height: '100vh',
                border: '2px solid #4CAF50',
                borderRadius: '10px',
                boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
                backgroundColor: '#f9f9f9',
                overflow: 'hidden',
            }}
        >3D </div>
    );
};

const Graph = () => {
    return (
        <>
            <Graph2D />
            <Graph3D />
        </>
    )
}

export default Graph
