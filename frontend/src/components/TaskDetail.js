import React, { useEffect, useState, useRef } from 'react'
import api from '../services/api'
import AgentChat from './AgentChat'
import CodeViewer from './CodeViewer'
import MetricsGraph from './MetricsGraph'
import LiveMonitor from './LiveMonitor'

export default function TaskDetail({ task, onBack }) {
    const [tab, setTab] = useState('overview')
    const [codes, setCodes] = useState([])
    const [messages, setMessages] = useState([])
    const [logFiles, setLogFiles] = useState([])
    const [selectedLog, setSelectedLog] = useState(null)
    const pollRef = useRef(null)

    const fetchAll = async () => {
        api.get(`/get_code/${task.id}`).then(r => setCodes(r.data.versions || [])).catch(() => { })
        api.get(`/get_messages/${task.id}`).then(r => setMessages(r.data.messages || [])).catch(() => { })
        api.get(`/get_results/${task.id}`).then(r => {/* future: show */ }).catch(() => { })
        api.get(`/get_feedback/${task.id}`).then(r => {/* future: show */ }).catch(() => { })
    }

    useEffect(() => {
        fetchAll()
        pollRef.current = setInterval(fetchAll, 10000)
        return () => clearInterval(pollRef.current)
    }, [task])

    return (
        <div>
            <button onClick={onBack} className="mb-4 px-2 py-1 bg-gray-800 rounded">Back</button>
            <h2 className="text-2xl mb-2">{task.name}</h2>
            <div className="flex space-x-3 mb-4">
                <button onClick={() => setTab('overview')} className="px-3 py-1 bg-gray-800 rounded">Overview</button>
                <button onClick={() => setTab('chat')} className="px-3 py-1 bg-gray-800 rounded">Agent Conversation</button>
                <button onClick={() => setTab('code')} className="px-3 py-1 bg-gray-800 rounded">Code Versions</button>
                <button onClick={() => setTab('logs')} className="px-3 py-1 bg-gray-800 rounded">Logs & Metrics</button>
                <button onClick={() => setTab('containers')} className="px-3 py-1 bg-gray-800 rounded">Containers</button>
            </div>

            {tab === 'overview' && (
                <div className="bg-gray-800 p-4 rounded">
                    <p>{task.description}</p>
                    <p className="text-sm text-gray-400 mt-2">Creator: {task.creator_agent}</p>
                </div>
            )}

            {tab === 'chat' && (
                <AgentChat taskId={task.id} initialMessages={messages} />
            )}

            {tab === 'code' && (
                <CodeViewer taskId={task.id} versions={codes} />
            )}

            {tab === 'logs' && (
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <h3 className="mb-2">Saved Logs</h3>
                        <div className="bg-gray-800 p-4 rounded">
                            <button className="mb-2 px-2 py-1 bg-blue-600 rounded" onClick={async () => {
                                const res = await api.get(`/get_logs/${task.id}`)
                                setLogFiles(res.data.logs || [])
                            }}>Refresh Logs</button>
                            <div className="space-y-2 h-64 overflow-auto">
                                {logFiles.map(l => (
                                    <div key={l.filename} className="border-t border-gray-700 p-2">
                                        <div className="flex justify-between">
                                            <div>{l.filename}</div>
                                            <div className="space-x-2">
                                                <button onClick={async () => {
                                                    const res = await api.get(`/download_log/${task.id}/${l.filename}`, { responseType: 'text' })
                                                    setSelectedLog({ name: l.filename, content: res.data })
                                                }} className="px-2 py-1 bg-gray-700 rounded">Open</button>
                                                <a className="px-2 py-1 bg-gray-700 rounded" href={`${api.defaults.baseURL}/download_log/${task.id}/${l.filename}`}>Download</a>
                                            </div>
                                        </div>
                                        <div className="text-sm text-gray-400">Preview: {l.preview ? l.preview.slice(0, 120) : ''}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                    <div>
                        <h3 className="mb-2">Log Viewer</h3>
                        <div className="bg-black text-green-400 font-mono p-2 h-96 overflow-auto">
                            {selectedLog ? selectedLog.content : 'Open a log to view its content here.'}
                        </div>
                    </div>
                </div>
            )}

            {tab === 'containers' && (
                <div className="bg-gray-800 p-4 rounded">
                    <p>Containers are simulated. Use "Spawn New Run" to create a mock container.</p>
                    <button className="mt-2 px-3 py-1 bg-green-600 rounded" onClick={async () => {
                        const res = await api.post('/spawn_container', null, { params: { task_id: task.id } })
                        alert('Spawned: ' + JSON.stringify(res.data))
                    }}>Spawn New Run</button>
                </div>
            )}
        </div>
    )
}
