package com.jasper.labplatform

import android.os.Bundle
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.recyclerview.widget.LinearLayoutManager
import com.drakeet.multitype.MultiTypeAdapter
import com.jasper.labplatform.databinding.ActivityMainBinding
import com.jasper.labplatform.model.Empty
import com.jasper.labplatform.model.Info
import com.jasper.labplatform.model.Options
import com.jasper.labplatform.model.Title
import com.jasper.labplatform.viewbinder.EmptyItemViewBinder
import com.jasper.labplatform.viewbinder.InfoItemViewBinder
import com.jasper.labplatform.viewbinder.RadioGroupItemViewBinder
import com.jasper.labplatform.viewbinder.TitleItemViewBinder
import com.jasper.labplatform.websocket.LabWebSocketClient

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var labWebSocketClient: LabWebSocketClient

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
        initView()
    }

    private fun initView() {
        val mAdapter = MultiTypeAdapter()
        mAdapter.apply {
            register(TitleItemViewBinder())
            register(InfoItemViewBinder())
            register(RadioGroupItemViewBinder())
            register(EmptyItemViewBinder())
            items = arrayListOf<Any>().apply {
                add(Title(title = "可以公开的情报"))
                add(Info(hint = "本次轮数", value = "1/6"))
                add(Info(hint = "当前回合", value = "1/20"))
                for (i in 1..20) {
                    add(Info(hint = "测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试info${i}", value = "value${i}"))
                }
                add(Title(title = "请选择"))
                add(Options(listOf("测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试选项1", "选项2", "选项3")))
                add(Empty(0, 20))
            }
        }
        binding.containerRv.apply {
            adapter = mAdapter
            layoutManager = LinearLayoutManager(context)
        }
    }
}