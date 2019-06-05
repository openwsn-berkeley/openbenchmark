PATH_TO_FX='/usr/lib/jvm/javafx-sdk-12.0.1/lib'
export DISPLAY=":99"
/usr/lib/jvm/jdk-12.0.1/bin/java --module-path $PATH_TO_FX --add-modules=javafx.controls,javafx.swing -jar experimenter-cli2.jar --action start_experiment.yml