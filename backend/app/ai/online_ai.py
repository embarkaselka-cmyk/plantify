from openai import OpenAI

from ..config import get_settings


class OnlineAIService:
    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key) if self.settings.openai_api_key else None

    def generate_article(self, author_name: str, title: str, topic: str, category: str) -> str:
        if not self.client:
            return self._fallback(author_name, title, topic, category)

        prompt = (
            "اكتب مقالًا صحفيًا احترافيًا باللغة العربية الفصحى مخصصًا للأطفال واليافعين. "
            "يجب أن يكون منظمًا بعناوين فرعية، مقدمة، متن، وخاتمة، مع لغة جذابة ودقيقة. "
            f"اسم الكاتب: {author_name}. العنوان: {title}. الموضوع: {topic}. التصنيف: {category}."
        )

        response = self.client.responses.create(
            model="gpt-4.1-mini",
            input=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.output_text.strip()

    @staticmethod
    def _fallback(author_name: str, title: str, topic: str, category: str) -> str:
        return (
            f"# {title}\n\n"
            f"بقلم: {author_name}\n\n"
            f"**التصنيف:** {category}  \n"
            f"**الموضوع:** {topic}\n\n"
            "مقدمة:\n"
            "يقدم هذا المقال نظرة صحفية مبسطة ومفيدة تساعد القراء الصغار على فهم القضية المطروحة.\n\n"
            "المتن:\n"
            "تشير الوقائع إلى أهمية الموضوع في حياة المجتمع، حيث يساهم في بناء الوعي وتعزيز التفكير النقدي. "
            "كما أن دور الصحافة الناشئة يتمثل في نقل المعلومات بدقة، والبحث عن المصادر الموثوقة، وتقديم "
            "أمثلة قريبة من واقع القراء.\n\n"
            "خاتمة:\n"
            "الصحفي الصغير ليس ناقل أخبار فقط، بل صانع أثر إيجابي في محيطه."
        )
