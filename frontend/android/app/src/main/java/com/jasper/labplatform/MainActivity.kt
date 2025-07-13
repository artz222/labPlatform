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
import com.jasper.labplatform.repository.model.Title
import com.jasper.labplatform.utils.showIpInputDialog
import com.jasper.labplatform.viewbinder.EmptyItemViewBinder
import com.jasper.labplatform.viewbinder.ImageItemViewBinder
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
            if (data.end) {
                add(Title(title = "实验已经结束，感谢您的参与"))
            } else {
                add(Title(title = "可以公开的情报"))
                data.infos.forEach {
                    add(it)
                }
                for (image in data.images) {
                    add(image)
                }
                add(Title(title = "请选择"))
                add(data.options)
                add(Empty(0, 20))
            }
        }

        val diffCallback = ExpInfoRVDiffCallback(mAdapter.items, newItems)
        val diffResult = DiffUtil.calculateDiff(diffCallback)
        mAdapter.items = newItems

        diffResult.dispatchUpdatesTo(mAdapter)
    }
}