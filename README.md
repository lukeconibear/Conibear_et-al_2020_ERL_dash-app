### Interactive plot
Code for an interactive plot ([here](http://lukeconibear.pythonanywhere.com/)) visualising how a complete transition to clean household energy in India can save one-quarter of the healthy life lost to particulate matter pollution exposure in India.  
For more information, see the paper [here](https://doi.org/10.1088/1748-9326/ab8e8a).  

### Setup Python environment
- Create a conda environment with the required libraries from the config file (.yml) in the repository:
```
conda env create --name interactiveplot --file=interactiveplot.yml
```
- Or create your own using:
```
conda create -n interactiveplot -c conda-forge dash dash-core-components dash-html-components dash-bootstrap-components pandas numpy geopandas shapely plotly
``` 
