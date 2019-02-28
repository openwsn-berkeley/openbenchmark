<?php

namespace App\Classes\ExperimentController;

class CommandHandler {

    const COMMAND_MAIN = '/home/vagrant/iotlab-exp-auto/main.py';
    const OV_GUARD_TIME = 20; //A guard time in seconds for the nodes to start sending serial data before running OV
    const OV_LOG_GUARD_TIME = 5; //A guard time in seconds for the nodes to start sending serial data before running OV

    private $reserve_nodes_cmd = "python " . self::COMMAND_MAIN . " -reserve 2>&1"; //2>&1 added to insure that all output is given as a return of shell_exec function
    private $otbox_start_cmd = "python " . self::COMMAND_MAIN . " -otbox 2>&1";
    private $ov_start_cmd = "python " . self::COMMAND_MAIN . " -ov-start 2>&1";
    private $ov_monitor_cmd = "python " . self::COMMAND_MAIN . " -ov-monitor > /dev/null 2>/dev/null &";
    private $exp_terminate = "python " . self::COMMAND_MAIN . " -terminate 2>&1";

    function reserve_nodes() {
        return shell_exec($this->reserve_nodes_cmd);
    }

    function otbox_start() {
        return shell_exec($this->otbox_start_cmd);
    }

    function ov_start() {
        return shell_exec($this->ov_start_cmd);
    }

    function ov_monitor() {
        return shell_exec($this->ov_monitor_cmd);
    }

    function exp_terminate() {
        return shell_exec($this->exp_terminate);
    }

}
