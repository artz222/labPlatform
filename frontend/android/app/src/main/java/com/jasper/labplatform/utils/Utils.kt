package com.jasper.labplatform.utils

import android.os.Handler
import android.os.Looper

fun runOnMainThread(block: () -> Unit) {
    if (Looper.myLooper() == Looper.getMainLooper()) {
        // Already on the main thread, execute directly
        block()
    } else {
        // Not on the main thread, post to the main thread's handler
        Handler(Looper.getMainLooper()).post {
            block()
        }
    }
}