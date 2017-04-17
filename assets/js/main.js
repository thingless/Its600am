function getData(city){
  city = city.toLowerCase().replace(/ /g,'_')
  return new Promise((resolve, reject)=>{
    $.ajax({
      url:ROOT_PATH+city+'.json',
      dataType:'json',
      success:resolve,
      error:reject
    })
  })
}

function setHeatmapData(jsonData, time){
  time = parseInt(time)
  var max = jsonData
    .map((d)=>d.avgValue)
    .sort((a,b)=>b-a)[0];
  var kmeans = jsonData
    .find((d)=>d.time===time)
    .kmeans
  var data = {
    data: kmeans.map((e)=>{ return {lng:e[0], lat:e[1], value:[2]} }), //exp data point {lat: 24.6408, lng:46.7728, count: 3}
    min: 1,
    max: max,
  }
  heatmapLayer.setData(data);
}

$(document).ready(function(){

//init map
var baseLayer = L.tileLayer(
  'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18
  }
);
heatmapLayer = new HeatmapOverlay({
  // radius should be small ONLY if scaleRadius is true (or small radius is intended)
  // if scaleRadius is false it will be the constant radius used in pixels
  radius: .005,
  maxOpacity: .6,
  // scales the radius based on map zoom
  scaleRadius: true,
  // if set to false the heatmap uses the global maximum for colorization
  // if activated: uses the data maximum within the current map boundaries
  //   (there will always be a red spot with useLocalExtremas true)
  useLocalExtrema: false,
  // which field name in your data represents the latitude - default "lat"
  latField: 'lat',
  // which field name in your data represents the longitude - default "lng"
  lngField: 'lng',
  // which field name in your data represents the data value - default "value"
  valueField: 'value'
});
var map = new L.Map('map', {
  center: new L.LatLng(37.77086432692309, -122.41304015000001),
  zoom: 12,
  layers: [baseLayer, heatmapLayer]
});

getData('San Francisco').then((data)=>{
  setHeatmapData(data, 1200)
})

})
