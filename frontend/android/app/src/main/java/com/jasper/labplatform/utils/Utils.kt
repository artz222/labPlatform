package com.jasper.labplatform.utils

import android.graphics.drawable.GradientDrawable
import android.os.Handler
import android.os.Looper
import android.view.View
import androidx.core.graphics.toColorInt

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

fun setRoundedBackground(view: View, backgroundColor: Int, cornerRadiusDp: Float) {
    val gradientDrawable = GradientDrawable()
    gradientDrawable.shape = GradientDrawable.RECTANGLE
    gradientDrawable.setColor(backgroundColor)

    // Convert Dp to Px for corner radius
    val cornerRadiusPx = cornerRadiusDp * view.context.resources.displayMetrics.density
    gradientDrawable.cornerRadius = cornerRadiusPx

    view.background = gradientDrawable
}

val groupColors = listOf(
    "#FFFFF7D3",
    "#FFE8FAE5",
    "#FFDCF0F2",
)

fun getGroupColor(index: Int): Int {
    return groupColors[index].toColorInt()
}
