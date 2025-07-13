package com.jasper.labplatform.repository

import android.os.Handler
import android.os.Looper
import android.util.Log
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import com.google.gson.Gson
import com.google.gson.annotations.SerializedName
import com.jasper.labplatform.repository.model.DecisionMessage
import com.jasper.labplatform.repository.model.ExperimentInfo
import com.jasper.labplatform.repository.model.SocketMessage
import com.jasper.labplatform.utils.getUUID
import com.jasper.labplatform.utils.runOnMainThread
import com.jasper.labplatform.utils.saveUUID
import com.jasper.labplatform.websocket.LabWebSocketClient
import org.java_websocket.handshake.ServerHandshake
import java.net.URI

object Repository {
    private val TAG = Repository::class.java.simpleName
    private val WEBSOCKET_TAG = "$TAG:websocket"
    var baseIP: String? = null
    private val websocketUrl by lazy { "ws://${baseIP}:8000/ws" }
    private val gson = Gson()

    private val _experimentInfo = MutableLiveData<ExperimentInfo>()
    val experimentInfo: LiveData<ExperimentInfo> get() = _experimentInfo

    private var uuid = getUUID() ?: ""

    private val labWebSocketClient by lazy {
        object : LabWebSocketClient(URI(websocketUrl)) {
            override fun onOpen(handshakedata: ServerHandshake?) {
                super.onOpen(handshakedata)
                send(gson.toJson(SocketMessage(cmd = CMD.CONNECT, data = uuid)))
            }

            override fun onMessage(message: String?) {
                super.onMessage(message)
                if (message.isNullOrEmpty()) return
                val socketMessage = try {
                    gson.fromJson(message, SocketMessage::class.java)
                } catch (
                    e: Exception
                ) {
                    Log.e(WEBSOCKET_TAG, "Error parsing message: ${e.message}")
                    return
                }
                runOnMainThread {
                    parseMessage(socketMessage)
                }
            }

            override fun onClose(code: Int, reason: String?, remote: Boolean) {
                super.onClose(code, reason, remote)
                Handler(Looper.getMainLooper()).postDelayed({
                    tryReconnectWebsocket()
                }, 2000)
            }

            override fun onError(ex: Exception?) {
                super.onError(ex)
            }
        }
    }

    private fun parseMessage(message: SocketMessage) {
        when (message.cmd) {
            CMD.UPDATE_EXPERIMENT_INFO -> {
                _experimentInfo.postValue(gson.fromJson(message.data, ExperimentInfo::class.java))
            }

            CMD.CONNECT -> {
                uuid = message.data ?: ""
                saveUUID(message.data ?: "")
            }

            CMD.SUBMIT_DESITION -> TODO()
        }
    }

    enum class CMD {
        @SerializedName("UPDATE_EXPERIMENT_INFO")
        UPDATE_EXPERIMENT_INFO,

        @SerializedName("CONNECT")
        CONNECT,

        @SerializedName("SUBMIT_DESITION")
        SUBMIT_DESITION
    }

    fun tryConnectWebsocket() {
        Log.d(WEBSOCKET_TAG, "Trying to connect to: $websocketUrl")
        try {
            labWebSocketClient.connect()
        } catch (e: Exception) {
            Log.e(WEBSOCKET_TAG, "Error connecting to WebSocket server: ${e.message}")
        }
    }

    private fun tryReconnectWebsocket() {
        Log.d(WEBSOCKET_TAG, "Trying to reconnect to: $websocketUrl")
        try {
            labWebSocketClient.reconnect()
        } catch (e: Exception) {
            Log.e(WEBSOCKET_TAG, "Error reconnecting to WebSocket server: ${e.message}")
        }
    }

    fun sendMessage(message: SocketMessage) {
        labWebSocketClient.send(gson.toJson(message))
    }

    fun submitDecision(decision: String) {
        sendMessage(
            SocketMessage(
                cmd = CMD.SUBMIT_DESITION,
                data = gson.toJson(DecisionMessage(uuid = uuid, decision = decision))
            )
        )
    }

}