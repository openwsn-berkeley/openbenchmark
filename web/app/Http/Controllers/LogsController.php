<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Classes\Logs\LogParser;


class LogsController extends Controller
{

    function __construct() {
    	$this->log_parser = new LogParser;
    }

    function get($action, $experiment_id = "") {
    	return $this->log_parser->get_log_data($action, $experiment_id);
    }

    function download($experiment_id, $log_type) {
    	return $this->log_parser->download($experiment_id, $log_type);
    }

}