export default function Settings({ branding, setBranding }) {
  const update = (field, value) => setBranding({ ...branding, [field]: value })

  const handleLogo = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => update('logo_url', reader.result)
    reader.readAsDataURL(file)
  }

  return (
    <section className="card">
      <h2>الهوية البصرية</h2>
      <div className="form-grid">
        <label>اللون الأساسي <input type="color" value={branding.primary_color} onChange={(e) => update('primary_color', e.target.value)} /></label>
        <label>اللون الثانوي <input type="color" value={branding.secondary_color} onChange={(e) => update('secondary_color', e.target.value)} /></label>
        <label>رفع الشعار <input type="file" accept="image/*" onChange={handleLogo} /></label>
      </div>
    </section>
  )
}
