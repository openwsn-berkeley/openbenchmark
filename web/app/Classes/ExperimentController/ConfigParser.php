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
				"id"        => $generic_id,
				"name"      => $node_data["node_id"],
				"role"      => $node_data["role"],
				"area"      => $node_data["area"],
				"_cssClass" => "node " . $node_data["role"],
				"booted"    => false,
				"failed"    => false,
				"active"    => false
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