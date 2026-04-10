export default function ExportManager({ onCreateMagazine, onExportPdf, onExportPng, magazines }) {
  return (
    <section className="card">
      <h2>إدارة التصدير</h2>
      <div className="actions">
        <button onClick={onCreateMagazine}>إنشاء نسخة جريدة</button>
        <button onClick={onExportPdf}>Export PDF</button>
        <button onClick={onExportPng}>Export PNG</button>
      </div>
      <ul>
        {magazines.map((m) => (
          <li key={m.id}>{m.name} - العدد {m.issue_number}</li>
        ))}
      </ul>
    </section>
  )
}
