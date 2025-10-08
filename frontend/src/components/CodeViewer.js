import React, { useState } from 'react'
import api from '../services/api'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

export default function CodeViewer({ taskId, versions = [] }) {
    const [open, setOpen] = useState(false)
    const [content, setContent] = useState('')
    const [title, setTitle] = useState('')

    const viewVersion = async (version) => {
        try {
            const res = await api.get(`/download_code/${taskId}/${version}`, { responseType: 'text' })
            setContent(res.data)
            setTitle(`v${version}`)
            setOpen(true)
        } catch (e) {
            alert('Failed to fetch code')
        }
    }

    const copy = () => {
        navigator.clipboard.writeText(content)
    }

    return (
        <div className="bg-gray-800 p-4 rounded">
            <h3 className="mb-2">Code Versions</h3>
            {versions.length === 0 && <div className="text-gray-400">No code uploaded yet.</div>}
            <ul>
                {versions.map(v => (
                    <li key={v.version} className="border-t border-gray-700 py-2 flex justify-between items-center">
                        <div>
                            <div className="font-medium">Version {v.version}</div>
                            <div className="text-sm text-gray-400">{v.files.join(', ')}</div>
                        </div>
                        <div>
                            <button onClick={() => viewVersion(v.version)} className="px-2 py-1 bg-blue-600 rounded mr-2">View</button>
                            <a href={`${api.defaults.baseURL}/download_code/${taskId}/${v.version}`} className="px-2 py-1 bg-gray-700 rounded" download>Download</a>
                        </div>
                    </li>
                ))}
            </ul>

            {open && (
                <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-60">
                    <div className="bg-gray-900 w-3/4 h-3/4 p-4 rounded">
                        <div className="flex justify-between items-center mb-2">
                            <h4 className="text-lg">Code {title}</h4>
                            <div className="space-x-2">
                                <button onClick={copy} className="px-2 py-1 bg-gray-700 rounded">Copy</button>
                                <button onClick={() => setOpen(false)} className="px-2 py-1 bg-red-600 rounded">Close</button>
                            </div>
                        </div>
                        <div className="overflow-auto h-full bg-black p-2">
                            <SyntaxHighlighter language="python" style={oneDark} customStyle={{ background: '#0b1220' }}>
                                {content}
                            </SyntaxHighlighter>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
