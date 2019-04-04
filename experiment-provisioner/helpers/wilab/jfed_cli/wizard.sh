PATH_TO_FX='/usr/lib/jvm/javafx-sdk-11.0.2/lib'
export DISPLAY=":99"
/usr/lib/jvm/jdk-11.0.2/bin/java --module-path $PATH_TO_FX --add-modules=javafx.controls,javafx.swing -jar experimenter-cli2.jar --wizard