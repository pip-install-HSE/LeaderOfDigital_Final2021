import Chart from "../../components/chart/Chart";
import FeaturedInfo from "../../components/featuredInfo/FeaturedInfo";
import "./home.css";
import {objectData, objectData2, userData} from "../../dummyData";
import WidgetSm from "../../components/widgetSm/WidgetSm";
import WidgetLg from "../../components/widgetLg/WidgetLg";
import Search from "../../components/search/Search";
import MapDraw from "../../components/map/Map";
import ObjectList from "../../components/objectList/ObjectList";
import React from 'react'
import TextField from '@mui/material/TextField';
import TwoDatePickers from "../../components/twodatepickers/TwoDatePickers";
import LinearProgressWithLabel from "../../components/progressbar/ProgressBar";


export default class Home extends React.Component {
    state = {
        objectData: [],
        geometryData: [],
        tasksGeometry:[],
        progress: 0,
    }

    componentWillUnmount() {
        clearInterval(this.interval);
    }

    onSearch = (e) => {
        // console.log(e);
        fetch(`http://84.252.74.223:8080/search/?object_name=${e}`)
            .then(res => res.json())
            .then(
                (result) => {
                    console.log(result[1]);
                    this.setState({
                        objectData: result[0],
                        geometryData : result[1]
                    });
                },
            )
        // this.render();
        // this.forceUpdate();
    };
    componentDidMount() {
        this.onSearch('');
    }



    onChangeData = (data) =>{
        console.log(data);
        this.setState({objectData: data})
    }

    setOilSpills = (tasks) => {

        if (tasks){
            this.setState({
                tasksGeometry: tasks
            })
            console.log(this.state.tasksGeometry)
        }
    }

      render() {
        return (
        <div className="home">
          {/*<FeaturedInfo />*/}
            <Search onSearch={this.onSearch}/>
          {/*<Chart data={userData} title="Аналитика инцедентов" grid dataKey="Actve User"/>*/}
            <MapDraw geometryData={this.state.geometryData} tasksData={this.state.tasksGeometry}/>
            <TwoDatePickers setOilSpills={this.setOilSpills} objects={this.state.objectData} progress={this.state.progress}/>
            <LinearProgressWithLabel value={this.state.progress} />
            <ObjectList objectData={this.state.objectData} onChangeData={this.onChangeData}/>
          {/*<div className="homeWidgets">*/}
          {/*  <WidgetSm/>*/}
          {/*  <WidgetLg/>*/}
          {/*</div>*/}
        </div>
      );
}
}
