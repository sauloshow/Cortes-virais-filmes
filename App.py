import streamlit as st
import yt_dlp
import google.generativeai as genai
from moviepy.editor import VideoFileClip
import os
import json

st.set_page_config(page_title="Gerador de Cortes Virais IA", page_icon="✂️", layout="centered")

st.title("✂️ Gerador de Cortes Virais Multi-Plataforma")
st.markdown("Crie cortes verticais usando vídeos do **Instagram, Facebook, TikTok, YouTube** ou envio direto de MP4.")

api_key = "AQ.Ab8RN6IixV2CjzxG26vbHDu7DPq0ycxd-0AYVQl79W7mxGj6mw"

opcao = st.radio("Escolha a origem do vídeo:", ("Link de Rede Social (Instagram, Facebook, TikTok, YT)", "Enviar Arquivo MP4"))

social_url = None
uploaded_file = None

if opcao == "Link de Rede Social (Instagram, Facebook, TikTok, YT)":
    social_url = st.text_input("Cole o link do vídeo:")
else:
    uploaded_file = st.file_uploader("Escolha um arquivo do seu dispositivo:", type=["mp4", "mov", "mkv"])

def baixar_video_redes(url):
    output_filename = "input_video.mp4"
    if os.path.exists(output_filename):
        os.remove(output_filename)

    ydl_opts = {
        # Pega a versão direta em MP4 já unificada (evita checagens rigorosas de IP)
        'format': 'b[ext=mp4]/best[ext=mp4]/best',
        'outtmpl': output_filename,
        'overwrites': True,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        
    return output_filename


    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_filename,
        'overwrites': True,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        
    return output_filename

def processar_corte(input_path, start_sec, end_sec, output_path):
    with VideoFileClip(input_path) as video:
        corte = video.subclip(start_sec, end_sec)
        w, h = corte.size
        target_width = int(h * (9 / 16))
        
        if w < target_width:
            corte_vertical = corte
        else:
            x1 = (w - target_width) // 2
            corte_vertical = corte.crop(x1=x1, y1=0, x2=x1 + target_width, y2=h)
            
        corte_vertical.write_videofile(output_path, codec="libx264", audio_codec="aac")

if st.button("🚀 Processar e Gerar Corte"):
    video_file = "input_video.mp4"
    
    try:
        genai.configure(api_key=api_key)
        
        if opcao == "Link de Rede Social (Instagram, Facebook, TikTok, YT)":
            if not social_url:
                st.warning("Insira um link válido.")
                st.stop()
            with st.spinner("1. Baixando o vídeo..."):
                video_file = baixar_video_redes(social_url)
        else:
            if not uploaded_file:
                st.warning("Selecione um arquivo de vídeo.")
                st.stop()
            with st.spinner("1. Carregando arquivo..."):
                with open(video_file, "wb") as f:
                    f.write(uploaded_file.getbuffer())

        if not os.path.exists(video_file) or os.path.getsize(video_file) == 0:
            st.error("Não foi possível baixar o vídeo por este link. Tente enviar o arquivo MP4 diretamente.")
            st.stop()

        with st.spinner("2. Analisando o vídeo com IA..."):
            with VideoFileClip(video_file) as clip:
                duracao = int(clip.duration)
            
            if duracao <= 30:
                inicio = 0
                fim = duracao
                st.info(f"O vídeo possui apenas {duracao}s. Processando o conteúdo completo.")
            else:
                model = genai.GenerativeModel('gemini-1.5-flash')
                p = f'Análise um vídeo de {duracao} segundos. Escolha o melhor intervalo (30 a 60s) para redes sociais. Retorne apenas um JSON: {{"inicio": 10, "fim": 40}}.'
                
                response = model.generate_content(p)
                response_text = response.text.replace("```json", "").replace("```", "").strip()
                corte_info = json.loads(response_text)
                
                inicio = corte_info.get("inicio", 0)
                fim = corte_info.get("fim", min(30, duracao))
                st.info(f"Trecho viral identificado: de {inicio}s até {fim}s.")

        with st.spinner("3. Editando corte para formato vertical (9:16)..."):
            output_clip = "corte_viral.mp4"
            processar_corte(video_file, inicio, fim, output_clip)
            
        st.success("Corte gerado com sucesso!")
        st.video(output_clip)
        
        with open(output_clip, "rb") as f:
            st.download_button(
                label="📥 Baixar Corte Viral (MP4)",
                data=f,
                file_name="corte_viral.mp4",
                mime="video/mp4"
            )

    except Exception as e:
        st.error(f"Erro: {str(e)}")
                
