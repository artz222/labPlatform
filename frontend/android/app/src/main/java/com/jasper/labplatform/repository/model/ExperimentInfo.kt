package com.jasper.labplatform.repository.model

data class ExperimentInfo(
    val infos: List<Info>,
    val images: List<Image>,
    val options: Options,
    val expStatus: ExperimentStatus
)

enum class ExperimentStatus {
    RUNNING,
    PENDING,
    END
}