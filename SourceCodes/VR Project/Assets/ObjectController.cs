
        using UnityEngine;
        using System.Collections;
        using System;
        using System.IO;
        using System.Net.Sockets;
        using System.Threading;



public class ObjectController : MonoBehaviour
    {
        public String host = "192.168.1.102";
        public Int32 port = 65432;

        internal Boolean socket_ready = false;
        internal String input_buffer = "";

        TcpClient tcp_socket;
        NetworkStream net_stream;

        StreamWriter socket_writer;
        StreamReader socket_reader;

        public string received_data;
        public GameObject Cam;
        //Vector3 pose = new Vector3(0.0f, 0.0f, 0.0f);
        public string C;

        private void Start()
        {
            setupSocket();
            //Console.WriteLine("Socket is set up");
            //
        }


    void Update()
    {
        Debug.Log("Hello");
        received_data = readSocket();
        C = Decode(received_data);
        Debug.Log(C);
        
        //Console.WriteLine("Data : " + received_data);
        //string[] data = received_data.Split(',');
        //Vector3 pose = new Vector3(Single.Parse(data[0]), Single.Parse(data[1]), Single.Parse(data[2]));
        //Cam.transform.position = pose;
        //writeSocket("Received");
        /*switch (received_data)
        {
            case "pong":
                Debug.Log("Python controller sent: " + (string)received_data);
                writeSocket("ping");
                break;
            default:
                Debug.Log("Nothing received");
                break;
        }*/
    }
    
        void OnApplicationQuit()
        {
            closeSocket();
        }

        // Helper methods for:
        //...setting up the communication
        public void setupSocket()
        {
            try
            {
                tcp_socket = new TcpClient(host, port);
                net_stream = tcp_socket.GetStream();
                socket_writer = new StreamWriter(net_stream);
                socket_reader = new StreamReader(net_stream);
                socket_ready = true;
            }
            catch (Exception e)
            {
                // Something went wrong
                Debug.Log("Socket error: " + e);
            }
        }

        //... writing to a socket...
        public void writeSocket(string line)
        {
            if (!socket_ready)
                return;

            
            socket_writer.Write(line);
            socket_writer.Flush();
        }

        //... reading from a socket...
        public String readSocket()
        {
            if (socket_ready)
                return "";

        if (net_stream.DataAvailable)
        {
            return socket_reader.ReadLine();
            
        }
            return "";
            
        }

        //... closing a socket...
        public void closeSocket()
        {
            if (!socket_ready)
                return;

            socket_writer.Close();
            socket_reader.Close();
            tcp_socket.Close();
            socket_ready = false;
        }
    public static String Decode(string Path)
    {
        String text;
        using (StreamReader sr = new StreamReader(Path))
        {
            text = sr.ReadToEnd();
            byte[] bytes = Convert.FromBase64String(text);
            System.Text.UTF8Encoding encoder = new System.Text.UTF8Encoding();
            System.Text.Decoder decoder = encoder.GetDecoder();
            int count = decoder.GetCharCount(bytes, 0, bytes.Length);
            char[] arr = new char[count];
            decoder.GetChars(bytes, 0, bytes.Length, arr, 0);
            text = new string(arr);

            return text;
        }
    }
}



       

