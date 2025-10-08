import React, { useEffect, useState, useRef } from 'react'

export default function LiveMonitor() {
    const [lines, setLines] = useState(["Initializing run..."])
    const [running, setRunning] = useState(false)
    const intervalRef = useRef(null)

    useEffect(() => {
        if (running) {
            intervalRef.current = setInterval(() => {
                setLines(l => [...l, `log ${l.length + 1}: sample output`].slice(-200))
            }, 800)
        }
        return () => clearInterval(intervalRef.current)
    }, [running])

    return (
        <div className="bg-gray-800 p-4 rounded">
            <div className="flex justify-between items-center mb-2">
                <h3>Live Run Monitor (mock)</h3>
                <div className="space-x-2">
                    <button onClick={() => setRunning(true)} className="px-2 py-1 bg-green-600 rounded">Start</button>
                    <button onClick={() => setRunning(false)} className="px-2 py-1 bg-red-600 rounded">Stop</button>
                    <button onClick={() => setLines([])} className="px-2 py-1 bg-gray-700 rounded">Reset</button>
                </div>
            </div>
            <div className="bg-black text-green-400 font-mono p-2 h-64 overflow-auto">
                {lines.map((l, i) => (<div key={i}>{l}</div>))}
            </div>
        </div>
    )
}
