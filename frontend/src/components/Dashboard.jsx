export default function Dashboard({ articles, onSelectArticle, selectedArticleId, onDelete }) {
  return (
    <section className="card">
      <h2>لوحة المقالات</h2>
      <div className="list">
        {articles.length === 0 && <p>لا توجد مقالات بعد.</p>}
        {articles.map((article) => (
          <article key={article.id} className={`list-item ${selectedArticleId === article.id ? 'active' : ''}`}>
            <button className="link" onClick={() => onSelectArticle(article.id)}>{article.title}</button>
            <small>{article.author_name}</small>
            <button className="danger" onClick={() => onDelete(article.id)}>حذف</button>
          </article>
        ))}
      </div>
    </section>
  )
}
