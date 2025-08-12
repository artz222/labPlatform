package com.jasper.labplatform

import android.os.Bundle
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.LinearLayoutManager
import com.drakeet.multitype.MultiTypeAdapter
import com.jasper.labplatform.databinding.ActivityMainBinding
import com.jasper.labplatform.repository.Repository
import com.jasper.labplatform.repository.model.Empty
import com.jasper.labplatform.repository.model.ExperimentInfo
import com.jasper.labplatform.repository.model.ExperimentStatus
import com.jasper.labplatform.repository.model.Info
import com.jasper.labplatform.repository.model.InfoGroup
import com.jasper.labplatform.repository.model.Title
import com.jasper.labplatform.utils.getGroupColor
import com.jasper.labplatform.utils.showIpInputDialog
import com.jasper.labplatform.viewbinder.EmptyItemViewBinder
import com.jasper.labplatform.viewbinder.ImageGroupViewBinder
import com.jasper.labplatform.viewbinder.ImageItemViewBinder
import com.jasper.labplatform.viewbinder.InfoGroupViewBinder
import com.jasper.labplatform.viewbinder.InfoItemViewBinder
import com.jasper.labplatform.viewbinder.RadioGroupItemViewBinder
import com.jasper.labplatform.viewbinder.TitleItemViewBinder
import com.jasper.labplatform.viewbinder.diff.ExpInfoRVDiffCallback


class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val mAdapter = MultiTypeAdapter()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        // 设置main内容区上下padding（status bar和nav bar）
        ViewCompat.setOnApplyWindowInsetsListener(binding.main) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }
        init()
    }

    private fun init() {
        initView()
        if (Repository.baseIP == null) {
            showIpInputDialog(this) { ip ->
                Repository.baseIP = ip
                Repository.tryConnectWebsocket()
            }
        } else {
            Repository.tryConnectWebsocket()
        }
        Repository.experimentInfo.observe(this) { data ->
            refreshRvContainer(data)
        }
    }

    private fun initView() {
        mAdapter.apply {
            register(TitleItemViewBinder())
            register(ImageGroupViewBinder())
            register(InfoGroupViewBinder())
            register(InfoItemViewBinder())
            register(RadioGroupItemViewBinder())
            register(ImageItemViewBinder())
            register(EmptyItemViewBinder())
        }
        binding.containerRv.apply {
            adapter = mAdapter
            layoutManager = LinearLayoutManager(context)
        }
    }

    private fun refreshRvContainer(data: ExperimentInfo) {

        val newItems = arrayListOf<Any>().apply {
            when (data.expStatus) {
                ExperimentStatus.RUNNING -> {
                    add(Title(title = "可以公开的情报"))
                    // 处理信息分组
                    var index = 0
                    var colorIndex = 0
                    while (index < data.infos.size) {
                        val info = data.infos[index++]
                        if (info.hint == "#info_group") {
                            val groupTitle = info.value
                            val groupInfos = arrayListOf<Info>()
                            val group =
                                InfoGroup(groupTitle, groupInfos, getGroupColor(colorIndex++))
                            add(group)
                            while (index < data.infos.size) {
                                val nextInfo = data.infos[index++]
                                if (nextInfo.hint == "#info_group") {
                                    index--
                                    break
                                }
                                groupInfos.add(nextInfo)
                            }
                        } else {
                            add(info)
                        }
                    }
                    // 处理图片数据
                    add(data.images)
                    // 处理选项数据
                    add(Title(title = "请选择"))
                    add(data.options)
                    add(Empty(0, 20))
                }

                ExperimentStatus.PENDING -> {
                    add(Title(title = "当前实验回合结果处理中，请等待"))
                }

                ExperimentStatus.END -> {
                    add(Title(title = "实验已经结束，感谢您的参与"))
                }
            }
        }

        val diffCallback = ExpInfoRVDiffCallback(mAdapter.items, newItems)
        val diffResult = DiffUtil.calculateDiff(diffCallback)
        mAdapter.items = newItems

        diffResult.dispatchUpdatesTo(mAdapter)
    }
}