import json
import os
import re
import subprocess
import urllib.request
import streamlit as st
from audio_recorder_streamlit import audio_recorder

# Configurações do servidor local
LOCAL_PORT = os.environ.get("DRAEL_PORT", "8080")
LOCAL_URL = f"http://127.0.0.1:{LOCAL_PORT}/v1/chat/completions"
LOCAL_KEY = "drael-local"

CHARTER = """Voce e Antrax, assistente autônomo no NetHunter. Responda de forma direta.
Para executar comandos bash no sistema, responda estritamente usando o formato:
```tool
{"tool":"bash","args":{"cmd":"seu comando aqui"}}
```"""

# Configuração da Página
st.set_page_config(
    page_title="ANTRAX // ADVANCED HUD",
    page_icon="☠️",
    layout="wide"
)

# Estilização CSS Hacker Cyberpunk Next-Gen (Glassmorphism + Ultra Neon HUD)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap');

    /* Fundo AMOLED e Fontes Futuristas */
    .stApp {
        background-color: #020503 !important;
        color: #00FF66 !important;
        font-family: 'Rajdhani', sans-serif !important;
    }

    /* Ocultar elementos padrão */
    #MainMenu, footer, header {visibility: hidden;}

    /* Core JARVIS HUD 3D de Alta Tecnologia */
    .hud-main-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 10px 0;
    }
    .jarvis-core-wrapper {
        position: relative;
        width: 160px;
        height: 160px;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .ring-layer-1 {
        position: absolute;
        width: 150px;
        height: 150px;
        border: 2px solid rgba(0, 255, 102, 0.2);
        border-top: 3px solid #00FF66;
        border-bottom: 3px solid #00FF66;
        border-radius: 50%;
        animation: rotateCW 8s linear infinite;
        box-shadow: 0 0 20px rgba(0, 255, 102, 0.3);
    }
    .ring-layer-2 {
        position: absolute;
        width: 120px;
        height: 120px;
        border: 2px dashed #00FF99;
        border-radius: 50%;
        animation: rotateCCW 4s linear infinite;
    }
    .ring-layer-3 {
        position: absolute;
        width: 90px;
        height: 90px;
        border: 1px solid rgba(0, 255, 102, 0.5);
        border-left: 3px solid #00FF66;
        border-radius: 50%;
        animation: rotateCW 2s linear infinite;
    }
    .core-reactor {
        width: 40px;
        height: 40px;
        background: radial-gradient(circle, #00FF66 0%, #003311 80%);
        border-radius: 50%;
        box-shadow: 0 0 30px #00FF66, 0 0 60px #00FF66;
        animation: pulseHyper 1s ease-in-out infinite alternate;
    }

    @keyframes rotateCW { 100% { transform: rotate(360deg); } }
    @keyframes rotateCCW { 100% { transform: rotate(-360deg); } }
    @keyframes pulseHyper {
        0% { transform: scale(0.8); opacity: 0.6; box-shadow: 0 0 15px #00FF66; }
        100% { transform: scale(1.15); opacity: 1; box-shadow: 0 0 35px #00FF66; }
    }

    /* Painel de Status do Sistema (Widgets) */
    .telemetry-bar {
        display: flex;
        justify-content: space-around;
        background: rgba(0, 20, 10, 0.6);
        border: 1px solid rgba(0, 255, 102, 0.3);
        border-radius: 8px;
        padding: 8px;
        margin-bottom: 20px;
        backdrop-filter: blur(5px);
    }
    .telemetry-item {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.75rem;
        letter-spacing: 1px;
        color: #00FF66;
    }
    .telemetry-value {
        color: #ffffff;
        font-weight: bold;
    }

    /* Header Principal */
    .title-main {
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900;
        color: #00FF66;
        text-align: center;
        letter-spacing: 4px;
        text-shadow: 0 0 15px rgba(0, 255, 102, 0.8);
        margin-bottom: 2px;
    }

    /* Mensagens Estilo Terminal Glassmorphic */
    .stChatMessage {
        background: rgba(0, 15, 5, 0.7) !important;
        border: 1px solid rgba(0, 255, 102, 0.3) !important;
        border-left: 4px solid #00FF66 !important;
        border-radius: 6px !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 255, 102, 0.1) !important;
        margin-bottom: 12px;
    }
    .stChatMessage p {
        color: #E0FFE0 !important;
        font-size: 1.05rem;
    }

    /* Campo de Digitação Sci-Fi */
    .stChatInputContainer textarea {
        background: rgba(0, 20, 8, 0.9) !important;
        color: #00FF66 !important;
        border: 1px solid #00FF66 !important;
        border-radius: 8px !important;
        box-shadow: 0 0 15px rgba(0, 255, 102, 0.3) !important;
        font-family: 'Orbitron', sans-serif !important;
    }
    .stChatInputContainer button {
        background-color: #00FF66 !important;
        color: #000000 !important;
        border-radius: 6px !important;
        box-shadow: 0 0 10px #00FF66 !important;
    }

    /* Blocos de Comando Bash Executados */
    .stCodeBlock {
        border: 1px solid #00FF66 !important;
        background-color: #010A03 !important;
        box-shadow: 0 0 20px rgba(0, 255, 102, 0.25) !important;
    }
</style>
""", unsafe_allow_html=True)

# 1. Renderização do Holograma JARVIS
st.markdown("""
<div class="hud-main-container">
    <div class="jarvis-core-wrapper">
        <div class="ring-layer-1"></div>
        <div class="ring-layer-2"></div>
        <div class="ring-layer-3"></div>
        <div class="core-reactor"></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<h1 class="title-main">ANTRAX // AI CORE</h1>', unsafe_allow_html=True)

# 2. Barra de Telemetria e Status Visuais
st.markdown("""
<div class="telemetry-bar">
    <div class="telemetry-item">OS: <span class="telemetry-value">NETHUNTER</span></div>
    <div class="telemetry-item">CPU: <span class="telemetry-value">ONLINE (98%)</span></div>
    <div class="telemetry-item">ENCRYPTION: <span class="telemetry-value">AES-256</span></div>
    <div class="telemetry-item">TUNNEL: <span class="telemetry-value">ACTIVE</span></div>
</div>
""", unsafe_allow_html=True)

def exec_tool(tool_name, args):
    if tool_name == "bash":
        cmd = args.get("cmd", "")
        try:
            res = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            return (res.stdout or res.stderr or "Sem saída.").strip()
        except Exception as e:
            return f"Erro no comando: {str(e)}"
    return "Ferramenta desconhecida."

def call_local(messages):
    payload_dict = {
        "messages": messages,
        "temperature": 0.2,
        "stream": False,
        "cache_prompt": True,
        "use_mmap": True,
    }
    payload = json.dumps(payload_dict).encode("utf-8")
    req = urllib.request.Request(
        LOCAL_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LOCAL_KEY}",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": CHARTER}]

# 3. Módulos de Entrada de Usuário (Voz & Texto)
col_mic, col_status = st.columns([1, 4])
with col_mic:
    st.markdown("<span style='color:#00FF66; font-family: Orbitron; font-size: 0.8rem;'>[ VOICE INPUT ]</span>", unsafe_allow_html=True)
    audio_bytes = audio_recorder(
        text="",
        recording_color="#00FF66",
        neutral_color="#003311",
        icon_name="microphone",
        icon_size="2x",
    )

if audio_bytes:
    st.info("⚡ SINAL DE ÁUDIO CAPTURADO.")

# Exibição do Histórico de Conversas
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Prompt de Entrada estilo Console Cyberpunk
if user_input := st.chat_input("COMMAND PROMPT // INJECT SYSTEM QUERY..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("CORE PROCESSING QUERY..."):
            try:
                response = call_local(st.session_state.messages)
                st.write(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )

                # Parser e Execução de Ferramentas Bash
                match = re.search(
                    r"```tool\s*(\{.*?\})\s*```", response, re.DOTALL
                )
                if match:
                    tool_data = json.loads(match.group(1))
                    cmd_exec = tool_data.get("args", {}).get("cmd")
                    st.info(f"⚡ EXECUTANDO NO NETHUNTER: `{cmd_exec}`")

                    out = exec_tool(
                        tool_data.get("tool"), tool_data.get("args", {})
                    )
                    st.code(out, language="bash")

                    st.session_state.messages.append(
                        {
                            "role": "user",
                            "content": f"[Saída da Ferramenta]:\n{out}",
                        }
                    )
            except Exception as e:
                st.error(f"SYSTEM FAULT / CRITICAL ERROR: {e}")
