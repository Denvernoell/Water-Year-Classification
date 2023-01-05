import streamlit as st
from bs4 import BeautifulSoup
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

url = 'https://cdec.water.ca.gov/reportapp/javareports?name=wsihist'
R = requests.get(url)
soup = BeautifulSoup(R.text,'html.parser')
pres = soup.find_all('pre')

T = pres[0]
brs = T.string.split('\r\n\r\n')

class Location:
	def __init__(self, name, reconstructed_cols,forecast_cols):
		self.name = name
		self.reconstructed_cols = reconstructed_cols
		self.forecast_cols = forecast_cols
		self.forecast()
		self.reconstructed()
		
	def reconstructed(self):
		table = brs[3]
		table = BeautifulSoup(table).find_all('p')[0]
		rows = [i.split('   ') for i in table.text.split('\r\n')[9:]]
		df = pd.DataFrame(rows)
		# display(df)
		data = df.iloc[:,self.reconstructed_cols]
		# display(data)
		data.columns = ["Water Year",'Oct-Mar','Apr-Jul','WYsum','Index','Year type']
		data = data.astype({'Water Year':'int','Oct-Mar':'float64','Apr-Jul':'float64','WYsum':'float64','Index':'float64','Year type':'string'})

		abbrs = {
			"W":"Wet Year",
			"AN":"Above Normal Year",
			"BN":"Below Normal Year",
			"D":"Dry Year",
			"C":"Critical Year",
			}
		data['Year type'] = data['Year type'].pipe(lambda x: x.str.strip().map(abbrs))

		self.reconstructed_df = data
		
	def forecast(self):
		table = brs[11]
		table = BeautifulSoup(table).find_all('p')[0]
		rows = [i.split('   ') for i in table.text.split('\r\n')[3:]]
		df = pd.DataFrame(rows)
		# data = df[[self.reconstructed_cols]]
		data = df.iloc[:,self.forecast_cols]
		data.columns = ["Water Year",'Index','Year type']
		data = data.astype({'Water Year':'int','Index':'float64','Year type':'string'})
		# data['Index'] = data['Index']
		self.forecast_df = data
		




# SV.forecast_df
# SV.reconstructed_df
# .map(abbrs)



def plot_location(location):
	# https://plotly.com/python/time-series/#displaying-period-data
		
	fig1 = px.bar(
		location.reconstructed_df,
		x='Water Year',
		y='Index',
		color="Year type",
		# symbol="point_id",
		
	)

	# fig1 = go.Figure()
	# rec = location.reconstructed_df
	# fig1.add_trace(go.Bar(
	# 	x=rec['Water Year'],
	# 	y=rec['Index'],
	# 	# color=rec["Year type"],
	# 	marker_color=rec["Year type"],
	# 	xperiod="Y1",
	#     xperiodalignment="middle",
	# 	# symbol="point_id",
		
	# ))
	# fig1.update_xaxes(tickmode='linear', ticklabelmode="period")
	fig1.update_traces(width=.7)

	fig2 = px.scatter(
		location.forecast_df,
		x='Water Year',
		y='Index',
		# color="transducer_id",
		# size=3
	)
	fig2.update_traces(marker_size=8,marker_line_width=2,marker_line_color='DarkSlateGrey',marker_color='MediumPurple')

	fig = go.Figure(data=fig1.data + fig2.data)
	return fig



SV = Location('Sacramento Valley',reconstructed_cols=[0,1,2,3,4,5],forecast_cols=[0,4,6])
SJ = Location('San Joaquin Valley',reconstructed_cols=[0,7,8,9,10,11],forecast_cols=[0,13,15])

st.set_page_config(
		page_title="California Water Supply Index",
		layout="wide",
		page_icon="🌊",
	)
st.title('California Water Supply Index')

SJ_tab,SV_tab = st.tabs(['San Joaquin Valley','Sacramento Valley'])

with SJ_tab:
	st.plotly_chart(plot_location(SJ),use_container_width=True)
with SV_tab:
	st.plotly_chart(plot_location(SV),use_container_width=True)