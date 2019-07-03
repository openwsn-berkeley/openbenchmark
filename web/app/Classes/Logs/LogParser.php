<?php

namespace App\Classes\Logs;

use SuccessResponse;
use ErrorResponse;
use Response;


class LogParser {

	const ERRORS = [
		"no-file" => "File does not exists"
	];

	function get_log_data($action, $experiment_id) {
		$invalid_params = $this->_validate_params($action, $experiment_id);

		if (count($invalid_params) == 0)
        	return SuccessResponse::response(200, $this->_invoke_python_interface($action, $experiment_id));

        return ErrorResponse::response(400, $invalid_params);
	} 

	function download($experiment_id, $log_type) {
		try {
			$prefix = [
				"raw"      => "raw/raw_",
				"kpi"      => "kpis/kpi_",
				"kpi-json" => "kpis/.cache/cached_kpi_"
			];

			$suffix = [
				"raw"      => ".log",
				"kpi"      => ".log",
				"kpi-json" => ".json"	
			];

			if (array_key_exists($log_type, $prefix))
				$name_prefix = $prefix[$log_type];
			else
				throw new \Exception(self::ERRORS["no-file"]);

			if (array_key_exists($log_type, $suffix))
				$name_suffix = $suffix[$log_type];
			else
				throw new \Exception(self::ERRORS["no-file"]);

			$name = "$name_prefix$experiment_id$name_suffix";

			$file_path = "/home/vagrant/openbenchmark/experiment_orchestrator/kpi/$name";

			$file_path_err = $this->_validate_file_path($file_path);
			if ($file_path_err != "")
				throw new \Exception($file_path_err);

			return Response::download($file_path);

		} catch (\Exception $e) {
			return ErrorResponse::response(400, $e->getMessage());
		}
	}

	private function _invoke_python_interface($action, $experiment_id) {
		$python_interface_path = "/home/vagrant/openbenchmark/experiment_orchestrator/kpi/kpis/log_parser.py";

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

	private function _validate_file_path($file_path) {
		if (file_exists($file_path))
			return "";
		return self::ERRORS["no-file"];
	}

}