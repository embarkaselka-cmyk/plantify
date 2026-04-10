import { useEffect, useMemo, useState } from 'react'
import ArticleEditor from './components/ArticleEditor'
import Dashboard from './components/Dashboard'
import MagazinePreview from './components/MagazinePreview'
import Settings from './components/Settings'
import ExportManager from './components/ExportManager'
import {
  createMagazine,
  deleteArticle,
  exportMagazinePdf,
  exportMagazinePng,
  fetchArticles,
  fetchMagazines,
  generateArticle,
} from './services/api'

export default function App() {
  const [articles, setArticles] = useState([])
  const [magazines, setMagazines] = useState([])
  const [selectedArticleId, setSelectedArticleId] = useState(null)
  const [selectedMode, setSelectedMode] = useState('auto')
  const [loading, setLoading] = useState(false)
  const [branding, setBranding] = useState({
    primary_color: '#2563eb',
    secondary_color: '#0f172a',
    logo_url: '',
  })

  const selectedArticle = useMemo(() => articles.find((a) => a.id === selectedArticleId), [articles, selectedArticleId])

  const loadData = async () => {
    const [a, m] = await Promise.all([fetchArticles(), fetchMagazines()])
    setArticles(a)
    setMagazines(m)
    if (a.length && !selectedArticleId) setSelectedArticleId(a[0].id)
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleGenerate = async (payload) => {
    setLoading(true)
    try {
      await generateArticle(payload)
      await loadData()
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    await deleteArticle(id)
    await loadData()
  }

  const handleCreateMagazine = async () => {
    await createMagazine({
      name: 'نادي الصحفي الصغير',
      issue_number: `${magazines.length + 1}`,
      article_ids: articles.map((a) => a.id).slice(0, 6),
      ...branding,
    })
    await loadData()
  }

  const latestMagazine = magazines[0]

  const download = (file) => window.open(`http://127.0.0.1:8000/magazines/download?path=${encodeURIComponent(file)}`, '_blank')

  const handleExportPdf = async () => {
    if (!latestMagazine) return alert('أنشئ جريدة أولًا')
    const result = await exportMagazinePdf(latestMagazine.id)
    download(result.file)
  }

  const handleExportPng = async () => {
    if (!latestMagazine) return alert('أنشئ جريدة أولًا')
    const result = await exportMagazinePng(latestMagazine.id)
    download(result.file)
  }

  return (
    <div className="container" dir="rtl">
      <header className="hero">
        <h1>نادي الصحفي الصغير - Newspaper Generator</h1>
      </header>

      <div className="grid">
        <Dashboard articles={articles} onSelectArticle={setSelectedArticleId} selectedArticleId={selectedArticleId} onDelete={handleDelete} />
        <ArticleEditor onGenerate={handleGenerate} selectedMode={selectedMode} setSelectedMode={setSelectedMode} isLoading={loading} />
        <Settings branding={branding} setBranding={setBranding} />
        <ExportManager onCreateMagazine={handleCreateMagazine} onExportPdf={handleExportPdf} onExportPng={handleExportPng} magazines={magazines} />
        <MagazinePreview article={selectedArticle} branding={branding} />
      </div>
    </div>
  )
}
