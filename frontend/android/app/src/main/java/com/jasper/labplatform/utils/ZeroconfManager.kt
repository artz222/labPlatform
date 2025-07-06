package com.jasper.labplatform.utils // Or your preferred package

import android.content.Context
import android.net.nsd.NsdManager
import android.net.nsd.NsdServiceInfo
import android.util.Log
import java.net.InetAddress
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.CopyOnWriteArrayList

/**
 * Manages Zeroconf (NSD) service discovery and resolution.
 */
class ZeroconfManager(context: Context) {

    private val nsdManager: NsdManager = context.getSystemService(Context.NSD_SERVICE) as NsdManager
    private var discoveryListener: NsdManager.DiscoveryListener? = null
    private var currentServiceType: String? = null
    private var isDiscovering = false

    // Thread-safe list for listeners
    private val serviceListeners = CopyOnWriteArrayList<ZeroconfServiceListener>()
    private val resolveListeners = ConcurrentHashMap<String, MutableList<ZeroconfResolveListener>>()


    companion object {
        private const val TAG = "ZeroconfManager"
    }

    /**
     * Listener for service discovery events (found, lost).
     */
    interface ZeroconfServiceListener {
        fun onServiceFound(serviceInfo: NsdServiceInfo)
        fun onServiceLost(serviceInfo: NsdServiceInfo)
        fun onDiscoveryStarted(serviceType: String)
        fun onDiscoveryStopped(serviceType: String)
        fun onDiscoveryFailed(serviceType: String, errorCode: Int, reason: String)
    }

    /**
     * Listener for service resolution events.
     */
    interface ZeroconfResolveListener {
        fun onServiceResolved(serviceInfo: NsdServiceInfo, ipAddress: String, port: Int)
        fun onResolveFailed(serviceInfo: NsdServiceInfo, errorCode: Int, reason: String)
    }

    fun addServiceListener(listener: ZeroconfServiceListener) {
        serviceListeners.addIfAbsent(listener)
    }

    fun removeServiceListener(listener: ZeroconfServiceListener) {
        serviceListeners.remove(listener)
    }

    /**
     * Adds a listener for a specific service name resolution.
     * Note: This listener will be removed after the service is resolved or fails to resolve once.
     */
    fun addResolveListener(serviceName: String, listener: ZeroconfResolveListener) {
        resolveListeners.computeIfAbsent(serviceName) { CopyOnWriteArrayList() }.add(listener)
    }

    /**
     * Removes a specific resolve listener for a service name.
     */
    fun removeResolveListener(serviceName: String, listener: ZeroconfResolveListener) {
        resolveListeners[serviceName]?.remove(listener)
        if (resolveListeners[serviceName]?.isEmpty() == true) {
            resolveListeners.remove(serviceName)
        }
    }


    private fun initializeDiscoveryListener() {
        discoveryListener = object : NsdManager.DiscoveryListener {
            override fun onDiscoveryStarted(regType: String) {
                isDiscovering = true
                Log.d(TAG, "Service discovery started: $regType")
                serviceListeners.forEach { it.onDiscoveryStarted(regType) }
            }

            override fun onServiceFound(service: NsdServiceInfo) {
                Log.d(
                    TAG,
                    "Service found: Name: ${service.serviceName}, Type: ${service.serviceType}"
                )
                // Check if it's the service type we are interested in.
                // The NsdManager should only return services of the type we requested,
                // but a check can be an extra safeguard.
                if (currentServiceType != null && service.serviceType.contains(
                        currentServiceType!!.removeSuffix(
                            "."
                        )
                    )
                ) {
                    serviceListeners.forEach { it.onServiceFound(service) }
                    // You might choose to auto-resolve here or let the client call resolveService explicitly.
                    // For this manager, we'll let the client call resolveService.
                } else {
                    Log.w(
                        TAG,
                        "Found service of unexpected type: ${service.serviceType} (expected: $currentServiceType)"
                    )
                }
            }

            override fun onServiceLost(service: NsdServiceInfo) {
                Log.i(TAG, "Service lost: ${service.serviceName}")
                serviceListeners.forEach { it.onServiceLost(service) }
                // Clean up any pending resolve listeners for this lost service
                resolveListeners.remove(service.serviceName)
            }

            override fun onDiscoveryStopped(serviceType: String) {
                isDiscovering = false
                Log.i(TAG, "Discovery stopped: $serviceType")
                serviceListeners.forEach { it.onDiscoveryStopped(serviceType) }
            }

            override fun onStartDiscoveryFailed(serviceType: String, errorCode: Int) {
                isDiscovering = false
                val reason = "Discovery start failed"
                Log.e(TAG, "$reason: Error code: $errorCode for type $serviceType")
                serviceListeners.forEach { it.onDiscoveryFailed(serviceType, errorCode, reason) }
                // Attempt to stop to clean up resources, though it might also fail.
                try {
                    nsdManager.stopServiceDiscovery(this)
                } catch (e: Exception) { /* Ignore */
                }
            }

            override fun onStopDiscoveryFailed(serviceType: String, errorCode: Int) {
                // isDiscovering state might be ambiguous here.
                val reason = "Discovery stop failed"
                Log.e(TAG, "$reason: Error code: $errorCode for type $serviceType")
                serviceListeners.forEach { it.onDiscoveryFailed(serviceType, errorCode, reason) }
            }
        }
    }

    fun startDiscovery(serviceType: String) {
        if (isDiscovering) {
            if (serviceType == currentServiceType) {
                Log.d(TAG, "Discovery already active for $serviceType")
                return
            } else {
                Log.d(
                    TAG,
                    "Stopping existing discovery for $currentServiceType to start for $serviceType"
                )
                stopDiscovery() // Stop previous discovery if type is different
            }
        }

        currentServiceType = serviceType
        if (discoveryListener == null) {
            initializeDiscoveryListener()
        }

        try {
            nsdManager.discoverServices(serviceType, NsdManager.PROTOCOL_DNS_SD, discoveryListener)
            Log.d(TAG, "Requested service discovery for type: $serviceType")
        } catch (e: IllegalArgumentException) {
            isDiscovering = false
            val reason = "IllegalArgumentException on starting discovery"
            Log.e(TAG, "$reason: ${e.message}", e)
            serviceListeners.forEach { it.onDiscoveryFailed(serviceType, -1, reason) }
        }
    }

    fun stopDiscovery() {
        if (isDiscovering && discoveryListener != null) {
            try {
                nsdManager.stopServiceDiscovery(discoveryListener)
                Log.d(TAG, "Requested stop service discovery for type: $currentServiceType")
                // onDiscoveryStopped will set isDiscovering to false
            } catch (e: IllegalArgumentException) {
                val reason = "IllegalArgumentException on stopping discovery"
                Log.e(TAG, "$reason: ${e.message}", e)
                // Manually call if stop failed, as onDiscoveryStopped might not be called
                isDiscovering =
                    false // Assume it stopped or failed to stop but we shouldn't consider it active
                currentServiceType?.let { type ->
                    serviceListeners.forEach { it.onDiscoveryFailed(type, -1, reason) }
                }
            }
        } else {
            Log.d(TAG, "Discovery not active or listener not initialized.")
            isDiscovering = false // Ensure consistency
        }
        // discoveryListener = null; // Consider if you want to nullify and re-initialize next time
        // currentServiceType = null;
    }

    fun resolveService(serviceInfo: NsdServiceInfo) {
        val serviceName = serviceInfo.serviceName
        if (resolveListeners[serviceName].isNullOrEmpty()) {
            Log.d(TAG, "No resolve listeners for service: $serviceName. Skipping resolve.")
            // return // Or resolve anyway if some default handling is desired
        }

        Log.d(TAG, "Attempting to resolve service: $serviceName")
        nsdManager.resolveService(serviceInfo, object : NsdManager.ResolveListener {
            override fun onResolveFailed(failedServiceInfo: NsdServiceInfo, errorCode: Int) {
                val reason = "Resolve failed"
                Log.e(TAG, "$reason for ${failedServiceInfo.serviceName}: Error code: $errorCode")
                val listeners =
                    resolveListeners[failedServiceInfo.serviceName]?.toList() // Create a copy for safe iteration
                listeners?.forEach { it.onResolveFailed(failedServiceInfo, errorCode, reason) }
                resolveListeners.remove(failedServiceInfo.serviceName) // Clean up listeners after failure
            }

            override fun onServiceResolved(resolvedServiceInfo: NsdServiceInfo) {
                Log.i(TAG, "Service resolved: Name: ${resolvedServiceInfo.serviceName}")
                val hostAddress: InetAddress? = resolvedServiceInfo.host
                val port: Int = resolvedServiceInfo.port

                if (hostAddress != null) {
                    val ipAddress = hostAddress.hostAddress
                    Log.i(
                        TAG,
                        "IP Address: $ipAddress, Port: $port for ${resolvedServiceInfo.serviceName}"
                    )

                    val listeners =
                        resolveListeners[resolvedServiceInfo.serviceName]?.toList() // Create a copy
                    listeners?.forEach {
                        it.onServiceResolved(
                            resolvedServiceInfo,
                            ipAddress,
                            port
                        )
                    }
                } else {
                    val reason = "Host address is null after resolution"
                    Log.w(TAG, "$reason for ${resolvedServiceInfo.serviceName}")
                    val listeners =
                        resolveListeners[resolvedServiceInfo.serviceName]?.toList() // Create a copy
                    listeners?.forEach { it.onResolveFailed(resolvedServiceInfo, -1, reason) }
                }
                // Clean up listeners for this service after successful resolution or if host is null
                resolveListeners.remove(resolvedServiceInfo.serviceName)
            }
        })
    }

    /**
     * Call this method to clean up resources, for example, in Activity's onDestroy.
     */
    fun cleanup() {
        stopDiscovery()
        serviceListeners.clear()
        resolveListeners.clear()
        discoveryListener = null // Allow it to be garbage collected
        Log.d(TAG, "ZeroconfManager cleaned up.")
    }

    fun isDiscovering(): Boolean = isDiscovering
}
