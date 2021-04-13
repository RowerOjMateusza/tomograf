
import matplotlib as plt
import numpy as np
import streamlit as st
import cv2
import tempfile
import math
from bresenham import bresenham
from skimage.filters.edges import convolve
import skimage.filters.rank
from datetime import date
import pydicom
from pydicom.data import get_testdata_files


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
    #points = getPointsBresenham([x1,y1],[x2,y2])
    points=list(bresenham(x1, y1,x2,y2))
    sum=0
    count=0
    for i in points:
        sum+= input[int(i[0])][int(i[1])]
        count+=1
    if count==0 :
        avg=0
    else :
        avg = sum/count
    return avg,points

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
    min_val=1000000000000
    for row in photo:
        tmp = max(row)
        minimum = min(row)
        if tmp > max_val:
            max_val = tmp
        if minimum<min_val:
            min_val=minimum
    return (photo-min_val) / (max_val-min_val)


def dicom(image, name, description, sex, birth, institution):
    filename = get_testdata_files("CT_small.dcm")[0];
    ds = pydicom.dcmread(filename);

    image2 = np.asarray(image, dtype=np.uint16)
    ds.Rows = image2.shape[1]
    ds.Columns = image2.shape[0]
    ds.PixelData = image2.tostring()
    
    ds.PatientName = name;
    ds.PatientSex = sex;
    ds.PatientBirthDate = birth;
    
    today = date.today()

    # dd/mm/YY
    
    ds.StudyDate = today.strftime("%d.%m.%Y")
    ds.InstitutionName = institution
    ds.StudyDescription = description

    ds.save_as("Tomograf.dcm")




def make_kernel(size):
  mask=[]
  for k in range(-size//2, size//2):
      if k == 0:
          mask.append(1)
      else:
          if k % 2 == 0:
              mask.append(0)
          if k % 2 == 1:
              mask.append((-4/(math.pi**2))/k**2)
  return mask

def filter(sinogram):
    kernel = make_kernel(100)
    filtered = np.zeros(len(sinogram))
    filtered = np.convolve(sinogram, kernel, mode='same') #splot
    return filtered

def make_square(photo):
    s = max(photo.shape[0], photo.shape[1])
    f = np.zeros((s, s))
    ax, ay = (s - photo.shape[1]) // 2, (s - photo.shape[0]) // 2
    f[ay:photo.shape[0] + ay, ax:ax + photo.shape[1]] = photo
    return f

def RMSE(orginal , estimate):
    suma=0
    cnt=0
    for i in range(orginal.shape[0]):
        for j in range (orginal.shape[1]):
            x = orginal[i][j] - estimate[i][j]
            cnt+=1
            suma+=x**2
    avg = suma/cnt
    return math.sqrt(avg)




def main():
    st.sidebar.title("""Tomograf""")
    file = st.sidebar.file_uploader("Upuść plik",type=['dcm','png','jpeg','jpg','bmp'])

    kroki = st.sidebar.checkbox("pokaż kroki pośrednie",value=True)
    filrowanie = st.sidebar.checkbox("użyj filtrowania",value=True)
    konwulacja = st.sidebar.checkbox("konwulacja skanów",value=True)
    mediana = st.sidebar.checkbox("filtr medianowy",value=True)
    if kroki:
        krok = st.sidebar.slider("Postępu obrotu emiterów i detektorów", 1, 360, 1, 1)

    alfa = st.sidebar.slider("Krok ∆α układu emiter/detektor", 0.5, 4.0, 1.0, 0.1)
    n = st.sidebar.slider("Liczba detektorów",50, 1000, 100,10)
    l = st.sidebar.slider("Rozwartość/rozpiętość układu emiter/detektor", 10,350,270, 5)

    patient_name = str(st.sidebar.text_input("Imię pacjenta", "Jan Nowak"))
    patient_sex= str(st.sidebar.text_input("Płeć pacjenta", "Male"))
    patient_birth= str(st.sidebar.text_input("Rok urodzenia pacjenta", "1968"))
    patient_institution= str(st.sidebar.text_input("Nazwa instytucji", "PP"))
    patient_description= str(st.sidebar.text_input("Komentarz", "Uwagi"))

    
    image = st.empty()
    image2 = st.empty()
    image3 = st.empty()
    if(file!=None):
        nm =  file.name
        p = st.empty()
        if (nm.split(".")[1] == "dcm"):
            
            ds = pydicom.dcmread(nm);
            imgDcm = ds.pixel_array
            print(type(ds.PatientName))
            capt = "Name: "+ str(ds.PatientName)+"\n" 
            capt+= "Sex: "+ str(ds.PatientSex)+"\n"
            capt+= "BirthDate: "+ str(ds.PatientBirthDate)+"\n"
            capt+= "Study Date: "+ str(ds.StudyDate)+"\n"
            capt+= "InstitutionName: "+ str(ds.InstitutionName)+"\n"
            capt+= "Description: "+ str(ds.StudyDescription)+"\n"
            st.text(capt)
            image.image(imgDcm,width=500,caption="")

        else:

            file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)
            image.image(file,width=500,caption='Input')
            img=np.asarray(img)
            img=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = make_square(img)
            img =normalize(img)

            sinogram=[]
            end_image=np.zeros(img.shape)
            liczba_skanów=int(360/alfa)
        

            for i in np.linspace(0,359,liczba_skanów):
                emiter,detector_list = rotate(int(img.shape[0]/2)-1,i,l,n)
                tmp = np.zeros(img.shape)
                sinogram_row=[]
                points=[]
                listOfPoints = []
                for id,j  in enumerate(detector_list):
                    x,points= value(emiter,j,img)
                    sinogram_row.append(x)
                    listOfPoints.append(points)

                sinogram.append(sinogram_row)
                if filrowanie:
                    sinogram_row = filter(sinogram_row)
                for id,line in enumerate(listOfPoints):
                    for [x, y] in line:
                            tmp[x][y] += sinogram_row[id]
                if konwulacja:
                    K = np.ones([5, 5])
                    K = K / sum(K)
                    tmp = convolve(tmp, K)
                end_image+=tmp
                if kroki:
                    if i%krok <1 and i!=0:
                        tmp_sinogram = normalize(sinogram)
                        image2.image(tmp_sinogram, caption='Sinogram')
                        tmp_end_image = normalize(end_image)
                        image3.image(tmp_end_image, width=500, caption='Input')
                        #p.write(RMSE(img,tmp_end_image))
            sinogram=normalize(sinogram)
            image2.image(sinogram, caption='Sinogram')

            end_image=normalize(end_image)
            if mediana:
                end_image = skimage.filters.rank.median(end_image, np.ones([3, 3]))
            image3.image(end_image, width=500, caption='Input')
            tmp_end_image = normalize(end_image)
            print(RMSE(img, tmp_end_image))

            dicom(end_image, patient_name, patient_description, patient_birth, patient_birth, patient_institution)





if __name__ == "__main__":
    main()
