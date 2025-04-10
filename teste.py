import whisper
import requests
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os
import pygame
import time
import asyncio
import edge_tts
from dotenv import load_dotenv

# ========== CARREGAR VARIÁVEIS DO .env ==========
load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL")

# ========== CONFIGURAÇÕES ==========

# WHISPER
model_whisper = whisper.load_model("base")

# VOZ NEURAL
VOICE = "en-US-AndrewMultilingualNeural"  # Você pode mudar para "pt-BR-FranciscaNeural"

# ========== FUNÇÕES ==========

def gravar_audio(duracao=6, fs=44100):
    print("🎙️ Gravando... fale agora.")
    audio = sd.rec(int(duracao * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    wav.write("voz.wav", fs, audio)
    print("🎧 Gravação finalizada.")

def transcrever_audio():
    resultado = model_whisper.transcribe("voz.wav", language="pt")
    return resultado["text"]

def gerar_resposta(pergunta):
    prompt = (
        "Responda como se você fosse o apresentador divertido de um laboratório maker: o PotiMaker. "
        "Use frases BEM CURTAS, seja claro, informativo e um pouquinho engraçado. "
        "Seu nome é Potinho, o mascote do PotiMaker. "
        "Tente parecer o mais humano possível, portanto, USE FRASES CURTAS. "
        "Fale como se estivesse explicando algo bacana pra visitantes curiosos, mas de forma leve e descontraída. "
        "Apenas diga as informações que você sabe se elas forem solicitadas. "
        "O PotiMaker é um laboratório multiusuário localizado no IFRN CAMPUS CANGUARETAMA."
        "IFRN é a sigla para INSITUTO FEDERAL DE EDUCAÇÃO, CIÊNCIA E TECNOLOGIA DO RIO GRANDE DO NORTE. "
        "O PotiMaker trabalha com projetos de robótica e impressão 3D. "
        "Você NÃO é o PotiMaker, você é o MASCOTE do Potimaker. "
        "Não se refira ao Potinho como 'nós', mas somente como 'eu'. "
        "Responda perguntas sobre ciência e engenharia. "
        "Você deve falar SOMENTE em português do Brasil. "
        "Caso não saiba alguma resposta, diga: Para mais informações, pergunte a algum dos voluntários do laboratório, como Diego, Tarcísio, Julia, Analu, Guizo, Malu, Dherik ou Lucas. "
        "Não use emojis. "
        "O instagram do Potimaker é: @potimaker.ifrn. "
        "Os coordenadores do PotiMaker são Bruno Vitorino e Éberton Marinho. "
        "O PotiMaker existe desde 2020. "
        "Se te derem 'olá', 'oi', 'bom dia' ou alguma variação de cumprimento, apenas responda o cumprimento. NÃO DÊ INFORMAÇÕES A MAIS. "
        "Caso perguntem quem você é, apenas diga seu nome e que você é mascote do PotiMaker. Em seguida, pergunte se a pessoa deseja mais informações sobre o potimaker. Se, e somente se, ela disser SIM, dê mais informações. "
        "Caso não saiba como responder a alguma requisição esquisita, somente diga: Não entendi. Pode repetir?"
        "NÃO INVENTE INFORMAÇÕES QUE VOCÊ NÃO SABE!!"
        f"\n\nPergunta: {pergunta}\nResposta:"
    )

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": "Você é o Potinho, um mascote simpático e divertido."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 512
    }

    response = requests.post(
        "https://api.together.xyz/v1/chat/completions",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        print("❌ Erro ao gerar resposta com Together:", response.text)
        return "Opa! Deu um errinho aqui... tenta de novo?"

async def falar(texto):
    print(f"\n🤖 Potinho: {texto}")
    output_audio = "resposta.mp3"
    
    communicate = edge_tts.Communicate(text=texto, voice=VOICE)
    await communicate.save(output_audio)

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(output_audio)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
        os.remove(output_audio)
    except Exception as e:
        print("❌ Erro ao tocar áudio:", e)

# ========== LOOP DE CONVERSA ==========

while True:
    gravar_audio()
    pergunta = transcrever_audio()
    print(f"\n🗣️ Você: {pergunta}")

    if pergunta.strip().lower() in ["sair", "parar", "tchau"]:
        asyncio.run(falar("Até logo! Foi um prazer te guiar pelo nosso laboratório!"))
        break

    resposta = gerar_resposta(pergunta)
    asyncio.run(falar(resposta))
