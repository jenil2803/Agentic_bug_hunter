'use client'

import { useState } from 'react'
import FileUpload from '@/components/FileUpload'
import ResultsTable from '@/components/ResultsTable'
import Dashboard from '@/components/Dashboard'
import Header from '@/components/Header'

export default function Home() {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFileUpload = async (file: File) => {
    setLoading(true)
    setError(null)

    try {
      // In production, this would send to a backend API
      // For now, we'll simulate the process
      console.log('Uploading file:', file.name)
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Mock results
      const mockResults = [
        {
          ID: '1',
          'Bug Line': 5,
          Explanation: 'vForce set to 35V which exceeds the allowed range of 30V for AVI64'
        },
        {
          ID: '2',
          'Bug Line': 3,
          Explanation: 'iClamp low and high values are exchanged, should be (-50mA, 50mA)'
        }
      ]
      
      setResults(mockResults)
    } catch (err) {
      setError('Error processing file. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadCSV = () => {
    if (results.length === 0) return

    // Convert results to CSV
    const headers = ['ID', 'Bug Line', 'Explanation']
    const csvContent = [
      headers.join(','),
      ...results.map((row: any) => 
        [row.ID, row['Bug Line'], `"${row.Explanation}"`].join(',')
      )
    ].join('\n')

    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `bug_detection_results_${new Date().getTime()}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🐛 Agentic Bug Hunter
          </h1>
          <p className="text-lg text-gray-600">
            AI-powered bug detection for C++ SmartRDI code
          </p>
        </div>

        {/* Upload Section */}
        <div className="mb-8">
          <FileUpload onUpload={handleFileUpload} loading={loading} />
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}
        </div>

        {/* Dashboard */}
        {results.length > 0 && (
          <>
            <Dashboard results={results} />
            
            {/* Results Table */}
            <div className="mt-8">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-semibold text-gray-900">
                  Detection Results
                </h2>
                <button
                  onClick={handleDownloadCSV}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Download CSV
                </button>
              </div>
              <ResultsTable results={results} />
            </div>
          </>
        )}

        {/* Empty State */}
        {!loading && results.length === 0 && (
          <div className="text-center py-16">
            <div className="inline-block p-8 bg-white rounded-full shadow-lg mb-4">
              <svg className="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              No Results Yet
            </h3>
            <p className="text-gray-500">
              Upload a CSV file to start detecting bugs
            </p>
          </div>
        )}
      </main>
    </div>
  )
}
