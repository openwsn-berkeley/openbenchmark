<?php
	
namespace App\Classes\ExperimentController;

class ConfigParser {

	private $scenario_config;

	private $roles = [
		"monitoring-sensor" => "Monitoring Sensor",
		"event-sensor"      => "Event Sensor",
		"actuator"          => "Actuator",
		"area-controller"   => "Area Controller",
		"zone-controller"   => "Zone Controller",
		"control-unit"      => "Control Unit",
		"sensor"            => "Sensor",
		"bursty-sensor"     => "Bursty Sensor",
		"gateway"           => "Gateway"
	];
	

	function get_config_data($param, $scenario, $testbed) {
		if ($param != 'nodes')
			return $this->_invoke_python_interface($param, $scenario, $testbed);

		return $this->_generate_nodes_data(
			$this->_invoke_python_interface($param, $scenario, $testbed)
		);
	}

	private function _invoke_python_interface($sc_identifier, $tb_identifier) {
		$python_interface_path = base_path() . "/../scenario-config/interface.py";
		$command = "python $python_interface_path --scenario=$sc_identifier --testbed=$tb_identifier";

		$command = "python $python_interface_path --param=$param";
		$command .= $param == 'nodes' ? " --scenario=$scenario --testbed=$testbed" : "";

		return json_decode(shell_exec($command), true);
	}

	private function _generate_nodes_data($res) {

		$data = [];
		$data["nodes"] = [];
		$data["links"] = [];

		foreach ($res as $generic_id => $node_data) {
			$data["nodes"][] = [
				"id"                => $generic_id,
				"name"              => $node_data["node_id"],
				"role"              => $node_data["role"],
				"roleFull"          => $this->roles[$node_data["role"]],
				"area"              => $node_data["area"],
				"_cssClass"         => "node " . $node_data["role"],
				"defaultCssClass"   => "node " . $node_data["role"],
				"transmissionPower" => $node_data["transmission_power_dbm"] . " dBm",
				"booted"    	    => false,
				"failed"            => false,
				"active"            => false
			];
			$data["links"] = $this->_append_node_links($data["links"], $generic_id, $node_data["destinations"]);
		}

		return $data;
	}

	private function _append_node_links($links, $source, $destinations) {
		foreach ($destinations as $destination) {
			$links[] = [
				"sid" => $source,
				"tid" => $destination
			];
		}
		return $links;
	}
	
}