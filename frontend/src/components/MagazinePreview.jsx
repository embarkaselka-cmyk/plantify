export default function MagazinePreview({ article, branding }) {
  return (
    <section className="card preview">
      <h2>معاينة مباشرة</h2>
      {article ? (
        <div className="newspaper" style={{ '--primary': branding.primary_color, '--secondary': branding.secondary_color }}>
          <header>
            {branding.logo_url && <img src={branding.logo_url} alt="logo" className="logo" />}
            <h1>{article.title}</h1>
            <p>بقلم: {article.author_name}</p>
          </header>
          <div className="columns">
            {article.content.split('\n').map((line, i) => <p key={i}>{line}</p>)}
          </div>
        </div>
      ) : (
        <p>اختر مقالًا لعرضه بتنسيق الجريدة.</p>
      )}
    </section>
  )
}
