import {Box, Typography} from "@material-ui/core";
import LinearProgress from '@mui/material/LinearProgress';
import React from 'react';

export default class LinearProgressWithLabel extends React.Component{



    render() {return (
    <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <Box sx={{ width: '100%', mr: 1 }}>
            <LinearProgress variant="determinate" {...this.props} />
        </Box>
        <Box sx={{ minWidth: 35 }}>
            <Typography variant="body2" color="text.secondary">{`${Math.round(
                this.props.value,
            )}%`}</Typography>
        </Box>
    </Box>
);
}
}