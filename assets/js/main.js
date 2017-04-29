class MapViewer {
  constructor(elementId){
    //First init the map and heatmap
    this.currentCityData = null;
    this.baseLayer = L.tileLayer(
      'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18
      }
    );
    this.heatmapLayer = new HeatmapOverlay({
      radius: .005,
      maxOpacity: .6,
      scaleRadius: true, // scales the radius based on map zoom
      useLocalExtrema: false, // if set to false the heatmap uses the global maximum for colorization
      latField: 'lat',
      lngField: 'lng',
      valueField: 'value'
    });
    this.map = new L.Map(elementId, {
      center: new L.LatLng(37.77086432692309, -122.41304015000001),
      zoom: 12,
      layers: [this.baseLayer, this.heatmapLayer]
    });
    //register for events
    $('#city-select').change(this.onCitySelect.bind(this))
    $('#time-select').change(this.onTimeSelect.bind(this))
    //load inital heatmap data
    this.onCitySelect();
  }
  onCitySelect(){
    this._getHeatmapData($('#city-select').val())
      .then((data)=>{
        this.currentCityData = data;
        this.map.panTo(new L.LatLng(
          (data[0].viewport.left+data[0].viewport.right)/2,
          (data[0].viewport.top+data[0].viewport.bottom)/2));
        this.onTimeSelect();
      })
  }
  onTimeSelect(){
    var time = parseFloat($('#time-select').val())
    $('#time-text').text(`${((Math.floor(time)+11)%12+1)}:${time%1?'30':'00'}${time>12?'pm':'am'}`)
    time = Math.floor(time)*100 + time%1*60
    this._setHeatmapData(time);
  }
  _getHeatmapData(city){
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
  _setHeatmapData(time){
    time = parseInt(time)
    //var max = this.currentCityData
    //  .map((d)=>d.avgValue)
    //  .sort((a,b)=>b-a)[0];
    var max = this.currentCityData
      .find((d)=>d.time===time)
      .avgValue
    var kmeans = this.currentCityData
      .find((d)=>d.time===time)
      .kmeans
    var data = {
      data: kmeans.map((e)=>{ return {lng:e[0], lat:e[1], value:[2]} }), //exp data point {lat: 24.6408, lng:46.7728, count: 3}
      min: 1,
      max: max,
    }
    this.heatmapLayer.setData(data);
  }
}

$(document).ready(function(){
  window.viewer = new MapViewer('map');
})
