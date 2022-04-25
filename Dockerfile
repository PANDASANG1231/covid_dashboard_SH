FROM zwj63518583/python_env

RUN apt-get update
RUN apt-get install make

RUN pip install geopandas
RUN pip install plotly
RUN pip install dash 
RUN pip install dash-bootstrap-components
RUN pip install wordcloud

RUN echo 'installing finish'