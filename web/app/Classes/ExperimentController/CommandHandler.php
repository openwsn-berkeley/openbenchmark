<?php

namespace App\Classes\ExperimentController;


class CommandHandler {

    const PROVISIONER_MAIN = 'python /home/vagrant/openbenchmark/experiment-provisioner/main.py';
    const OV_GUARD_TIME    = 20; //A guard time in seconds for the nodes to start sending serial data before running OV


    function reserve_nodes($user_id, $scenario, $testbed) {
        //2>&1 added to insure that all output is given as a return of shell_exec function
        $cmd = self::PROVISIONER_MAIN . " --user-id=$user_id --action=reserve --scenario=$scenario --testbed=$testbed &>>reserve.txt";
        return shell_exec($cmd);
    }

    function flash_firmware($user_id, $firmware) {
        $cmd = self::PROVISIONER_MAIN . " --user-id=$user_id --action=otbox-flash";
        
        if ($firmware != null)
            $cmd .= " --firmware=$firmware";

        $cmd .= " &>>flash.txt";

        return shell_exec($cmd);
    }

    function start_ov($user_id, $scenario, $testbed, $simulator) {
        $cmd = self::PROVISIONER_MAIN . " --user-id=$user_id --action=ov-start --scenario=$scenario --testbed=$testbed";

        if ($simulator != null)
             $cmd .= " --simulator";

         $cmd .= " &>>start_ov.txt";

        return shell_exec($cmd);
    }

    function exp_terminate($user_id) {
        $cmd = self::PROVISIONER_MAIN . " --user-id=$user_id --action=terminate &>>exp_terminate.txt";
        return shell_exec($cmd);
    }

}