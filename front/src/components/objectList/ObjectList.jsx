import "./objectList.css";
import { DataGrid } from "@material-ui/data-grid";
import { DeleteOutline } from "@material-ui/icons";
import {objectData} from "../../dummyData";
import { Link } from "react-router-dom";
import React from 'react'



export default class ObjectList extends React.Component {

  handleDelete = (id) => {
      this.props.onChangeData(this.props.objectData.filter((item) => item.id !== id));
  };

  columns = [
    {field: "id", headerName: "ID", width: 90},
    {field: "name", headerName: "Имя", width: 200},
    {field: "padding", headerName: "Отступы", width: 200},
    {
      field: "action",
      headerName: "Действие",
      width: 150,
      renderCell: (params) => {
        return (
            <>
              <Link to={"/object/" + params.row.id}>
                <button className="objectListEdit">Edit</button>
              </Link>
            </>
        );
      },
    },


  ];



  render() {
    return (
        <div className="objectList">
          <DataGrid
              rows={this.props.objectData}
              disableSelectionOnClick
              columns={this.columns}
              // pageSize={8}
              checkboxSelection
          />
        </div>
    );
  }

}
