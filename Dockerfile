FROM zwj63518583/python_env

RUN \
  echo 'check' \ 
  pip install geopandas \ 
  pip install plotly \ 
  pip install dash \ 
  pip install dash-bootstrap-components \
  pip install wordcloud \
  echo 'installing finish'