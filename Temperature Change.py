import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from calendar import month_abbr
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv("TUM00017237.csv")
df=df[["TUM00017237", "19730105" , "TMAX", "150"]]
df.rename({"TUM00017237":"ID", "19730105":"Date" , "TMAX":"Element", "150":"Data_Value"}, axis=1, inplace=True)
df["Date"]=pd.to_datetime(df["Date"], format="%Y%m%d")

df["Data_Value"] = df.loc[:,"Data_Value"]/10

tmin=df[df["Element"]=="TMIN"]
tmax=df[df["Element"]=="TMAX"]

tmin["Date"].replace(["2008-02-29","2012-02-29"], np.NaN, inplace=True)
tmin.dropna(inplace=True)
tmax["Date"].replace(["2008-02-29","2012-02-29"], np.NaN, inplace=True)
tmax.dropna(inplace=True)

df=tmin.merge(tmax, on="Date")
tmin=df[["Date", "Element_x","Data_Value_x"]]
tmin.rename({"Element_x":"Element", "Data_Value_x":"Data_Value"}, axis=1,inplace=True)
tmax=df[["Date", "Element_y","Data_Value_y"]]
tmax.rename({"Element_y":"Element", "Data_Value_y":"Data_Value"}, axis=1,inplace=True)
tmin.set_index("Date", inplace=True)
tmax.set_index("Date", inplace=True)
tmin["day"]=pd.DatetimeIndex(tmin.index).day
tmax["day"]=pd.DatetimeIndex(tmax.index).day
tmin["month"]=pd.DatetimeIndex(tmin.index).month
tmax["month"]=pd.DatetimeIndex(tmax.index).month

tmin2015 = tmin[(pd.to_datetime(tmin.index) >="2015") & (pd.to_datetime(tmin.index) <"2016")]
tminother=tmin[(pd.to_datetime(tmin.index) <"2015") & (pd.to_datetime(tmin.index) >="2005")]

tmax2015 = tmax[(pd.to_datetime(tmax.index) >="2015") & (pd.to_datetime(tmax.index) <"2016")]
tmaxother=tmax[(pd.to_datetime(tmax.index) <"2015") & (pd.to_datetime(tmax.index) >="2005")]

tmin2015["days"]=[x-datetime(2014,12,31) for x in tmin2015.index]
tmin2015["days"]=tmin2015["days"].dt.days.astype("int16")
tmax2015["days"]=[x-datetime(2014,12,31) for x in tmin2015.index]
tmax2015["days"]=tmax2015["days"].dt.days.astype("int16")

tmin2015=tmin2015.groupby(["month", "day"]).min()
tminother=tminother.groupby(["month", "day"]).min()
tmax2015=tmax2015.groupby(["month", "day"]).max()
tmaxother=tmaxother.groupby(["month", "day"]).max()

tmin2015=tmin2015.merge(tminother, on=["month","day"])
tmin2015=tmin2015[tmin2015["Data_Value_x"]<tmin2015["Data_Value_y"]]
tmax2015=tmax2015.merge(tmaxother, on=["month","day"])
tmax2015=tmax2015[tmax2015["Data_Value_x"]>tmax2015["Data_Value_y"]]

index=np.arange(1,366)
fig=plt.figure(facecolor="black")
plt.style.use("dark_background")

plt.plot(index, tminother["Data_Value"], color="blue", label="Min temperature (°C) values from the years 2005 through 2014")
plt.plot(index, tmaxother["Data_Value"], color="red", label="Max temperature (°C) values from the years 2005 through 2014")

plt.scatter(tmax2015["days"], tmax2015["Data_Value_x"], 65, alpha=0.4,color="fuchsia", label="Record breaking high temperatures (°C) from 2015", marker="^")
plt.scatter(tmin2015["days"], tmin2015["Data_Value_x"], 65, alpha=0.4,color="cyan", label="Record breaking low temperatures (°C) from 2015", marker="v")

polygon=plt.fill_between(index,tminother["Data_Value"],tmaxother["Data_Value"],alpha=0.1)

plt.title("Change in Temperature (°C) in Denizli, Turkey")
plt.xlabel("Months of the year")
plt.xticks([1,32,60,91,121,152,182,213,244,274,305,335])
plt.ylabel("Temperature (°C)")
plt.legend()
plt.xlim((1,365))
plt.ylim((tminother["Data_Value"].min()-5,tmaxother["Data_Value"].max()+5))
plt.gca().set_xticklabels(month_abbr[1:])
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)

verts=np.vstack([p.vertices for p in polygon.get_paths()])
ymin,ymax=verts[:,1].min(), verts[:,1].max()

imdata=np.array([np.interp(np.linspace(ymin,ymax,1000), [y1i,y2i],np.arange(2)) for y1i,y2i in zip(tminother["Data_Value"],tmaxother["Data_Value"])]).T

gradient= plt.imshow(imdata,cmap="turbo", aspect="auto", origin="lower", extent=[index.min(),index.max(), ymin,ymax])
gradient.set_clip_path(polygon.get_paths()[0], transform=plt.gca().transData)

plt.show()
