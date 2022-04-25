FROM zwj63518583/python_env

RUN apt-get update
RUN apt-get install make

RUN \
  echo 'check' \ 
  pip install geopandas \ 
  pip install plotly \ 
  pip install dash \ 
  pip install dash-bootstrap-components \
  pip install wordcloud \
  echo 'installing finish'