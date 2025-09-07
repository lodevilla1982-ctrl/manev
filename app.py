# app.py
import streamlit as st
import os
import tempfile
import base64
import zipfile
from utils.generator import FunkoChibiGenerator
import plotly.graph_objects as go
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="🎨 Funko Chibi Generator",
    page_icon="🎨",
    layout="wide"
)

# Estilos CSS
st.markdown("""
<style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
    }
    .stDownloadButton>button {
        background-color: #008CBA;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar generador
if 'generator' not in st.session_state:
    st.session_state.generator = FunkoChibiGenerator()
    st.session_state.parts = None

generator = st.session_state.generator

# Columnas
col1, col2 = st.columns([1, 2])

with col1:
    st.header("🔧 Configuración")
    st.markdown("---")

    # Tipo de personaje
    character_type = st.selectbox("Tipo", ["human", "child", "dog", "cat", "bear"])
    generator.character_type = character_type

    # Género
    gender = st.selectbox("Género", ["male", "female", "neutral"])
    generator.gender = gender

    # Escala
    scale = st.slider("Escala", 0.5, 2.0, 1.0, 0.1)
    generator.scale = scale

    # Tolerancia
    tolerance = st.slider("Tolerancia (mm)", -0.2, 0.0, -0.05, 0.01)
    generator.set_tolerance(tolerance)

    # Estilo de pelo
    hair_styles = {
        "male": ["short", "long", "bald"],
        "female": ["short", "long", "curly"],
        "neutral": ["short", "bald"]
    }
    hair_style = st.selectbox("Estilo de pelo", hair_styles[gender])
    generator.hair_style = hair_style

    # Ropa
    clothing = st.selectbox("Ropa", ["none", "shirt", "hat"])
    generator.clothing = clothing

    st.markdown("---")
    
    # Botón generar
    if st.button("🚀 Generar Modelo 3D", use_container_width=True):
        with st.spinner("Generando modelo 3D..."):
            try:
                parts = generator.generate_full_model()
                st.session_state.parts = parts
                st.success("✅ Modelo generado con éxito!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    # Exportar
    if st.session_state.parts:
        st.markdown("---")
        st.header("💾 Exportar")
        
        file_format = st.radio("Formato", ["STL", "OBJ"])
        
        if st.button("📥 Descargar Todas las Partes", use_container_width=True):
            with st.spinner("Exportando partes..."):
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        exported_files = generator.export_parts(tmpdir, file_format)
                        
                        zip_path = os.path.join(tmpdir, "funko_chibi_parts.zip")
                        with zipfile.ZipFile(zip_path, 'w') as zipf:
                            for file_path in exported_files:
                                if os.path.exists(file_path):
                                    zipf.write(file_path, os.path.basename(file_path))
                        
                        with open(zip_path, "rb") as f:
                            bytes_data = f.read()
                            b64 = base64.b64encode(bytes_data).decode()
                            href = f'<a href="data:application/zip;base64,{b64}" download="funko_chibi_parts.zip">Descargar ZIP</a>'
                            st.markdown(href, unsafe_allow_html=True)
                            
                except Exception as e:
                    st.error(f"❌ Error al exportar: {str(e)}")

with col2:
    st.header("👁️ Vista 3D")
    st.markdown("---")
    
    if st.session_state.parts:
        fig = go.Figure()
        
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
            '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
        ]
        
        for i, (name, mesh) in enumerate(st.session_state.parts.items()):
            if len(mesh.vertices) == 0:
                continue
                
            vertices = mesh.vertices
            faces = mesh.faces
            
            x, y, z = vertices.T
            i_indices, j_indices, k_indices = faces.T
            
            fig.add_trace(go.Mesh3d(
                x=x, y=y, z=z,
                i=i_indices, j=j_indices, k=k_indices,
                name=name,
                showscale=False,
                opacity=0.9,
                color=colors[i % len(colors)],
                hovertemplate=f'<b>{name}</b><extra></extra>'
            ))
        
        fig.update_layout(
            scene=dict(
                xaxis=dict(title='X'),
                yaxis=dict(title='Y'),
                zaxis=dict(title='Z'),
                aspectmode='data'
            ),
            title="Vista 3D del Funko Chibi",
            height=600,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("👆 Configura las opciones y haz clic en 'Generar Modelo 3D'")
        st.image("https://placehold.co/600x400/4ECDC4/FFFFFF?text=Funko+Chibi+Generator", 
                caption="Diseña tu Funko Chibi", use_column_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Desarrollado con ❤️ para impresión 3D | 
    <a href='https://github.com/' target='_blank'>GitHub</a> | 
    Compatible con FDM 3D Printers</p>
</div>
""", unsafe_allow_html=True)