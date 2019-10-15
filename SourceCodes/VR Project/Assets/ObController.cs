using System;
using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class ObController : MonoBehaviour
{
    #region private members 	
    	
    /// TCPListener to listen for incomming TCP connection requests. 	
    	
    private TcpListener tcpListener;
    /// Background thread for TcpServer workload. 	
    private Thread tcpListenerThread;
    /// Create handle to connected tcp client. 	
    private TcpClient connectedTcpClient;
    #endregion
    public string clientMessage;
    public GameObject Cam;
    private float time = 0.0f;
    public float interpolationPeriod = 0.01f;
    
    // Use this for initialization
    void Start()
    {
        // Start TcpServer background thread 		
        tcpListenerThread = new Thread(new ThreadStart(ListenForIncommingRequests));
        tcpListenerThread.IsBackground = true;
        tcpListenerThread.Start();
    }

    // Update is called once per frame
    void Update()
    {
        time += Time.deltaTime;

        if (time >= interpolationPeriod)
        {
            time = time - interpolationPeriod;
        }
        string[] data = clientMessage.Split(',');
        Vector3 pose = new Vector3(Single.Parse(data[0]), Single.Parse(data[1]), Single.Parse(data[2]));
        Cam.transform.position = pose;
        Cam.transform.rotation = Quaternion.Euler(0.0f, 45.0f, 0.0f);
        
    }

    /// <summary> 	
    /// Runs in background TcpServerThread; Handles incomming TcpClient requests 	
    /// </summary> 	
    private void ListenForIncommingRequests()
    {
        try
        {
            // Create listener on localhost port 8052. 			
            tcpListener = new TcpListener(IPAddress.Parse("192.168.1.109" + ""), 52595);
            tcpListener.Start();
            Debug.Log("Server is listening");
            Byte[] bytes = new Byte[1024];
            while (true)
            {
                using (connectedTcpClient = tcpListener.AcceptTcpClient())
                {
                    // Get a stream object for reading 					
                    using (NetworkStream stream = connectedTcpClient.GetStream())
                    {
                        int length;
                        // Read incomming stream into byte arrary. 						
                        while ((length = stream.Read(bytes, 0, bytes.Length)) != 0)
                        {
                            var incommingData = new byte[length];
                            Array.Copy(bytes, 0, incommingData, 0, length);
                            // Convert byte array to string message. 							
                            clientMessage = Encoding.ASCII.GetString(incommingData);
                            Debug.Log("client message received as: " + clientMessage);
                        }
                    }
                }
            }
        }
        catch (SocketException socketException)
        {
            Debug.Log("SocketException " + socketException.ToString());
        }
    }
    /// <summary> 	
    /// Send message to client using socket connection. 	
    /// </summary> 	
    private void SendMessage()
    {
        if (connectedTcpClient == null)
        {
            return;
        }

        try
        {
            // Get a stream object for writing. 			
            NetworkStream stream = connectedTcpClient.GetStream();
            if (stream.CanWrite)
            {
                string serverMessage = "This is a message from your server.";
                // Convert string message to byte array.                 
                byte[] serverMessageAsByteArray = Encoding.ASCII.GetBytes(serverMessage);
                // Write byte array to socketConnection stream.               
                stream.Write(serverMessageAsByteArray, 0, serverMessageAsByteArray.Length);
                Debug.Log("Server sent his message - should be received by client");
            }
        }
        catch (SocketException socketException)
        {
            Debug.Log("Socket exception: " + socketException);
        }
    }
}