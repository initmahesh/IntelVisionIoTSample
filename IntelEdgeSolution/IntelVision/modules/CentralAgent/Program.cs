namespace CentralAgent
{
    using System;
    using System.IO;
    using System.Runtime.InteropServices;
    using System.Runtime.Loader;
    using System.Security.Cryptography.X509Certificates;
    using System.Text;
    using System.Threading;
    using System.Threading.Tasks;
    using Microsoft.Azure.Devices.Client;
    using Microsoft.Azure.Devices.Client.Transport.Mqtt;
    using Microsoft.Azure.Devices.Shared;
    using Newtonsoft.Json;

    class Program
    {
        static string _deviceConnectionString = "";
        static DeviceClient _deviceClient = null;
        static CancellationTokenSource _cts;

        static void Main(string[] args)
        {
             _deviceConnectionString = Environment.GetEnvironmentVariable("EdgeConnectionString");
            if (string.IsNullOrEmpty(_deviceConnectionString))
            {
               Console.WriteLine($"Error: Missing environmental variable \"EdgeConnectionString\"... Please provide environmental variable \"EdgeConnectionString\" in deployment manifest.");
            }
            else
            {
                Init().Wait();

                // Wait until the app unloads or is cancelled
                _cts = new CancellationTokenSource();
                AssemblyLoadContext.Default.Unloading += (ctx) => _cts.Cancel();
                Console.CancelKeyPress += (sender, cpe) => _cts.Cancel();
                WhenCancelled(_cts.Token).Wait();
            }
        }

        /// <summary>
        /// Handles cleanup operations when app is cancelled or unloads
        /// </summary>
        public static Task WhenCancelled(CancellationToken cancellationToken)
        {
            var tcs = new TaskCompletionSource<bool>();
            cancellationToken.Register(s => ((TaskCompletionSource<bool>)s).SetResult(true), tcs);
            return tcs.Task;
        }

        /// <summary>
        /// Initializes the ModuleClient and sets up the callback to receive
        /// messages containing temperature information
        /// </summary>
        static async Task Init()
        {
            _deviceClient = DeviceClient.CreateFromConnectionString(_deviceConnectionString, TransportType.Mqtt);

            MqttTransportSettings mqttSetting = new MqttTransportSettings(TransportType.Mqtt_Tcp_Only);
            ITransportSettings[] settings = { mqttSetting };

            // Open a connection to the Edge runtime
            ModuleClient ioTHubModuleClient = await ModuleClient.CreateFromEnvironmentAsync(settings);
            await ioTHubModuleClient.OpenAsync();
            Console.WriteLine("IoT Hub module client initialized.");

            // Register callback to be called when a message is received by the module
            await ioTHubModuleClient.SetInputMessageHandlerAsync("input", OnMessageReceived, ioTHubModuleClient);
        }

        /// <summary>
        /// This method is called whenever the module is sent a message from the EdgeHub. 
        /// It just pipe the messages without any change.
        /// It prints all the incoming messages.
        /// </summary>
        static async Task<MessageResponse> OnMessageReceived(Message message, object userContext)
        {
            byte[] messageBytes = message.GetBytes();
            string messageString = Encoding.UTF8.GetString(messageBytes);
            Console.WriteLine($"Received message: [{messageString}]");
            //ex: {"height": 216.0, "position_x": 419.904, "position_y": 668.952, "width": 344.832, "confidence": 71, "id": 25, "label": "keyboard"}

            if (!string.IsNullOrEmpty(messageString))
            {
                //Parse input json string (See TelemetryData for telemetry definition)
                var data = JsonConvert.DeserializeObject<TelemetryData>(messageString);
                await SendTelemetryAsync(data, _cts.Token);
            }
            return MessageResponse.Completed;
        }

        private static async Task SendTelemetryAsync(TelemetryData telemetry, CancellationToken token)
        {
            try
            {
                if(_deviceClient != null)
                {
                    var messageString = JsonConvert.SerializeObject(telemetry);
                    var message = new Message(Encoding.ASCII.GetBytes(messageString));

                    token.ThrowIfCancellationRequested();
                    await _deviceClient.SendEventAsync(message);

                    Console.WriteLine("{0} > Sending telemetry: {1}", DateTime.Now, messageString);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine();
                Console.WriteLine("Intentional shutdown: {0}", ex.Message);
            }
        }
    }

    // Telemetry definition
    public class TelemetryData
    {


        [JsonProperty("headCount")]
        public int headCount { get; set; }

        [JsonProperty("headCountAccuracy")]
        public float headCountAccuracy{ get; set; }

        [JsonProperty("bunnySuitCount")]
        public int bunnySuitCount { get; set; }

        [JsonProperty("bunnySuitCountAccuracy")]
        public float bunnySuitCountAccuracy{ get; set; }

        [JsonProperty("glassesCount")]
        public int glassesCount { get; set; }

        [JsonProperty("glassesCountAccuracy")]
        public float glassesCountAccuracy{ get; set; }
        
    }
}
