<?php
	
namespace App\Classes\ExperimentController;

class ScenarioParser {

	private $scenario_config;
	private $scenarios = ["building-automation", "home-automation", "industrial-monitoring"];

	function __construct() {
        $this->scenario_config = base_path() . "/../experiment-orchestrator/scenarios";
        $this->command_handler = new CommandHandler();
    }
	
	function get_scenarios_json() {
		return "pass";
	}
}