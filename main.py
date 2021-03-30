
import matplotlib as plt
import numpy as np
import streamlit as st
import cv2
import tempfile
import math
from bresenham import bresenham

#zwraca punkty, które leza na prostej miedzy punktami A i B. Punkty to lista dwuelementowa ze wspolrzednymi punktow
#algorytm dziala w pierwszej ćwiartce ukladu wspolrzednych, w dolnej polowce (y=0 a y=x)
def to_photo_cord(x, y, size):
    return int(size / 2 + x), int(y + size / 2)
def brehensamAlg(A,B):
    points = []
    dX = B[0] - A[0]
    dY = B[1] - A[1]
    j= A[1]
    e = dY - dX
    for i in range( int(A[0]), int(B[0])):
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

#oblicza sredni wartość pikseli między emiterem a dekoderem
def value(A,B,input):
    x1,y1 = to_photo_cord(A[0],A[1],input.shape[0])
    x2,y2= to_photo_cord(B[0],B[1],input.shape[0])
    points = getPointsBresenham([x1,y1],[x2,y2])
    #print(x1,y1,x2,y2)

   #points=list(bresenham(x1, y1,x2,y2))
    sum=0
    count=0
    for i in points:
       # print(i)
        sum+= input[int(i[0])][int(i[1])]
        count+=1

    if count==0 :
        avg=0
    else :
        avg = sum/count

    return avg

#zwraca listę pozycji [x,y] detektorow
def get_detector_positions(r, step, theta, number_of_detectors):
    detector_list=[]
    for i in range(0, number_of_detectors):
            detec_buffer = []
            angle = step + 180 - theta/2 + i*(theta/(number_of_detectors-1))
            detec_buffer.append( r * math.cos( math.radians(angle) ))
            detec_buffer.append( r * math.sin( math.radians(angle) ))
            detector_list. append(detec_buffer)
    return detector_list

#obraca emiter i detektory, wylicza wspolrzedne emitera (podejscie stozkowe)
def rotate(r, alfa, theta, number_of_detectors):
    detector_list = [];
    #for step in range(0, 360, alfa):
    step=alfa
    emiter = []
    emiter.append(r * np.cos(math.radians(step)))
    emiter.append(r * np.sin(math.radians(step)))
    detector_list = get_detector_positions(r, step, theta, number_of_detectors)

    return emiter,detector_list

#normalizacja obrazu
def normalize(photo):
    max_val = 0
    for row in photo:
        tmp = max(row)
        if tmp > max_val:
            max_val = tmp
    return photo / max_val



def main():
    st.sidebar.title("""Tomograf""")
    file = st.sidebar.file_uploader("Upuść plik",type=['png','jpeg','jpg','bmp'])


    kroki = st.sidebar.checkbox("pokaż kroki pośrednie")
    if kroki:
        krok = st.sidebar.slider("Postępu obrotu emiterów i detektorów", 1, 360, 1, 1)

    alfa = st.sidebar.slider("Krok ∆α układu emiter/detektor", 0.5, 4.0, 1.0, 0.1)
    n = st.sidebar.slider("Liczba dekoderów",50, 1000, 100,1)
    l = st.sidebar.slider("Rozwartość/rozpiętość układu emiter/detektor", 10,350,270, 10)

    image = st.empty()
    image2 = st.empty()
    image3 = st.empty()
    if(file!=None):
        file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        image.image(file,width=500,caption='Input')
        img=np.asarray(img)
        img=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        sinogram=[]
        liczba_skanów=int(360/alfa)

        for i in np.linspace(0,360,liczba_skanów):
            emiter,detector_list = rotate(int(img.shape[0]/2)-1,i,l,n)
            tmp = []
            for id,j  in enumerate(detector_list):
                x= value(emiter,j,img)
                #print(x)
                tmp.append(x)
            sinogram.append(tmp)





        sinogram=normalize(sinogram)
        image2.image(sinogram, caption='Sinogram')
        image3.image(file, width=500, caption='Input')












if __name__ == "__main__":
    main()
