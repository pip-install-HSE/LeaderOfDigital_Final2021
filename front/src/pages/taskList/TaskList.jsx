import "./taskList.css";
import { DataGrid } from "@material-ui/data-grid";
import { DeleteOutline } from "@material-ui/icons";
import {objectData, tasksData} from "../../dummyData";
import { Link } from "react-router-dom";
import React from 'react'

export default class TaskList extends React.Component {
    state = {
        tasksData: []
    }

    componentDidMount() {
        fetch(`http://84.252.74.223:8080/tasks/`)
            .then(res => res.json())
            .then(
                (result) => {
                    console.log(result);
                    this.setState({
                        tasksData: result
                    });
                },
            )
        // this.setState({
        //     tasksData: tasksData
        // });

    }

    handleDelete = (id) => {
        this.props.onChangeData(this.props.tasksData.filter((item) => item.id !== id));
    };

    fetchObject(e){
        fetch(`http://84.252.74.223:8080/object/object_id=${e}`)
            .then(res => res.json())
            .then(
                (result) => {
                    console.log(result);
                    this.setState({
                        tasksData: result
                    });
                },
            )
    }

    columns = [
        {field: "id", headerName: "ID", width: 90},
        {field: "object_id", headerName: "Объект", width: 200,
            renderCell: (params) => {
                return (
                    <div className="productListItem">

                        {params.value}
                    </div>
                );
            }
        },
        {field: "data_datetime", headerName: "Дата и время", width: 200,
            type: 'dateTime',
            renderCell: (params) => {
                return (
                    <div className="productListItem">
                        {params.value}
                    </div>
                );
            },},
        // {field: "data_datetime", headerName: "Отступы", width: 20},

        {field: "oil_spill_chance", headerName: "Вероятность разлива", width: 200},
        {field: "cloudy", headerName: "Облачность", width: 200},
        {
            field: "action",
            headerName: "Действие",
            width: 150,
            renderCell: (params) => {
                return (
                    <>
                        <Link to={"/task/" + params.row.id}>
                            <button className="taskListEdit">Edit</button>
                        </Link>
                    </>
                );
            },
        },

    ];



    render() {
        return (
            <div className="taskList">
                <DataGrid
                    localeText='ru-RU'
                    rows={this.state.tasksData}
                    disableSelectionOnClick
                    columns={this.columns}
                    // pageSize={8}
                    checkboxSelection
                />
            </div>
        );
    }

}
