package com.jasper.labplatform.utils

import com.tencent.mmkv.MMKV

private const val UUID_TAG = "uuid"

fun getUUID(): String? {
    return MMKV.defaultMMKV().decodeString(UUID_TAG, "")
}

fun saveUUID(uuid: String) {
    MMKV.defaultMMKV().encode(UUID_TAG, uuid)
}
