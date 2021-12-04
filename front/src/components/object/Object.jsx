import {
  CalendarToday, DeleteOutline,
  LocationSearching,
  MailOutline,
  PermIdentity,
  PhoneAndroid,
  Publish,
} from "@material-ui/icons";
import {Link, useParams} from "react-router-dom";
import "./object.css";
import MapDraw from "../map/Map";
import React, {useState} from "react";

export default function Object1() {
  let { objectId } = useParams();
  const [data, setData] = useState(0);

  fetch(`http://84.252.74.223:8000/get_object/?object_id=${objectId}`)
      .then(res => res.json())
      .then(
          (result) => {
            console.log(result);
            setData(result['features'][0]);
          })


  console.log(objectId, data)

  return (
    <div className="object">
      <div className="objectTitleContainer">
        <h1 className="objectTitle">Изменить Объект</h1>
        <Link to="/newObject">
          <button className="objectAddButton">Создать</button>
        </Link>
      </div>
      <div className="objectContainer">
        <div className="objectUpdate">
          <span className="objectUpdateTitle">Изменить</span>
          <form className="objectUpdateForm">
            <div className="objectUpdateLeft">
              <div className="objectUpdateItem">
                <label>Имя</label>
                <input
                  type="text"
                  placeholder="Сила Сибири"
                  className="objectUpdateInput"
                />
              </div>
              <div className="objectUpdateItem">
                <label>Теги</label>
                <input
                  type="text"
                  placeholder="{'Организация': 'ООО Газпром'}"
                  className="objectUpdateInput"
                />
              </div>
              <div className="objectUpdateItem">
                <label>Отступы</label>
                <input
                  type="number"
                  placeholder={10}
                  className="objectUpdateInput"
                />
              </div>
              <div className="objectUpdateItem">
                <label>Геометрия</label>
                <input
                    type="text"
                    placeholder="{type:Polygon}"
                    className="objectUpdateInput"
                />
              </div>
            </div>

          </form>
          <div className={"objectUpdateButtonContainer"}>
          <button type={"submit"} className="objectUpdateButton">Обновить</button>
            <>
              {/*<Link to={"/object/" + params.row.id}>*/}
              {/*  <button className="objectListEdit">Изменить</button>*/}
              {/*</Link>*/}
              <DeleteOutline
                  className="objectListDelete"
                  // onClick={() => this.handleDelete(params.row.id)}
              />
            </>
          </div>
        </div>
        <div className="objectShow">
          <MapDraw geometryData={data}/>
        </div>

      </div>


    </div>
  );
}
