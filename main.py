import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

WINDOW_AREA = 4.5
COL_NAMES = ["Year", "Month", "Day", "Hour", "Minutes", "xxx", "DryBulp", "DewPointTemp", "RelHum", "AtmosPressure",
             "ExtHorRad", "ExtDirRad", "HorIRSky", "GloHorRad", "DirNorRad", "DifHorRad", "GloHorIllum",
             "DirNorIllum", "DifHorIllum", "ZenLum", "WindDir", "WindSpeed", "TotSkyCvr", "OpaqSkyCvr",
             "Visibility", "CeilingHgt", "PresWeathObs", "PresWeathCodes", "PrecipWtr", "AerosolOptDepth",
             "SnowDepth", "DaysLastSnow", "Albedo", "LiqPrecDepth", "LiqPrecQuantity"]

def about():
    message = "The software is based on the average mean temperature method of EnDrIn by Jørgen Erik Christensen. The room as the calculation is performed on is the MIT Reference Office with only 1 south-facing free facade. The remaining envelope is considered adiabatic.\nThis program is developed in a special course at The Technical University of Denmark, DTU Construct by Lasse V. Friis.\nAny questions or comments should be directed to s173799@dtu.dk.\n Note that the software is under development. "
    tk.messagebox.showinfo(title="About", message=message)

def ImportWeather():
    global data
    path = tk.filedialog.askopenfilename() #opening epw-file.
    if path.lower().endswith(('.epw')):
        data = pd.read_table(path, delimiter=",", skiprows=(0, 1, 2, 3, 4, 5, 6, 7), names=COL_NAMES)
        data = data.drop(columns=COL_NAMES[15:36])
        #setting datetime and cleaning columns
        data["date"] = data["Day"].astype(str) + '/'  + data["Month"].astype(str) + '/' + data["Year"].astype(str)
        data["date"] = pd.to_datetime(data["date"],format='%d/%m/%Y')
        data = data.set_index(data["date"])
        data = data.drop(columns=["date","Year","Month","Day","Minutes"])
        but_calc.config(state=tk.NORMAL) #activates calculation button
        but_weather.config(text="Import EPW Weatherfile (Imported)")
    else:
        tk.messagebox.showinfo(title="Error", message="Weather file is not in epw-format.")

def SolarGainCalc():
    if len(frame_entry.get()) == 0 or len(g_entry.get()) == 0 or len(fc_entry.get()) == 0 or len(area_entry.get()) == 0 or len(vent_entry.get()) == 0 or len(vent_temp_entry.get()) == 0:
        but_calc.config(text="Calculate (Please insert values!)")
    else:
        but_calc.config(text="Calculate")

        # internal gains
        internal = float(ig_entry.get())
        # calculating ventilation
        data["IndoorTemp"] = 20
        H_inf = 1.224*float(inf_entry.get())*24/24 #infiltration W/K
        data["Ventilation"] = 1.224*float(vent_entry.get()) * (float(vent_h_entry.get()) / 24)# * (float(vent_temp_entry.get())-data["IndoorTemp"])
        # calculating solar heat gain
        data["SolarGain"] = data["DirNorRad"] * float(frame_entry.get()) * float(g_entry.get()) * float(fc_entry.get()) * float(area_entry.get()) * 0.7 #EnDrIn correction factor (12-67)
        # W/K transmission loss/gain
        HL = float(wall_area_entry.get()) * float(wall_u_entry.get()) + float(area_entry.get()) * float(win_u_entry.get())
        #new indoor temperature
        data["NewIndoorTemp"] = (data["DryBulp"]+273.15 + ((data["SolarGain"] + internal)/(HL+H_inf+data["Ventilation"])))-273.15
        data[['NewIndoorTemp']].idxmax()
        data.loc[data["NewIndoorTemp"] < 20,"NewIndoorTemp"] = 20
        #activating buttons
        but_plot.config(state=tk.NORMAL)  # activates plot
        but_export.config(state=tk.NORMAL)
        but_export_data.config(state=tk.NORMAL)

def plot():
        global plot1
        if len(date_entry.get()) == 0:
            tk.messagebox.showinfo(title="Error", message="Please enter date")
        else:
            #converting input to datetime object
            date = datetime(2009,int(month_entry.get()),int(date_entry.get()))
            print(date)
            data_date_limited = data.loc[date]
            print(data_date_limited)
            #plotting options
            figure = plt.Figure(figsize=(3,3), dpi=100)
            ax = figure.add_subplot(111)
            chart_type = FigureCanvasTkAgg(figure, window)
            chart_type.get_tk_widget().grid(column=2, row=3, columnspan=4,rowspan=14)
            plot1 = data_date_limited.plot(x='Hour',y='NewIndoorTemp',kind='scatter', legend=True)
            ax.set_title('Indoor Air Temperatures')

def export_plot():
    plot1.get_figure().savefig('plot.png')
    tk.messagebox.showinfo(title="Plot Export", message="plot.png has been downloaded")

def export_data():
    data.to_csv("Dataset.csv")
    tk.messagebox.showinfo(title="Plot Export", message = "Dataset.csv has been downloaded")

window = tk.Tk()
window.title("Overheating Design Tool")
window.geometry("600x540")

#chart
figure = plt.Figure(figsize=(3,3), dpi=100)
ax = figure.add_subplot(111)
chart_type = FigureCanvasTkAgg(figure, window)
chart_type.get_tk_widget().grid(column=2, row=3, columnspan=4,rowspan=14)

headline = tk.Label(text="Window properties",font=("ARIAL"))
headline.grid(column = 0,row = 0,columnspan=2)

area_text = tk.Label(text="Area of window:")
area_text.grid(column = 0,row = 1)
area_entry = tk.Entry(width = 20)
area_entry.grid(column = 1,row = 1)
area_entry.delete(0,tk.END)
area_entry.insert(0,"4.5")

frame_text = tk.Label(text="Frame fraction:")
frame_text.grid(column = 0,row = 2)
frame_entry = tk.Entry(width = 20)
frame_entry.grid(column = 1,row = 2)
frame_entry.delete(0,tk.END)
frame_entry.insert(0,"0.1")

g_text = tk.Label(text="Solar heat transmittance:")
g_text.grid(column = 0,row = 3)
g_entry = tk.Entry(width = 20)
g_entry.grid(column = 1,row = 3)

fc_text = tk.Label(text="Sunlight protection factor:")
fc_text.grid(column = 0,row = 4)
fc_entry = tk.Entry(width = 20)
fc_entry.grid(column = 1,row = 4)

explainer = tk.Label(text="This calculator enables you to calculate\n the annual solar heat gain via Energy+ weather data.")
explainer.grid(column = 0,row = 5,columnspan=2)

hl_internal_gains = tk.Label(text="Internal gains",font=("ARIAL"))
hl_internal_gains.grid(column = 0,row = 8,columnspan=2)

ig_text = tk.Label(text="Internal gains [W]:")
ig_text.grid(column = 0,row = 9)
ig_entry = tk.Entry(width = 20)
ig_entry.grid(column = 1,row = 9)

explainer = tk.Label(text="Internal gains is inserted as the constant\naverage load in the climate zone")
explainer.grid(column = 0,row = 10,columnspan=2)

#ENVELOPE ---------------------------------------------------
hl_envelope = tk.Label(text="Envelope",font=("ARIAL"))
hl_envelope.grid(column = 0,row = 11,columnspan=2)

wall_area_text = tk.Label(text="Area of walls [m2]:")
wall_area_text.grid(column = 0,row = 12)
wall_area_entry = tk.Entry(width = 20)
wall_area_entry.grid(column = 1,row = 12)
wall_area_entry.delete(0,tk.END)
wall_area_entry.insert(0,"6.42")

wall_u_text = tk.Label(text="U-value of walls [W/m2K]:")
wall_u_text.grid(column = 0,row = 13)
wall_u_entry = tk.Entry(width = 20)
wall_u_entry.grid(column = 1,row = 13)

win_u_text = tk.Label(text="U-value of window [W/m2K]:")
win_u_text.grid(column = 0,row = 14)
win_u_entry = tk.Entry(width = 20)
win_u_entry.grid(column = 1,row = 14)


#Ventilation ----------------------------------------------------
hl_ventilation = tk.Label(text="Ventilation",font=("ARIAL"))
hl_ventilation.grid(column = 0,row = 15,columnspan=2)

inf_text = tk.Label(text="Infiltration [m3/h]:")
inf_text.grid(column = 0,row = 16)
inf_entry = tk.Entry(width = 20)
inf_entry.grid(column = 1,row = 16)

vent_text = tk.Label(text="Pot. Mechanical Ventilaition:")
vent_text.grid(column = 0,row = 17)
vent_entry = tk.Entry(width = 20)
vent_entry.grid(column = 1,row = 17)

vent_h_text = tk.Label(text="Pot. Vent. operating hours [h]:")
vent_h_text.grid(column = 0,row = 18)
vent_h_entry = tk.Entry(width = 20)
vent_h_entry.grid(column = 1,row = 18)

vent_temp_text = tk.Label(text="Pot. Vent. input temperature:")
vent_temp_text.grid(column = 0,row = 19)
vent_temp_entry = tk.Entry(width = 20)
vent_temp_entry.grid(column = 1,row = 19)

#results --------------------------------------------------------------------------
but_weather = tk.Button(text="Import EPW Weatherfile",width = 80,command=ImportWeather)
but_weather.grid(column = 0,row = 21,columnspan=4)

but_calc = tk.Button(text="Calculate",width = 80,command=SolarGainCalc,state=tk.DISABLED)
but_calc.grid(column = 0,row = 20,columnspan=4)

hl_results = tk.Label(text="Results",font=("ARIAL"))
hl_results.grid(column = 2,row = 0,columnspan=2)

date_text = tk.Label(text = 'Specify date [dd]:')
date_text.grid(column = 2,row = 1,columnspan=1)
date_entry = tk.Entry(width = 10)
date_entry.grid(column = 2,row = 2,columnspan=1)

month_text = tk.Label(text = 'Specify month [mm]:')
month_text.grid(column = 3,row = 1,columnspan=1)
month_entry = tk.Entry(width = 10)
month_entry.grid(column = 3,row = 2,columnspan=1)

but_plot = tk.Button(text="Plot",width = 40,command=plot,state=tk.DISABLED)
but_plot.grid(column = 2,row = 17,columnspan=2)

but_export = tk.Button(text="Export Plot",width = 40,command=export_plot,state=tk.DISABLED)
but_export.grid(column = 2,row = 18,columnspan=2)

but_export_data = tk.Button(text="Export Data",width = 40,command=export_data,state=tk.DISABLED)
but_export_data.grid(column = 2,row = 19,columnspan=2)

but_plot.config(state=tk.DISABLED)
but_export.config(state=tk.DISABLED)
but_export_data.config(state=tk.DISABLED)

but_about = tk.Button(text="About",width = 20,command=about)
but_about.grid(column = 0,row = 22,columnspan=1)

version = tk.Label(text="Version 1.0 27.05.2022")
version.grid(column = 3,row = 22,columnspan=1)

window.mainloop()





