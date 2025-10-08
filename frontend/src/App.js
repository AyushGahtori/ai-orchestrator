import React from 'react'
import Dashboard from './components/Dashboard'
import TaskDetail from './components/TaskDetail'

export default function App() {
    const [page, setPage] = React.useState('dashboard')
    const [selectedTask, setSelectedTask] = React.useState(null)

    return (
        <div className="min-h-screen bg-gray-900 text-gray-100">
            <header className="p-4 border-b border-gray-800">
                <div className="container mx-auto flex items-center justify-between">
                    <h1 className="text-2xl font-semibold">AI Orchestrator</h1>
                    <div>
                        <button onClick={() => { setPage('dashboard') }} className="px-3 py-1 bg-gray-800 rounded">Dashboard</button>
                    </div>
                </div>
            </header>
            <main className="container mx-auto p-6">
                {page === 'dashboard' && (
                    <Dashboard onViewTask={(t) => { setSelectedTask(t); setPage('task') }} />
                )}
                {page === 'task' && selectedTask && (
                    <TaskDetail task={selectedTask} onBack={() => setPage('dashboard')} />
                )}
            </main>
        </div>
    )
}
