import TextField from "@mui/material/TextField";
import React from "react";
import './twodatepickers.css'
import moment from "moment";

export default class TwoDatePickers extends React.Component {
    state = {
        st_value: "2021-12-03T10:30",
        end_value: "2021-12-06T10:30",
        real_start_date: undefined,
        real_end_date: undefined,
        notifySended: false
    }

    progressStep = 0
    progress = 0


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

    sendTelegramNotification(chat_id, text){
        let botToken = "5032450393:AAGaDjw3zD4NRwePBJXHCYUT7nymADzVY5Q";
        let url = `https://api.telegram.org/bot${botToken}/sendMessage?chat_id=${chat_id}&text=${text}`
        fetch(url).then(r => r.json())
    }

    makeRequest () {
        this.changeDates()
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
                    console.log(result);
                    if (result.features.length > 0 && !this.state.notifySended){
                        this.setState({
                            notifySended: true
                        })
                        this.sendTelegramNotification(446162145, "Новый нефтеразлив!!!")
                    }
                    this.props.setOilSpills(result);
                })
    }

    setProgressStep(){
        console.log(new Date(this.state.real_end_date) - new Date(this.state.real_start_date), new Date(this.state.real_end_date), new Date(this.state.real_start_date))
        let a = moment(this.state.st_value,'YYYYMMDDTh:mm');
        let b = moment(this.state.end_value,'YYYYMMDDTh:mm');
        this.progressStep = 100/b.diff(a, 'days');
        console.log(this.progressStep, new Date(this.state.end_value), new Date(this.state.st_value))
    }

    clear(){
        clearInterval(this.interval);
        this.setState({
            st_value: this.state.real_start_date,
            end_value: this.state.real_end_date,
            real_start_date: undefined,
            real_end_date: undefined,

        });
        this.progress = 0
        this.props.onChangeProgress(this.progress)
    }

    changeDates(){
        console.log(this.progressStep)
        // this.setProgressStep()
        // console.log(new Date(this.state.st_value), this.progress);
        if (!this.state.real_start_date && !this.state.real_end_date){
            this.progress = 0
            this.props.onChangeProgress(this.progress)
            console.log(this.state)
            this.setProgressStep()
            this.setState({
                real_start_date: this.state.st_value,
                real_end_date: this.state.end_value,
                end_value: moment(addDays(new Date(this.state.st_value), 1)).format('YYYY-MM-DDTh:mm'),
            })

        }else if (new Date(this.state.st_value) < new Date(this.state.real_end_date)){
            let st_val = moment(addDays(new Date(this.state.st_value), 1)).format('YYYY-MM-DDTh:mm');
            let end_val = moment(addDays(new Date(this.state.end_value), 1)).format('YYYY-MM-DDTh:mm');
            if (new Date(st_val) >= new Date(this.state.real_end_date))
            {
                this.clear()
                return
            }
            this.setState({
                st_value: st_val,
                end_value: end_val
            })

        } else{
            this.clear()
            return
        }
        this.progress = this.progress+this.progressStep
        this.props.onChangeProgress(this.progress)


        function addDays(date, days) {
            return new Date(date.getTime() + days*24*60*60000);
        }
    }

    onClick = () =>{
        this.interval = setInterval(() => this.makeRequest(), 1000);
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