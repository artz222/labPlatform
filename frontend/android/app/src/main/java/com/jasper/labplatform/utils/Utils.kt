package com.jasper.labplatform.utils

import android.graphics.drawable.GradientDrawable
import android.net.Uri
import android.os.Handler
import android.os.Looper
import android.view.View
import android.widget.ImageView
import androidx.core.graphics.toColorInt
import com.bumptech.glide.Glide
import com.bumptech.glide.load.engine.DiskCacheStrategy

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

fun loadImage(url: String, imageView: ImageView) {
    // 关闭glide磁盘缓存，避免图片动态修改之后，客户端命中缓存出现异常
    Glide.with(imageView.context)
        .load(url)
        .diskCacheStrategy(DiskCacheStrategy.NONE)
        .into(imageView)
}

fun loadImage(uri: Uri, imageView: ImageView) {
    Glide.with(imageView.context)
        .load(uri)
        .into(imageView)
}
