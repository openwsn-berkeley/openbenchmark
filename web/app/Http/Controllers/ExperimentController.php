<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use CommandHandler;
use ConfigParser;
use App\Experiment;
use Response;


class ExperimentController extends Controller
{

    function __construct() {
        $this->config_parser   = new ConfigParser();
        $this->cmd_handler     = new CommandHandler();

        // Temporarily hardcodes user id. The id shall be taken from the database
        // by searching the database for a user with the same bearer token as the 
        // one provided in the header of a request 
        $this->user_id         = 1; 
    }

    function start($scenario, $testbed, $simulator=false, $firmware=null) {
        $this->reserve_nodes($scenario, $testbed);
        $this->flash_firmware($firmware);

        sleep($this->cmd_handler::OV_GUARD_TIME); //A guard time to wait for the nodes to start sending serial data before running OV
        
        $this->start_ov($scenario, $testbed, $simulator);
    }

    function upload() {
        return response()->json([
            'status' => 'success'
        ]);
    }


    // Experiment start-up steps
    function reserve_nodes($scenario, $testbed) {
        return $this->cmd_handler->reserve_nodes($this->user_id, $scenario, $testbed);
    }

    function flash_firmware($firmware=null) {
        return $this->cmd_handler->flash_firmware($this->user_id, $firmware);
    }

    function start_ov($scenario, $testbed, $simulator=false) {
        return $this->cmd_handler->start_ov($this->user_id, $scenario, $testbed, $simulator);
    }

    function exp_terminate() {
        return $this->cmd_handler->exp_terminate($this->user_id);
    }


    // Scenario data retrieval
    function get_config_data($param, $scenario=null, $testbed=null) {
        if ($param == null) 
            return ErrorResponse::response(422, '`param` is a required argument');
        else if ($param == 'nodes' && ($scenario == null or $testbed == null))
            return ErrorResponse::response(422, 'If `param` is set to `nodes`, `scenario` and `testbed` cannot be null');
        else 
            return response()->json($this->config_parser->get_config_data($param, $scenario, $testbed));
    }

    function store_experiment(Request $request) {
        $experiment = new Experiment;
        $experiment->experiment_id = $request->experiment_id;
        $experiment->scenario      = $request->scenario;
        $experiment->testbed       = $request->testbed;
        $experiment->firmware      = $request->firmware;
        $experiment->save();

        return Response::json([
            "success"     => true
        ], 200);
    }

    function get_experiment($id) {
        return Experiment::where('experiment_id', $id)->get();
    }

}