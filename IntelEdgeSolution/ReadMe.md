On host 
  please make sure you have VScode and can build and deploy python on Iot Edge devices as per instruction below
    https://docs.microsoft.com/en-us/azure/iot-edge/tutorial-python-module
  Please change env file to your contianer registry credentials build and deploy ...

On Edge Device :

  Please use this device as it comes with docker,Intel open Vinoand IotEdge installed...

  https://up-shop.org/home/285-up-squared-ai-vision-x-developer-kit.html#/116-up_squared_ai_vision_x_developer_kit-version_b_w_myriad_x


  On device

  1. “sudo gedit ~/.profile”  command to add “xhost +” command to “.profile” file, so now we don’t need to execute “xhost +” every time after restarting machine.This required to allow display to be used form docker .

  2. Modify Connection string taken from iot Edge device as per instruction here https://docs.microsoft.com/en-us/azure/iot-edge/quickstart-linux as this device already has iot edge and docker installed youjust modify a file with you connection STring 
    To edit the config.yaml, run this command in a Terminal on the Ubuntu machine.
      sudo nano /etc/iotedge/config.yaml
    This is the content of the config.yaml, replace the the <ADD..> with the connection string.

        provisioning:
        source: "manual"
        device_connection_string: "<ADD DEVICE CONNECTION STRING HERE>"
    At this point, you have an IoT Edge device connected to the IoT Hub Service.

  3.Set Usb rules by runing batch file at location 
    /opt/intel/computer_vision_sdk/install_dependencies/install_NCS_udev_rules.sh




