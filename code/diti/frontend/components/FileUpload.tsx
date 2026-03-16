'use client'

import { useCallback } from 'react'

interface FileUploadProps {
  onUpload: (file: File) => void
  loading: boolean
}

export default function FileUpload({ onUpload, loading }: FileUploadProps) {
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file && file.name.endsWith('.csv')) {
      onUpload(file)
    }
  }, [onUpload])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      onUpload(file)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <label
        htmlFor="file-upload"
        className="flex flex-col items-center justify-center w-full h-48 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-primary-500 transition-colors"
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
      >
        {loading ? (
          <div className="flex flex-col items-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mb-4"></div>
            <p className="text-gray-600 font-medium">Analyzing code...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <svg className="w-12 h-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p className="text-gray-700 font-medium mb-1">
              <span className="text-primary-600">Click to upload</span> or drag and drop
            </p>
            <p className="text-sm text-gray-500">CSV files only</p>
          </div>
        )}
        <input
          id="file-upload"
          type="file"
          accept=".csv"
          className="hidden"
          onChange={handleChange}
          disabled={loading}
        />
      </label>
    </div>
  )
}
