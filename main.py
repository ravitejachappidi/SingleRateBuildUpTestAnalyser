import streamlit as st

import math
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 

import sklearn

from sklearn.linear_model import LinearRegression

st.title("Constant Rate Build up test")

uploaded_file = st.file_uploader("Choose a file of pressure-time data with headers p in psi and t in hr respectively")
if uploaded_file is not None:
    # # To read file as bytes:
    # bytes_data = uploaded_file.getvalue()
    # st.write(bytes_data)

    # # To convert to a string based IO:
    # stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    # st.write(stringio)

    # # To read file as string:
    # string_data = stringio.read()
    # st.write(string_data)

    # Can be used wherever a "file-like" object is accepted:
    with st.container():
        dataframe = pd.read_csv(uploaded_file)
        st.header("Given Input data")
        st.write(dataframe)

    
    st.sidebar.title("Enter the values")

    tp = st.sidebar.number_input("pseudo flowing time(hr) [24*Np/Q(last)]")

    t = st.sidebar.number_input("Enter when well bore storage effect stops - t")

    st.sidebar.title("Enter values for k and s")
    porosity = st.sidebar.number_input("Porosity(fraction)")
    height = st.sidebar.number_input("Height(ft)")
    ct = st.sidebar.number_input("Compressbility(in psi^-1 * 10e-6)")
    flowRate = st.sidebar.number_input("Flow Rate(RB/D))")
    fvf_o = st.sidebar.number_input("Formation volume factor(Bo)")
    rw = st.sidebar.number_input("Borehole radius(ft)")
    viscosity = st.sidebar.number_input("Viscosity(mu)")
    pwf = st.sidebar.number_input("Pwf(psia)")

    st.caption("Enter pseudo time(tp) for further data")
    if tp != 0:    
        with st.container():
            dataset = dataframe
            dataset_delta_t = []

            for i in range(0,len(dataset)-1,1):
                dataset_delta_t.append(dataset["t"][i+1] - dataset["t"][i])

            for i in range(len(dataset_delta_t)):
                dataset_delta_t[i] = round(dataset_delta_t[i], ndigits = 4)        

            dataset = dataset.drop([0])


        with st.container():
            tp_deltat = []

            for i in range(1,len(dataset)+1):
                tp_deltat.append((tp+dataset["t"][i])/dataset["t"][i])

            for i in range(len(tp_deltat)):
                tp_deltat[i] = round(tp_deltat[i], ndigits = 4)
        

            dataset["(tp + delta t)/delta t"] = tp_deltat

        with st.container():
            n = np.array(dataset["(tp + delta t)/delta t"])

            for i in range(len(n)):
                n[i] = math.log10(n[i])    

            dataset["log((tp + delta t)/delta t)"] = n 

            st.header("Data produced from Given data - Horner plot parameters")
            st.write(dataset)

        
        with st.container():
            x1 = dataset["log((tp + delta t)/delta t)"]
            x2 = dataset["p"]

            fig = plt.figure()
            plt.scatter(x1,x2)
            plt.title("log((tp + delta t)/delta t) vs p")
            plt.xlabel("log((tp + delta t)/delta t)")
            plt.ylabel("p")

            #splt.show()
            st.header("Complete Horners Build up plot")
            st.pyplot(fig)

            st.write("Enter the log((tp + delta t)/delta t) last value for t where curve started to form i.e where well bore storage effect ends")

            
            
            if  t != 0:
                c = dataset[dataset["log((tp + delta t)/delta t)"] < t]
                x11 = c["log((tp + delta t)/delta t)"]
                x22 = c["p"]

                fig2 = plt.figure()
                plt.scatter(x11,x22)
                plt.title(" log((tp + delta t)/delta t) vs p")
                plt.xlabel("log((tp + delta t)/delta t)")
                plt.ylabel("p")

                st.header("Horners Build up plot for linear regression")
                st.caption("change t value only upto a value where you can see a strainght line in plot")
                st.pyplot(fig2)

                lr = LinearRegression()

                lr.fit(np.array(c["log((tp + delta t)/delta t)"]).reshape(-1,1),np.array(c["p"]).reshape(-1,1))

                m = lr.coef_
                c = lr.intercept_
                st.write("slope of the regression line :")
                st.write(m[0][0])

                st.write("intercept of the regression line :")
                st.write(c[0])

                st.header("Enter the values in the sidebar to get permeability and skin")

               

                if porosity != 0 and height != 0 and porosity != 0 and ct != 0 and fvf_o != 0 and rw != 0 and viscosity != 0 and pwf != 0:
                    k = -(162.6*fvf_o*viscosity*flowRate)/(m*height)
                    st.text("The permeability is: ")
                    st.text(round(k[0][0], ndigits = 4))

                    b_1hr = c + m*math.log10(tp+1)

                    s = 1.1513*(((pwf - b_1hr)/m) - math.log10(k/(porosity*viscosity*ct*(10**(-6))*rw*rw)) + 3.2275)
                    st.text("The skin is: ")
                    st.text(round(s[0][0], ndigits = 4))

                    st.text("Total pressure drop:")
                    total_delta_p = c - pwf
                    st.text(round(total_delta_p[0],ndigits = 4))

                    st.text("pressure drop caused by skin is:")
                    delta_Ps = -m*s*0.8686
                    st.text(round(delta_Ps[0][0],ndigits = 4))

                    st.text("perecentage of pressure drop caused by skin is:")
                    delta_Ps_perc = delta_Ps/total_delta_p
                    st.text(round(delta_Ps_perc[0][0],ndigits = 4))

                else:
                    st.caption("Enter the data other than 0 in given columns")    




                

