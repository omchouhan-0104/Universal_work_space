from openai import OpenAI


class SummarizationService:

    @staticmethod
    def summarize(
        text: str,
        max_length: int = 500,
    ) -> str:

        if not text or not text.strip():
            raise ValueError(
                "Text cannot be empty"
            )

        if max_length < 50:
            raise ValueError(
                "max_length must be at least 50"
            )

        client = OpenAI()

        prompt = f"""
Summarize the following text clearly and concisely.

Requirements:
- Keep the important information.
- Do not invent facts.
- Use simple language.
- Return only the summary.
- Keep the summary reasonably concise.

Text:

{text}
"""

        response = client.responses.create(
            model="gpt-5.5",
            instructions=(
                "You are a professional document "
                "summarization assistant."
            ),
            input=prompt,
            max_output_tokens=max_length,
        )

        summary = response.output_text.strip()

        if not summary:
            raise ValueError(
                "AI returned an empty summary"
            )

        return summary
