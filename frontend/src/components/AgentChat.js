import React, { useState } from 'react'
import api from '../services/api'

export default function AgentChat({ taskId, initialMessages = [] }) {
    const [messages, setMessages] = useState(initialMessages)
    const [text, setText] = useState('')
    const [sender, setSender] = useState('generator')

    const post = async () => {
        if (!text) return
        await api.post('/upload_message', { task_id: taskId, sender, content: text })
        const res = await api.get(`/get_messages/${taskId}`)
        setMessages(res.data.messages)
        setText('')
    }

    return (
        <div className="bg-gray-800 p-4 rounded">
            <div className="space-y-2 h-64 overflow-auto mb-3">
                {messages.map(m => (
                    <div key={m.id} className="p-2 border-b border-gray-700">
                        <div className="text-sm text-gray-400">{m.sender} {'->'} {m.receiver || 'all'} <span className="ml-2 text-xs">{m.created_at || ''}</span></div>
                        <div className="mt-1">{m.content}</div>
                    </div>
                ))}
            </div>
            <div className="flex space-x-2">
                <select value={sender} onChange={e => setSender(e.target.value)} className="bg-gray-900 p-2 rounded">
                    <option value="generator">Generator</option>
                    <option value="coder">Coder</option>
                    <option value="evaluator">Evaluator</option>
                </select>
                <input value={text} onChange={e => setText(e.target.value)} className="flex-1 p-2 bg-gray-900 rounded" placeholder="Message content" />
                <button onClick={post} className="px-3 py-1 bg-blue-600 rounded">Send</button>
            </div>
        </div>
    )
}
