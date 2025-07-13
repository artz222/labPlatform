package com.jasper.labplatform.repository.model

import com.jasper.labplatform.repository.Repository

data class SocketMessage(val cmd: Repository.CMD, val data: String? = null)


data class DecisionMessage(val uuid: String, val decision: String)