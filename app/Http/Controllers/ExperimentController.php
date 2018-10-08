<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Custom\CommandHandler;

class ExperimentController extends Controller
{
    function start() {
        $cmd_handler = new CommandHandler();

        $cmd_handler->reserve_nodes();
        $cmd_handler->otbox_start();

        sleep($cmd_handler::OV_GUARD_TIME); //A guard time to wait for the nodes to start sending serial data before running OV
        $cmd_handler->ov_start();

        sleep($cmd_handler::OV_LOG_GUARD_TIME); //A guard time to wait for OV to start writing the log
        return $cmd_handler->ov_monitor();
    }

    function upload() {
        return response()->json([
            'status' => 'success'
        ]);
    }

    function exp_terminate() {
        $cmd_handler = new CommandHandler();
        $cmd_handler->exp_terminate();

        return response()->json([
            'status' => 'terminated'
        ]);
    }


    // Functions for test routes
    function reserve_exp() {
        $cmd_handler = new CommandHandler();
        return $cmd_handler->reserve_nodes();
    }

    function start_otbox() {
        $cmd_handler = new CommandHandler();
        return $cmd_handler->otbox_start();
    }

    function start_ov() {
        $cmd_handler = new CommandHandler();
        return $cmd_handler->ov_start();
    }

    function start_watcher() {
        $cmd_handler = new CommandHandler();
        return $cmd_handler->ov_monitor();
    }
}
