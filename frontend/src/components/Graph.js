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
                .linkLabel((link) => `Relation: ${link.source.id} → ${link.target.id}`)
                .nodeAutoColorBy('id')
                .nodeRelSize(5)
            return () => graph._destructor && graph._destructor();
        }
    }, []);
    
    return (
        <div style={{ padding: '20px' }}>
            <h1 style={{ textAlign: 'center', color: '#4CAF50' }}>2D View</h1>
            <div id="graph"
                style={{
                    width: '100%',
                    height: '80vh',
                    border: '2px solid #4CAF50',
                    borderRadius: '10px',
                    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
                    backgroundColor: '#f9f9f9',
                    overflow: 'hidden',
                }}
            >
            </div>
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
                .linkLabel((link) => `Relation: ${link.source.id} → ${link.target.id}`)
                .linkDirectionalArrowLength(5)
                .linkDirectionalArrowRelPos(1);
            return () => graph._destructor && graph._destructor();

        }
    }, []);

    return (
        <div style={{ padding: '20px' }}>
            <h1 style={{ textAlign: 'center', color: '#4CAF50' }}>3D View</h1>
            <div id="3d-graph"
                style={{
                    width: '100%',
                    height: '80vh',
                    border: '2px solid #4CAF50',
                    borderRadius: '10px',
                    overflow: 'hidden',
                }}
            >
            </div>
        </div>
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
