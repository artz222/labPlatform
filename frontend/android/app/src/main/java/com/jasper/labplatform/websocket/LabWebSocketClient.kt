package com.jasper.labplatform.websocket

import android.util.Log
import org.java_websocket.client.WebSocketClient
import org.java_websocket.handshake.ServerHandshake
import java.net.URI

open class LabWebSocketClient(uri: URI) : WebSocketClient(uri) {
    companion object {
        private const val TAG = "LabWebSocketClient"
    }

    override fun onOpen(handshakedata: ServerHandshake?) {
        Log.d(TAG, "Connection opened")
    }

    override fun onMessage(message: String?) {
        Log.d(TAG, "Received message: $message")
    }

    override fun onClose(code: Int, reason: String?, remote: Boolean) {
        Log.d(TAG, "Connection closed")
    }

    override fun onError(ex: Exception?) {
        Log.e(TAG, "Error: ${ex?.message}")
    }

    override fun send(text: String?) {
        super.send(text)
        Log.d(TAG, "Sent message: $text")
    }
}