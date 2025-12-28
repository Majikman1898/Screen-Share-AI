import openai
from typing import List, Dict, Optional

class AIClient:
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.conversation_history: List[Dict[str, str]] = []

    def send_query(self, prompt: str, image_base64: Optional[str] = None, include_history: bool = False) -> str:
        messages = []

        if include_history:
            messages.extend(self.conversation_history)

        user_content = []
        if prompt:
             user_content.append({"type": "text", "text": prompt})

        if image_base64:
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_base64}"
                }
            })

        messages.append({"role": "user", "content": user_content})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=300
            )
            reply = response.choices[0].message.content

            # Update history
            if include_history:
                self.conversation_history.append({"role": "user", "content": prompt if prompt else "Image sent"}) # Simplified history for now
                self.conversation_history.append({"role": "assistant", "content": reply})

            return reply
        except Exception as e:
            return f"Error: {str(e)}"

    def clear_history(self):
        self.conversation_history = []
