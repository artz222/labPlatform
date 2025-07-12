package com.jasper.labplatform

import android.app.Application
import com.tencent.mmkv.MMKV


class MainApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        val rootDir = MMKV.initialize(this)
        println("mmkv root: $rootDir")
    }
}