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

