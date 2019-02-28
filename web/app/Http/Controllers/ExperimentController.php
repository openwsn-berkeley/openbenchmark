<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use CommandHandler;
use ScenarioParser;

class ExperimentController extends Controller
{

    function __construct() {
        $this->scenario_parser = new ScenarioParser();
        $this->command_handler = new CommandHandler();
    }

    function start() {
        $this->cmd_handler->reserve_nodes();
        $this->cmd_handler->otbox_start();

        sleep($cmd_handler::OV_GUARD_TIME); //A guard time to wait for the nodes to start sending serial data before running OV
        
        $this->cmd_handler->ov_start();

        sleep($cmd_handler::OV_LOG_GUARD_TIME); //A guard time to wait for OV to start writing the log
        
        return $this->cmd_handler->ov_monitor();
    }

    function upload() {
        return response()->json([
            'status' => 'success'
        ]);
    }

    function exp_terminate() {
        return $this->cmd_handler->exp_terminate();
    }


    // Functions for test routes
    function reserve_exp() {
        return $this->cmd_handler->reserve_nodes();
    }

    function start_otbox() {
        return $this->cmd_handler->otbox_start();
    }

    function start_ov() {
        return $this->cmd_handler->ov_start();
    }

    function start_watcher() {
        return $this->cmd_handler->ov_monitor();
    }
}
