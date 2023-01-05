import streamlit as st
from bs4 import BeautifulSoup
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
st.set_page_config(
		page_title="California Water Supply Index",
		layout="wide",
		page_icon="🌊",
	)

url = 'https://cdec.water.ca.gov/reportapp/javareports?name=wsihist'
def get_tables():
	url = 'https://cdec.water.ca.gov/reportapp/javareports?name=wsihist'
	R = requests.get(url)
	soup = BeautifulSoup(R.text,'html.parser')
	pres = soup.find_all('pre')

	T = pres[0]
	brs = T.string.split('\r\n\r\n')
	return brs

abbrs = {
	"W":"Wet Year",
	"AN":"Above Normal Year",
	"BN":"Below Normal Year",
	"D":"Dry Year",
	"C":"Critical Year",
	}
class Location:
	def __init__(self, name, reconstructed_cols,forecast_cols,years):
		self.name = name
		self.reconstructed_cols = reconstructed_cols
		self.forecast_cols = forecast_cols
		self.tables = get_tables()

		filter_years = lambda df: df.loc[(df['Water Year'] >= years[0]) & (df['Water Year'] <= years[1])]
		
		try:
			self.reconstructed_df = self.reconstructed().pipe(filter_years)
			self.forecast_df = self.forecast().pipe(filter_years)

		except Exception as e:
			st.error(f"Error loading data for {self.name}\n{e}")
			
			st.markdown(self.tables[3])
			# st.markdown(self.tables[11])
		
	def reconstructed(self):
		table_text = self.tables[3]
		# st.markdown(table)
		try:	
			# st.markdown(table)
			table = BeautifulSoup(table_text,features="lxml").find_all('p')[0]
			rows = [i.split('   ') for i in table.text.split('\r\n')[9:]]
			df = pd.DataFrame(rows)
			# display(df)
			data = df.iloc[:,self.reconstructed_cols]
			# display(data)
			data.columns = ["Water Year",'Oct-Mar','Apr-Jul','WYsum','Index','Year type']
			data = data.astype({'Water Year':'int','Oct-Mar':'float64','Apr-Jul':'float64','WYsum':'float64','Index':'float64','Year type':'string'})

			data['Year type'] = data['Year type'].pipe(lambda x: x.str.strip().map(abbrs))

			return data
		except Exception as e:
			st.error(f"Error loading data for {self.name}\n{e}")
			st.markdown(table_text)
		
	def forecast(self):
		table_text = self.tables[11]
		# st.markdown(table)
		try:
			table = BeautifulSoup(table_text,features="lxml").find_all('p')[0]	
			rows = [i.split('   ') for i in table.text.split('\r\n')[3:]]
			df = pd.DataFrame(rows)
			# data = df[[self.reconstructed_cols]]
			data = df.iloc[:,self.forecast_cols]
			data.columns = ["Water Year",'Index','Year type']
			data = data.astype({'Water Year':'int','Index':'float64','Year type':'string'})
			data['Year type'] = data['Year type'].pipe(lambda x: x.str.strip().map(abbrs))
			return data
		except Exception as e:
			st.error(f"Error loading data for {self.name}\n{e}")
			st.markdown(table_text)


def plot_location(location):
	# https://plotly.com/python/time-series/#displaying-period-data
	# st.markdown(y_max)
	water_year_colors = {
		"Wet Year": "blue",
		"Above Normal Year": "green",
		"Below Normal Year": "purple",
		"Dry Year": "orange",
		"Critical Year": "red",
		}


	fig1 = px.bar(
		location.reconstructed_df,
		x='Water Year',
		y='Index',
		color="Year type",
		# symbol="point_id",
		color_discrete_map=water_year_colors,
		
		
	)

	fig1.update_traces(width=.7)

	fig2 = px.scatter(
		location.forecast_df,
		x='Water Year',
		y='Index',
		color="Year type",
		color_discrete_map=water_year_colors,
		# size=3
	)
	fig2.update_traces(
		marker_size=16,
		marker_line_width=4,
		marker_line_color='DarkSlateGrey',
		# marker_color='MediumPurple'
		)

	fig = go.Figure(data=fig1.data + fig2.data)
	# only show Index on hover
	# fig.update_traces(hovertemplate=)

	fig.update_layout(hovermode="x unified")

	return fig

def display_elements(location):
	st.plotly_chart(plot_location(location),use_container_width=True)
	
	col1,col2 = st.columns(2)
	with col1:
		st.markdown(f"## Reconstructed Values")
		st.dataframe(location.reconstructed_df.style.format(subset=['Oct-Mar','Apr-Jul','WYsum','Index'], formatter="{:.2f}"))

	with col2:
		st.markdown(f"## Forecast Values")
		st.dataframe(location.forecast_df.style.format(subset=['Index'], formatter="{:.2f}"))

st.title('California Water Supply Index')
# water_years = self.reconstructed_df['Water Year']
# water_years = [1900,2025]
y_max, y_min = 1900,2025
# y_max, y_min = int(water_years.max()), int(water_years.min())
years = st.slider('Water Year',min_value=y_min,max_value=y_max,value=[y_min,y_max])
st.markdown("Bar chart shows reconstructed values. Scatter plot shows forecast values. Hover over a point to see the index values.")

SJ_tab,SV_tab = st.tabs(['San Joaquin Valley','Sacramento Valley'])

with SJ_tab:
	L = Location('San Joaquin Valley',reconstructed_cols=[0,7,8,9,10,11],forecast_cols=[0,13,15],years=years)
	display_elements(L)
	

with SV_tab:
	L = Location('Sacramento Valley',reconstructed_cols=[0,1,2,3,4,5],forecast_cols=[0,4,6],years=years)
	display_elements(L)

st.markdown(f"Original data: [California Department of Water Resources]({url})")