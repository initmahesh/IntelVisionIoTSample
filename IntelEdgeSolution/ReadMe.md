“sudo gedit ~/.profile” command to add “xhost +” command to “~/.profile” file, so now we don’t need to execute “xhost +” every time after restarting machine.





Pull onnxruntime with OpenVINO_EP-CPU_FP32 container images to local machine:
$ sudo docker login shtmpacr.azurecr.io -u shtmpacr -p BeQ5JGagCs/nTBpG4NYG0QKOboItQb+0
$ sudo docker pull shtmpacr.azurecr.io/openvinoep/onnxruntime-cpu
$ sudo docker pull shtmpacr.azurecr.io/openvinoep/onnx-iot-cpu

(Yu-Kwen: For security concern, please let me know when Advantech finish to download the above container images, and I will delete the above private acr shtmpacr. )

Modified Docker files used to build onnxruntime with OpenVINO_EP: 
https://shtmpstorage.blob.core.windows.net/test/OpenVino/EP/Advantech/OnnxRuntime.zip

Test result: https://shtmpstorage.blob.core.windows.net/test/OpenVino/EP/Advantech/TestResult.MOV


Setup build machine:
 
1. Install Ubuntu 16.04.6 LTS.
 
2. Install docker:
$ sudo apt install docker.io

3. Download and unzip OnnxRuntime.zip from https://shtmpstorage.blob.core.windows.net/test/OpenVino/EP/Advantech/OnnxRuntime.zip.
 
4. Change directory to the extracted OnnxRuntime directory, and download and save l_openvino_toolkit_p_2018.5.455.tgz to OnnxRuntime directory.
 
5. Build  Azure IoT Edge with ONNX Runtime-OpenvinoEP-CPU_FP32 “onnx-iot-cpu” by the following commands:
$ sudo docker build -t onnxruntime-cpu --build-arg DEVICE=CPU_FP32 --network host .
$ sudo docker build -t onnx-iot-cpu -f Dockerfile.iot --network host .
 
6. Push the built “onnx-iot-cpu” to Azure Container Registry:
$ sudo docker login <your_acr_name>.azurecr.io -u <your_username> -p <your_password>
$ sudo docker tag onnx-iot-cpu <your_acr_name>.azurecr.io/openvinoep/onnx-iot-cpu
$ sudo docker push <your_acr_name>.azurecr.io/openvinoep/onnx-iot-cpu
 
7. Use “Set modules” button to add “onnx-iot-cpu” module to your Azure IoT Edge device and change Container Create Options to the following settings as mentioned in https://software.intel.com/en-us/get-started-with-the-openvino-toolkit-and-microsoft-azure-iot-edge#inpage-nav-5:


{
  "HostConfig": {
    "Binds": [
      "/tmp/.X11-unix:/tmp/.X11-unix",
      "/dev/video0:/dev/video0"
    ],
    "Devices": [
      {
        "PathOnHost": "/dev/video0",
        "PathInContainer": "/dev/video0",
        "CgroupPermissions": "mrw"
      }
    ],
    "Privileged": true
  },
  "Env": [
    "DISPLAY=:0"
  ]
} 
 
Setup test machine:
 
1. Install Ubuntu 16.04.6 LTS
 
2. Install docker:
$ sudo apt install docker.io
 
3. Install Azure IoT Edge Runtime by following the instructions in https://docs.microsoft.com/en-us/azure/iot-edge/how-to-install-iot-edge-linux.
Note: if fail to download or connect IoT Edge runtime, please uncomment or remove “dns=dnsmasq” in /etc/NetworkManager if it exists.
 
4. Use “sudo gedit ~/.profile” command to add “xhost +” command to “~/.profile” file, save  “~/.profile” file, and restart test machine.
 
5. Now it will start to download onnx-iot-cpu module to your test machine and start tiny_yolov2_demo.py as shown in https://shtmpstorage.blob.core.windows.net/test/OpenVino/EP/Advantech/TestResult.MOV.


Validate webcam by local docker on test machine:
 
$ xhost +
$ sudo docker run -it --privileged --device /dev/video0:/dev/video0 -v /home/test/app:/app -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix shtmpacr.azurecr.io/openvinoep/onnxruntime-cpu











docker run \
--rm \
-it \
-e DISPLAY=$DISPLAY \
--ipc host \
-v /tmp/.X11-unix:/tmp/.X11-unix \
--network host \
--mount type=bind,source=/home/mahesh/my,destination=/opt/data/ \
--privileged \
-v /dev:/dev \
--entrypoint bash \
mycapreg.azurecr.io/onnxruntimedevice


verification :;
	root@mahesh-UP-APL01:/opt/data/Intel worker safety demo# pip3 list
decorator (4.4.0)
networkx (2.3)
numpy (1.16.4)
onnx (1.5.0)
onnxruntime-openvino (0.4.0)
opencv-python (4.1.0.25)
pip (8.1.1)
protobuf (3.8.0)
setuptools (20.7.0)
six (1.12.0)
typing (3.6.6)
typing-extensions (3.7.2)
wheel (0.29.0)
You are using pip version 8.1.1, however version 19.1.1 is available.
You should consider upgrading via the 'pip install --upgrade pip' command.
root@mahesh-UP-APL01:/opt/data/Intel worker safety demo# ls /dev
autofs           drm_dp_aux0  hidraw2    i2c-6         loop1   memory_bandwidth    null      snd     tty15  tty26  tty37  tty48  tty59   ttyS11  ttyS22  ttyS7      vcs3   vga_arbiter
block            ecryptfs     hpet       i2c-7         loop2   mmcblk0             port      stderr  tty16  tty27  tty38  tty49  tty6    ttyS12  ttyS23  ttyS8      vcs4   vhci
btrfs-control    fb0          hugepages  i2c-8         loop3   mmcblk0boot0        ppp       stdin   tty17  tty28  tty39  tty5   tty60   ttyS13  ttyS24  ttyS9      vcs5   vhost-net
bus              fd           hwrng      i2c-9         loop4   mmcblk0boot1        psaux     stdout  tty18  tty29  tty4   tty50  tty61   ttyS14  ttyS25  ttyprintk  vcs6   vhost-vsock
char             full         i2c-0      initctl       loop5   mmcblk0p1           ptmx      tty     tty19  tty3   tty40  tty51  tty62   ttyS15  ttyS26  uhid       vcsa   video0
console          fuse         i2c-1      input         loop6   mmcblk0p2           pts       tty0    tty2   tty30  tty41  tty52  tty63   ttyS16  ttyS27  uinput     vcsa1  zero
core             gpiochip0    i2c-10     kmsg          loop7   mmcblk0p3           random    tty1    tty20  tty31  tty42  tty53  tty7    ttyS17  ttyS28  urandom    vcsa2
cpu              gpiochip1    i2c-11     kvm           mapper  mmcblk0rpmb         rfkill    tty10   tty21  tty32  tty43  tty54  tty8    ttyS18  ttyS29  userio     vcsa3
cpu_dma_latency  gpiochip2    i2c-2      lightnvm      mcelog  mqueue              rtc       tty11   tty22  tty33  tty44  tty55  tty9    ttyS19  ttyS3   v4l        vcsa4
cuse             gpiochip3    i2c-3      log           media0  net                 rtc0      tty12   tty23  tty34  tty45  tty56  ttyS0   ttyS2   ttyS30  vcs        vcsa5
disk             hidraw0      i2c-4      loop-control  mei0    network_latency     shm       tty13   tty24  tty35  tty46  tty57  ttyS1   ttyS20  ttyS31  vcs1       vcsa6
dri              hidraw1      i2c-5      loop0         mem     network_throughput  snapshot  tty14   tty25  tty36  tty47  tty58  ttyS10  ttyS21  ttyS6   vcs2       vfio


pip3 install Pillow 

On host 
xhost +

On host copy the usb sewtting as per below 