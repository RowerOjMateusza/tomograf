
import matplotlib as plt
import numpy as np
import streamlit as st

#zwraca punkty, które leza na prostej miedzy punktami A i B. Punkty to lista dwuelementowa ze wspolrzednymi punktow
#algorytm dziala w pierwszej ćwiartce ukladu wspolrzednych, w dolnej polowce (y=0 a y=x)
def brehensamAlg(A,B):
    points = []
    dX = B[0] - A[0]
    dY = B[1] - A[1] 
    j= A[1] 
    e = dY - dX 
    for i in range( A[0], B[0]):
        points.append([i,j])
        if( e >=0):
            j+=1
            e-=dX 
        i+=1
        e+=dY
    return points;

def changeAxis(A,B,isAxisX):
    if(not(isAxisX)):
        A[0],A[1]=A[1],A[0]
        B[0],B[1]=B[1],B[0]
    return brehensamAlg(A,B)

#zwraca numery pikseli, zwrocone przez algorytm Bresenhama
def getPointsBresenham( A, B ):

    isTop = False
    isLeft = False
    isAxisX = True

    #sprawdzanie, ktora cwiartka ukladu
    if( A[0] - B[0] > 0 ):
        isLeft = True;
    if( A[1] - B[1] < 0 ):
        isTop = True;
    #spradzenie, ktora polowka cwiartki
    if ( abs(A[0] - B[0]) < abs(A[1]-B[1])):
        isAxisX = False;

    ##pierwsza cwiartka ukladu wspolrzednych
    if( isTop and not(isLeft)):     
        points = changeAxis(A,B,isAxisX)

    ##druga cwiartka ukladu wspolrzednych
    elif( isTop and isLeft ):         
        B[0]=-B[0]
        points = changeAxis(A,B,isAxisX)
        for item in points:
            item[0]=-item[0];

    ##trzecia cwiartka ukladu wspolrzednych
    elif( not(isTop) and isLeft ):    
        B[0]=-B[0]
        B[1]=-B[1]
        points = changeAxis(A,B,isAxisX)
        for item in points:
            item[0]=-item[0];
            item[1]=-item[1];
    ##czwarta cwiartka ukladu wspolrzednych
    else:                           
        B[1]=-B[1]
        points = changeAxis(A,B,isAxisX)
        for item in points:
            item[1]=-item[1];
    
    if(not(isAxisX)):
        for item in points:
            item.reverse();
    return points;




#zwraca listę pozycji [x,y] detektorow
def get_detector_positions(r, step, theta, number_of_detectors): 
    for i in range(0, number_of_detectors):
            detec_buffer = [];
            angle = step + np.pi - theta/2 + i*(theta/(detectors-1)) 
            detec_buffer.append( r * cos( angle ))
            detec_buffer.append( r * sin( angle ))
            detector_list. append(detec_buffer)


#obraca emiter i detektory, wylicza wspolrzedne emitera (podejscie stozkowe)
def rotate(r, alfa, theta, number_of_detectors):
    detector_list = [];
    for step in range(0, 360, alfa):
        emiter = []
        emiter.append(r * np.cos(step))
        emiter.append(r * np.sin(step))
        detector_list = get_detector_positions(r, step, theta, number_of_detectors)


        



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
