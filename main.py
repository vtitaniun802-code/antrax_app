import threading
import requests
from kivy.app import App
from kivy.clock import mainthread
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

# Configuração da URL do DuckDNS
URL = "http://antrax-app.duckdns.org:8080/v1/chat/completions"


class AntraxApp(App):

    def build(self):
        self.title = "Antrax Agent"

        root = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.scroll = ScrollView(size_hint=(1, 0.85))
        self.chat_history = Label(
            text="[System]: Conectado a antrax-app.duckdns.org\n",
            size_hint_y=None,
            markup=True,
            valign="top",
            halign="left",
        )
        self.chat_history.bind(
            texture_size=lambda instance, value: setattr(
                instance, "height", value[1]
            )
        )
        self.chat_history.bind(
            width=lambda instance, value: setattr(
                instance, "text_size", (value, None)
            )
        )
        self.scroll.add_widget(self.chat_history)
        root.add_widget(self.scroll)

        input_layout = BoxLayout(
            orientation="horizontal", size_hint=(1, 0.15), spacing=5
        )
        self.text_input = TextInput(
            hint_text="Digite um comando...", multiline=False
        )
        send_btn = Button(
            text="Enviar", size_hint=(0.3, 1), background_color=(0, 0.7, 0.9, 1)
        )
        send_btn.bind(on_release=self.send_message)

        input_layout.add_widget(self.text_input)
        input_layout.add_widget(send_btn)
        root.add_widget(input_layout)

        return root

    def send_message(self, instance):
        user_text = self.text_input.text.strip()
        if not user_text:
            return

        self.append_text(f"\n[b]Você:[/b] {user_text}")
        self.text_input.text = ""

        threading.Thread(target=self.query_llm, args=(user_text,)).start()

    def query_llm(self, prompt):
        try:
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "Voce e o Antrax. Responda direto.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
            }
            res = requests.post(URL, json=payload, timeout=15)
            if res.status_code == 200:
                answer = res.json()["choices"][0]["message"]["content"]
                self.append_text(f"\n[b]Antrax:[/b] {answer}")
            else:
                self.append_text(f"\n[Erro]: Status {res.status_code}")
        except Exception as e:
            self.append_text(f"\n[Erro de conexão]: {str(e)}")

    @mainthread
    def append_text(self, text):
        self.chat_history.text += text


if __name__ == "__main__":
    AntraxApp().run()
