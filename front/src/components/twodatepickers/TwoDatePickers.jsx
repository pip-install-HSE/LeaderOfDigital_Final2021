import TextField from "@mui/material/TextField";
import React from "react";
import './twodatepickers.css'

export default class TwoDatePickers extends React.Component {
    state = {
        st_value: "2021-12-03T10:30",
        end_value: "2021-12-03T10:30",
        real_start_date: undefined,
        real_end_date: undefined,
    }

    _handleSt = (e) => {
        this.setState({
            st_value: e.target.value
        })
    }

    _handleEnd = (e) => {
        this.setState({
            end_value: e.target.value
        })
    }

    makeRequest () {
        let os = []
        if (this.props.objects){
            os = this.props.objects
        }
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                object_ids: os.map(s=>s.id),
                datetime_start: this.state.st_value,
                datetime_end: this.state.end_value,
            })
        };
        fetch(`http://84.252.74.223:8080/oil_spills/`, requestOptions)
            .then(res => res.json())
            .then(
                (result) => {
                    // console.log(result);
                    this.props.setOilSpills(result);
                })
    }

    onClick = () =>{
        console.log(this.state.st_value)
        this.interval = setInterval(() => this.makeRequest(), 5000);
        if (!this.state.real_start_date && !this.state.real_end_date){
            this.setState({
                real_start_date: this.state.st_value,
                real_end_date: this.state.end_value
            })
        }
        this.setState({
            st_value: addDays(new Date(this.state.st_value))
        })
        function addDays(date, days) {
            return new Date(date.getTime() + days*24*60*60000);
        }
        console.log(new Date(this.state.st_value));
    }
    componentWillUnmount() {
        clearInterval(this.interval);
    }
    render(){
        return <div  className="twodatepickers">
                <TextField className="startdatepicker"
                id="datetime-local"
                label="Начало периода"
                type="datetime-local"
                sx={{ width: 250 }}
                InputLabelProps={{
                    shrink: true,
                }} onChange={this._handleSt}
                           value={this.state.st_value}
            />
                <TextField className="enddatepicker"
                    id="datetime-local"
                    label="Конец периода"
                    type="datetime-local"
                    sx={{ width: 250 }}
                    InputLabelProps={{
                        shrink: true,
                    }} onChange={this._handleEnd}
                           value={this.state.end_value}
                />
                <button className="submitTwoDatePickers" onClick={this.onClick}>Установить</button>
            </div>


        // </div>

    }

}