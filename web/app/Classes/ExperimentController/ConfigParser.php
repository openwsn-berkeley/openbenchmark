<?php
	
namespace App\Classes\ExperimentController;

class ConfigParser {

	private $scenario_config;
	private $scenarios = [
		"building-automation"   => "Building automation", 
		"home-automation"       => "Home automation", 
		"industrial-monitoring" => "Industrial monitoring"];
	private $testbeds  = [
		"iotlab" => "IoT-LAB",
		"wilab"  => "w-iLab.t"
	];
	
	function get_config_data() {
		$res["scenarios"] = $this->scenarios;
		$res["testbeds"]  = $this->testbeds;

		foreach ($this->scenarios as $sc_identifier => $scenario) {
			$res["nodes"][$sc_identifier] = [];
			foreach ($this->testbeds as $tb_identifier => $testbed) {
				$res["nodes"][$sc_identifier][$tb_identifier] = json_decode($this->_invoke_python_interface(
					$sc_identifier,
					$tb_identifier
				));
			}
		}

		return $res;
	}

	private function _invoke_python_interface($sc_identifier, $tb_identifier) {
		$python_interface_path = base_path() . "/../scenario-config/interface.py";
		$command = "python $python_interface_path --scenario=$sc_identifier --testbed=$tb_identifier";

		return shell_exec($command);
	}
}