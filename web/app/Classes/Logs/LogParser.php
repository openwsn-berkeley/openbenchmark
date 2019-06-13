<?php

namespace App\Classes\Logs;

use SuccessResponse;
use ErrorResponse;


class LogParser {

	function get_log_data($action, $experiment_id) {
		$invalid_params = $this->_validate_params($action, $experiment_id);

		if (count($invalid_params) == 0)
        	return SuccessResponse::response(200, $this->_invoke_python_interface($action, $experiment_id));

        return ErrorResponse::response(400, $invalid_params);
	} 

	private function _invoke_python_interface($action, $experiment_id) {
		$python_interface_path = "/home/vagrant/openbenchmark/experiment-orchestrator/kpi/kpis/log_parser.py";

		$command = "python $python_interface_path --action=$action";
		$command .= $action == 'data-fetch' ? " --experiment-id=$experiment_id" : "";
		
		return json_decode(shell_exec($command), true);
	}

	private function _validate_params($action, $experiment_id) {
		$invalid_params = [];

		if (!in_array($action, ["log-list", "data-fetch"]))
			$invalid_params[] = [
				"param"   => "action",
				"message" => "--action param must be 'log-list' or 'data-fetch'"
			];

		if ($action == "data-fetch" && strlen($experiment_id) < 5)
			$invalid_params[] = [
				"param"  => "experiment_id",
				"message" => "Invalid value of --experiment-id"
			];

		return $invalid_params;
	}

}