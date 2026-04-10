import requests

from ..config import get_settings


class OfflineAIService:
    def __init__(self):
        self.settings = get_settings()

    def generate_article(self, author_name: str, title: str, topic: str, category: str) -> str:
        prompt = (
            "اكتب مقالًا عربيًا صحفيًا احترافيًا للأطفال. "
            "رتّب المخرجات إلى: مقدمة، تفاصيل، خاتمة، مع أسلوب واضح. "
            f"اسم الكاتب: {author_name}. العنوان: {title}. الموضوع: {topic}. التصنيف: {category}."
        )

        try:
            response = requests.post(
                f"{self.settings.ollama_host}/api/generate",
                json={
                    "model": self.settings.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=60,
            )
            response.raise_for_status()
            payload = response.json()
            text = payload.get("response", "").strip()
            return text or self._fallback(author_name, title, topic, category)
        except Exception:
            return self._fallback(author_name, title, topic, category)

    @staticmethod
    def _fallback(author_name: str, title: str, topic: str, category: str) -> str:
        return (
            f"# {title}\n\n"
            f"بقلم: {author_name}\n\n"
            f"تصنيف: {category}\n\n"
            f"الموضوع: {topic}\n\n"
            "في هذا العدد، نعرض تقريرًا مبسطًا يساعد القارئ الصغير على فهم الموضوع بطريقة ممتعة. "
            "كما نبرز أهمية الاستقصاء والتحقق من المصادر قبل نشر الخبر. "
            "وفي النهاية، يبقى الصحفي الصغير صوتًا واعيًا ينشر المعرفة والإيجابية."
        )
