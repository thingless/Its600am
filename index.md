<div id="map">
</div>
<h3>
Showing life at <span id="time-text">2:30am</span> in
<select id="city-select">
  <option value="San Francisco">San Francisco</option>
  <option value="New York">New York</option>
  <option value="Las Vegas">Las Vegas</option>
  <option value="Boston">Boston</option>
  <option value="Los Angeles">Los Angeles</option>
  <option value="Chicago">Chicago</option>
  <option value="Nashville">Nashville</option>
  <option value="Houston">Houston</option>
  <option value="Denver">Denver</option>
  <option value="Cincinnati">Cincinnati</option>
</select>
<input id="time-select" class="form-control" type="range" min="5" max="23.5" step="0.5" ng-model="slider['contrast']" value="6">
</h3>

## About

The time lapse above allows you to see open restaurants, bars, cafes, etc in large cities around the US. Select a city from the dropdown and then adjust the time by moving the slider.

The location of restaurants and their hours of operation is based off of Google Maps data. The code for this site can be found on
[GitHub](https://github.com/thingless/its600am/). The raw data is not aviablie due to Google's licensing.
