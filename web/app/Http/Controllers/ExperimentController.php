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
        $this->cmd_handler->reserve($this->user_id, $scenario, $testbed, false);
        $this->cmd_handler->flash($this->user_id, $firmware, false);
        $this->cmd_handler->sut_start($this->user_id, $scenario, $testbed, ($simulator == "true"), true);
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
    function reserve($scenario, $testbed) {
        return $this->cmd_handler->reserve($this->user_id, $scenario, $testbed);
    }

    function flash($firmware=null, $branch=null) {
        return $this->cmd_handler->flash($this->user_id, $firmware, $branch);
    }

    function sut_start($scenario, $testbed, $simulator=false) {
        return $this->cmd_handler->sut_start($this->user_id, $scenario, $testbed, ($simulator == "true"));
    }

    function terminate() {
        return $this->cmd_handler->terminate($this->user_id);
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