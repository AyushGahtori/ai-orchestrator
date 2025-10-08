import React, { useEffect, useState } from 'react'
import api from '../services/api'

export default function Dashboard({ onViewTask }) {
    const [tasks, setTasks] = useState([])
    const [stats, setStats] = useState({})

    useEffect(() => {
        api.get('/get_tasks').then(r => setTasks(r.data.tasks)).catch(() => setTasks([]))
        api.get('/stats').then(r => setStats(r.data)).catch(() => { })
    }, [])

    return (
        <div>
            <div className="grid grid-cols-4 gap-4 mb-4">
                <div className="bg-gray-800 p-4 rounded">
                    <div className="text-sm text-gray-400">Total Tasks</div>
                    <div className="text-2xl">{stats.total_tasks ?? '-'}</div>
                </div>
                <div className="bg-gray-800 p-4 rounded">
                    <div className="text-sm text-gray-400">Completed</div>
                    <div className="text-2xl">{stats.completed_tasks ?? '-'}</div>
                </div>
                <div className="bg-gray-800 p-4 rounded">
                    <div className="text-sm text-gray-400">Average Accuracy</div>
                    <div className="text-2xl">{stats.avg_accuracy ? (stats.avg_accuracy.toFixed(2)) : '-'}</div>
                </div>
                <div className="bg-gray-800 p-4 rounded">
                    <div className="text-sm text-gray-400">Active Containers</div>
                    <div className="text-2xl">{stats.active_containers ?? '-'}</div>
                </div>
            </div>
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-medium">Tasks</h2>
                <button className="px-3 py-1 bg-green-600 rounded" onClick={async () => {
                    // demo: create a fake task using demo API key
                    const payload = { name: 'Demo Task ' + Date.now(), dataset: 'mnist', description: 'Auto-created demo', creator_agent: 'generator' }
                    await api.post('/upload_task', payload)
                    const res = await api.get('/get_tasks')
                    setTasks(res.data.tasks)
                }}>Create Demo Task</button>
            </div>
            <div className="bg-gray-800 rounded p-4">
                <table className="w-full text-left text-sm">
                    <thead>
                        <tr className="text-gray-400">
                            <th>Task</th>
                            <th>Dataset</th>
                            <th>Status</th>
                            <th>Creator</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        {tasks.map(t => (
                            <tr key={t.id} className="border-t border-gray-700">
                                <td className="py-2">{t.name}</td>
                                <td>{t.dataset}</td>
                                <td>{t.status}</td>
                                <td>{t.creator_agent}</td>
                                <td><button className="px-2 py-1 bg-blue-600 rounded" onClick={() => onViewTask(t)}>View</button></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
