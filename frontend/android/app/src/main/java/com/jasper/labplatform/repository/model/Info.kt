package com.jasper.labplatform.repository.model

data class Info(val hint: String, val value: String)

data class InfoGroup(val title: String, val infos: List<Info>, val color: Int)
