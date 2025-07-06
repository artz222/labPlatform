package com.jasper.labplatform.websocket

import android.util.Log
import org.java_websocket.client.WebSocketClient
import org.java_websocket.handshake.ServerHandshake
import java.net.URI

open class LabWebSocketClient(uri: URI) : WebSocketClient(uri) {
    override fun onOpen(handshakedata: ServerHandshake?) {
        Log.d("WebSocket", "Connection opened")
    }

    override fun onMessage(message: String?) {
        Log.d("WebSocket", "Received message: $message")
    }

    override fun onClose(code: Int, reason: String?, remote: Boolean) {
        Log.d("WebSocket", "Connection closed")
    }

    override fun onError(ex: Exception?) {
        Log.e("WebSocket", "Error: ${ex?.message}")
    }
}