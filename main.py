import streamlit as st
import matplotlib as plt
import numpy as np




def main():
    st.sidebar.title("""Tomograf""")
    file = st.sidebar.file_uploader("Upuść plik",type=['png','jpeg','jpg','bmp'])
    kroki = st.sidebar.checkbox("pokaż kroki pośrednie")
    if kroki:
        krok = st.sidebar.slider("Postępu obrotu emiterów i detektorów", 1, 360, 1, 1)

    alfa = st.sidebar.slider("Krok ∆α układu emiter/detektor", 1, 360, 1, 1)
    n = st.sidebar.slider("Liczba dekoderów",50, 1000, 100,1)
    l = st.sidebar.slider("Rozwartość/rozpiętość układu emiter/detektor", 3, 50,30, 1)



    image = st.empty()
    image2 = st.empty()
    image3 = st.empty()
    if(file!=None):
        image.image(file,width=500,caption='Input')
        image2.image(file, width=500, caption='Input')
        image3.image(file, width=500, caption='Input')





if __name__ == "__main__":
    main()
