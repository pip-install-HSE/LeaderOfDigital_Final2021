import "./search.css";
import SearchField from "react-search-field";

import { ArrowDownward, ArrowUpward } from "@material-ui/icons";
import React from "react";

export default class Search extends React.Component {
    // const { data, setData } = useFetch();
    // let onChange = (text) => {
    //     console.log(text);
    // }
    // console.log(change)
    render () {
        return (
            <div className="search">
                <SearchField
                    placeholder="Search..."
                    onChange={this.props.onSearch}
                    // searchText="This is initial search text"
                    classNames="searchbar"
                />

            </div>
        );
    }
}
