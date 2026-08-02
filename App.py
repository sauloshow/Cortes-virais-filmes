import streamlit as st
import yt_dlp
import google.generativeai as genai
from moviepy.editor import VideoFileClip
import os
import json

st.set_page_config(page_title="Gerador de Cortes Virais IA", page_icon="✂️", layout="centered")

st.title("✂️ Gerador de Cortes Virais de Vídeos")
st.markdown("Cole o link de um vídeo do YouTube para extrair os trechos de maior impacto usando Inteligência Artificial.")

# Sua chave da API do Gemini
api_key = "AQ.Ab8RN6IixV2CjzxG26vbHDu7DPq0ycxd-0AYVQl79W7mxGj6mw"

youtube_url = st.text_input("Link do vídeo do YouTube:")

def baixar_video(url):
    output_filename = "input_video.mp4"
    
    # Remove o arquivo antigo caso ele ainda exista
    if os.path.exists(output_filename):
        os.remove(output_filename)

    ydl_opts = {
        'format': 'best[ext=mp4]/best', # Garante um formato direto compatível
        'outtmpl': output_filename,
        'overwrites': True,
        'quiet': True,
        'no_warnings': True,
        # Simula um navegador real para evitar bloqueios do YouTube
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
        x1 = (w - target_width) // 2
        corte_vertical = corte.crop(x1=x1, y1=0, x2=x1 + target_width, y2=h)
        corte_vertical.write_videofile(output_path, codec="libx264", audio_codec="aac")

if st.button("🚀 Processar e Gerar Corte"):
    if not youtube_url:
        st.warning("Insira um link do YouTube válido.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            with st.spinner("1. Baixando o vídeo do YouTube..."):
                video_file = baixar_video(youtube_url)
                
                # Validação para confirmar se o vídeo foi realmente baixado
                if not os.path.exists(video_file) or os.path.getsize(video_file) == 0:
                    raise Exception("Não foi possível baixar este vídeo específico do YouTube. Tente outro link de vídeo/podcast público.")
                
            with st.spinner("2. Analisando o tempo do vídeo com IA..."):
                with VideoFileClip(video_file) as clip:
                    duracao = int(clip.duration)
                
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                Análise um vídeo que tem {duracao} segundos de duração total.
                Escolha o intervalo de tempo mais marcante (com duração entre 30 e 60 segundos) para um vídeo curto de redes sociais (Reels/TikTok).
                Retorne EXATAMENTE um JSON com as chaves "inicio" e "fim" representando os segundos numéricos. Exemplo: {{"inicio": 10, "fim": 40}}.
                """
                
                response = model.generate_content(prompt)
                
                response_text = response.text.replace("```json", "").replace("```", "").strip()
                corte_info = json.loads(response_text)
                
                inicio = corte_info.get("inicio", 0)
                fim = corte_info.get("fim", min(30, duracao))
                
                st.info(f"Trecho viral identificado: de {inicio}s até {fim}s.")

            with st.spinner("3. Formatando clipe para formato vertical (9:16)..."):
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
            st.error(f"Ocorreu um erro durante o processamento: {str(e)}")

