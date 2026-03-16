export default function Header() {
  return (
    <header className="bg-white shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">🔍</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Bug Hunter</h1>
              <p className="text-xs text-gray-500">Infineon Hackathon 2026</p>
            </div>
          </div>
          
          <div className="flex items-center gap-6 text-sm text-gray-600">
            <a href="#" className="hover:text-primary-600 transition-colors">
              Documentation
            </a>
            <a href="#" className="hover:text-primary-600 transition-colors">
              About
            </a>
            <a href="https://github.com" className="hover:text-primary-600 transition-colors">
              GitHub
            </a>
          </div>
        </div>
      </div>
    </header>
  )
}
