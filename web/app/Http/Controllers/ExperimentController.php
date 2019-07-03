<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use CommandHandler;
use ConfigParser;
use App\Classes\ErrorResponse;
use App\Experiment;
use App\Classes\SuccessResponse;
use Exception;


class ExperimentController extends Controller
{

    const FILE_DESTINATION = "/home/vagrant/openbenchmark/experiment_provisioner/firmware";

    function __construct() {
        $this->config_parser   = new ConfigParser();
        $this->cmd_handler     = new CommandHandler();

        // Temporarily hardcodes user id. The id shall be taken from the database
        // by searching the database for a user with the same bearer token as the 
        // one provided in the header of a request 
        $this->user_id         = 1; 
    }

    function start($scenario, $testbed, $simulator=false, $firmware=null) {
        $this->cmd_handler->reserve_nodes($this->user_id, $scenario, $testbed, false);
        $this->cmd_handler->flash_firmware($this->user_id, $firmware, false);

        sleep($this->cmd_handler::OV_GUARD_TIME); //A guard time to wait for the nodes to start sending serial data before running OV
        
        $this->cmd_handler->start_ov($this->user_id, $scenario, $testbed, ($simulator == "true"), false);
    }

    function upload(Request $request) {
        try {
            $file = $request->file("file");
            $new_filename = $this->create_random(10);

            if ($file != null) {
                $file->move(self::FILE_DESTINATION, $new_filename);

                return SuccessResponse::response(200, [
                    "action" => "firmware-upload",
                    "name"   => $new_filename,
                ]);
            } else {
                throw new Exception("Error uploading the file");
            }

        } catch (Exception $e) {
            return ErrorResponse::response(500, $e->getMessage());
        }
    }


    // Experiment start-up steps
    function reserve_nodes($scenario, $testbed) {
        return $this->cmd_handler->reserve_nodes($this->user_id, $scenario, $testbed);
    }

    function flash_firmware($firmware=null) {
        return $this->cmd_handler->flash_firmware($this->user_id, $firmware);
    }

    function start_ov($scenario, $testbed, $simulator=false) {
        return $this->cmd_handler->start_ov($this->user_id, $scenario, $testbed, ($simulator == "true"));
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
        $experiment->experiment_token = $this->create_random(8);
        $experiment->scenario         = $request->scenario;
        $experiment->testbed          = $request->testbed;
        $experiment->firmware         = $request->has("firmware") ? $request->firmware : "default";
        $experiment->save();

        return SuccessResponse::response(200, Experiment::latest()->first());
    }

    function get_experiment($id) {
        return SuccessResponse::response(200, Experiment::where('experiment_token', $id)->first());
    }


    private function create_random($length) {
        $characters = 'abcdefghijklmnopqrstuvwxyz0123456789';
        $string = '';

        $max = strlen($characters) - 1;
        for ($i = 0; $i < $length; $i++) {
            $string .= $characters[mt_rand(0, $max)];
        }

        return $string;
    }

}