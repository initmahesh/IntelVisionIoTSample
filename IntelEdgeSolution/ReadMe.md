## On host 

  please make sure you have VScode and can build and deploy python on Iot Edge devices as per instruction below
    https://docs.microsoft.com/en-us/azure/iot-edge/tutorial-python-module
  Please change env file to your contianer registry credentials build and deploy ...
  
  Update the .env file with the values for your container registry. Refer to Create a container registry for more detail about ACR  settings.
  
        REGISTRY_NAME=<YourAcrUri>
        REGISTRY_USER_NAME=<YourAcrUserName>
        REGISTRY_PASSWORD=<YourAcrPassword>
    Sign in to your Azure Container Registry by entering the following command in the Visual Studio Code integrated terminal (replace <REGISTRY_USER_NAME>, <REGISTRY_PASSWORD>, and <REGISTRY_NAME> to your container registry values set in the .env file).
    docker login -u <REGISTRY_USER_NAME> -p <REGISTRY_PASSWORD> <REGISTRY_NAME>.azurecr.io

## On Edge Device :

  Please use this device as it comes with docker,Intel open Vino and IotEdge installed...

FOR X64 Intel edge ::  https://up-shop.org/home/285-up-squared-ai-vision-x-developer-kit.html#/116-up_squared_ai_vision_x_developer_kit-version_b_w_myriad_x


  ####On edge device

  1. “sudo gedit ~/.profile”  command to add “xhost +” command to “.profile” file, so now we don’t need to execute “xhost +” every time after restarting machine.This required to allow display to be used form docker .

  2. Install all dependencies (IoTedge, Moby/Docker)and Modify Connection string taken from iot Edge device as per instruction here https://docs.microsoft.com/en-us/azure/iot-edge/quickstart-linux.

    NOTE :: If this device already has iot edge and docker installed you just modify a file with you connection STring 
    To edit the config.yaml, run this command in a Terminal on the Ubuntu machine.
      sudo nano /etc/iotedge/config.yaml
    This is the content of the config.yaml, replace the the <ADD..> with the connection string.
    
   Also change the hostname to "<hostname>" as below 
   
    provisioning:
        source: "manual"
        device_connection_string: "<ADD DEVICE CONNECTION STRING HERE>"
          At this point, you have an IoT Edge device connected to the IoT Hub Service.
          
    ..
    ...
    ..
    
    ###############################################################################
    # Edge device hostname
    ###############################################################################
    #
    # Configures the environment variable 'IOTEDGE_GATEWAYHOSTNAME' injected into
    # modules. Regardless of case the hostname is specified below, a lower case
    # value is used to configure the Edge Hub server hostname as well as the
    # environment variable specified above.
    #
    # It is important to note that when connecting downstream devices to the
    # Edge Hub that the lower case value of this hostname be used in the
    # 'GatewayHostName' field of the device's connection string URI.
    ###############################################################################

    #hostname: "ivk-desktop"
    hostname: "<command:hostname output from device>"
Optional for Intel if NCS2 does not work from docker ::

  3.Set Usb rules by runing batch file at location 
    /opt/intel/computer_vision_sdk/install_dependencies/install_NCS_udev_rules.sh


### How to build for different edge boards 
#### For Intel 
  - Rename deployment.template.amd64.json as deployment.template.json right click and build and deploy as learned with above python sample to deploy temperature sensor module 
#### For Jetson Nano 
  - Rename deployment.template.arm64.json as deployment.template.json right click and build and deploy as learned with above python sample to deploy temperature sensor module 

#### For Raspi Nano 
  - Rename deployment.template.arm32.json as deployment.template.json right click and build and deploy as learned with above python sample to deploy temperature sensor module 



