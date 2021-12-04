import ReactMapboxGl, {GeoJSONLayer, Popup} from 'react-mapbox-gl';
import DrawControl from 'react-mapbox-gl-draw';
import React from "react";

// Don't forget to import the CSS
import "./map.css";
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css';
import 'mapbox-gl/dist/mapbox-gl.css';
// import 'mapboxgl'
// import LngLat from "mapbox-gl/src/geo/lng_lat";
// import LngLatBounds from "mapbox-gl/src/geo/lng_lat_bounds";
import L from 'leaflet'

const Map = ReactMapboxGl({
    accessToken:
        'pk.eyJ1IjoiZmFrZXVzZXJnaXRodWIiLCJhIjoiY2pwOGlneGI4MDNnaDN1c2J0eW5zb2ZiNyJ9.mALv0tCpbYUPtzT7YysA2g'
});

export default class MapDraw extends React.Component{
    state = {
        station: undefined,
        fitBounds: undefined
    }

    // updateBounds(polygon){
    //     // console.log({lng:polygon[0], lat:polygon[1]})
    //     // let fit = new L.Polygon(polygon).
    //     // let southWest = new LngLat(fit['_southWest']['lat'], fit['_southWest']['lng']);
    //     // let northEast = new LngLat(fit['_northEast']['lat'], fit['_northEast']['lng']);
    //     // let center = new LngLatBounds(southWest, northEast).getCenter();
    //     // console.log(fit)
    //     this.setState(
    //         {
    //             fitBounds: polygon
    //         }
    //     )
    //
    // }


    onDrawCreate = ({ features }) => {
        console.log(features);
    };

    onDrawUpdate = ({ features }) => {
        console.log({ features });
    };

    fillOnClick = ({ features, lngLat }) => {
        // this.setState(
        //     {
        //         fitBounds: lngLat
        //     }
        // )
        console.log({ lngLat, features });
        this.setState({station: {
                name: features[0].properties.name,
                position: [lngLat.lng, lngLat.lat],
        }})

    }

    render () {return (
            <div className="map-container">
                <Map
                    style="mapbox://styles/mapbox/streets-v9"
                    containerStyle={{
                        height: "600px",
                        width: "100%"
                    }}
                    // center={[100, 61]}
                    center={[76.672495, 61.460976]}
                    zoom={[10]}
                    fitBounds={this.state.fitBounds}

                >
                    {this.state.station && (
                        <Popup coordinates={this.state.station.position} offset={{
                            'bottom-left': [12, -38],  'bottom': [0, -38], 'bottom-right': [-12, -38]
                        }}>
                                <div>{this.state.station.name}</div>
                        </Popup>
                    )}
                    {/*<Layer type="symbol" id="marker" layout={{ 'icon-image': 'marker-15' }}>*/}
                    {/*    <Feature coordinates={[-0.481747846041145, 51.3233379650232]} />*/}
                    {/*</Layer>*/}
                    <GeoJSONLayer
                        data={this.props.geometryData}
                        symbolLayout={{
                            "text-field": "{name}",
                            "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
                            "text-offset": [0, 0.6],
                            "text-anchor": "top"
                        }}
                        fillLayout={{ "visibility": 'visible' }}
                        fillPaint={{
                            'fill-color': '#0080ff', // blue color fill
                            'fill-opacity': 0.5
                        }}
                        fillOnClick={this.fillOnClick}
                    />
                    <GeoJSONLayer
                        data={this.props.tasksData}
                        fillLayout={{ "visibility": 'visible' }}
                        fillPaint={{
                            'fill-color': '#f30404', // red color fill
                            'fill-opacity': 0.5
                        }}
                        fillOnClick={this.fillOnClick}
                    />

                    <DrawControl
                        // position="top-left"
                        displayControlsDefault={false}
                        controls= {{
                            polygon: true,
                            line_string: true,
                            trash: true
                        }}
                        // defaultMode="draw_polygon"
                    />
                </Map>
            </div>
        );
    }
}

