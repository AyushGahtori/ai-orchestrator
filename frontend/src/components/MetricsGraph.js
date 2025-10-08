import React from 'react'
import { Line } from 'react-chartjs-2'

export default function MetricsGraph() {
    // Mocked data for demo; future: fetch /get_results
    const data = {
        labels: ['1', '2', '3', '4', '5'],
        datasets: [
            { label: 'Accuracy', data: [0.6, 0.7, 0.75, 0.8, 0.82], borderColor: 'rgba(34,197,94,1)', tension: 0.2 }
        ]
    }
    return (
        <div className="bg-gray-800 p-4 rounded">
            <h3 className="mb-2">Accuracy / Loss (mock)</h3>
            <div style={{ height: 220 }}>
                <Line data={data} />
            </div>
        </div>
    )
}
