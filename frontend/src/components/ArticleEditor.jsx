import { useState } from 'react'

export default function ArticleEditor({ onGenerate, selectedMode, setSelectedMode, isLoading }) {
  const [form, setForm] = useState({
    author_name: '',
    title: '',
    topic: '',
    category: 'تعليمي',
  })

  const submit = (e) => {
    e.preventDefault()
    onGenerate({ ...form, mode: selectedMode })
  }

  return (
    <section className="card">
      <h2>مولد المقالات</h2>
      <form className="form-grid" onSubmit={submit}>
        <input placeholder="اسم الكاتب" value={form.author_name} onChange={(e) => setForm({ ...form, author_name: e.target.value })} required />
        <input placeholder="عنوان المقال" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
        <input placeholder="الموضوع" value={form.topic} onChange={(e) => setForm({ ...form, topic: e.target.value })} required />
        <input placeholder="التصنيف" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} required />

        <div className="mode-switch">
          <label>وضع الذكاء الاصطناعي:</label>
          <select value={selectedMode} onChange={(e) => setSelectedMode(e.target.value)}>
            <option value="auto">تلقائي</option>
            <option value="online">Online</option>
            <option value="offline">Offline</option>
          </select>
        </div>

        <button type="submit" disabled={isLoading}>{isLoading ? 'جارٍ التوليد...' : 'Generate Article'}</button>
      </form>
    </section>
  )
}
