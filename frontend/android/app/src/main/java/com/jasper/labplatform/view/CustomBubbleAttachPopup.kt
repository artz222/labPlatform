package com.jasper.labplatform.view

import android.annotation.SuppressLint
import android.content.Context
import android.view.View
import android.widget.TextView
import com.jasper.labplatform.R
import com.lxj.xpopup.core.BubbleAttachPopupView
import com.lxj.xpopup.util.XPopupUtils


@SuppressLint("ViewConstructor")
class CustomBubbleAttachPopup(context: Context, private val content: String? = null) :
    BubbleAttachPopupView(context) {
    override fun getImplLayoutId(): Int {
        return R.layout.custom_bubble_attach_popup
    }

    override fun onCreate() {
        super.onCreate()
        setBubbleShadowSize(XPopupUtils.dp2px(context, 6f))
        setArrowWidth(XPopupUtils.dp2px(context, 8f))
        setArrowHeight(XPopupUtils.dp2px(context, 9f))
        setArrowRadius(XPopupUtils.dp2px(context, 2f))
        val tv: TextView? = findViewById(R.id.tv)
        tv?.setOnClickListener { v: View? -> dismiss() }
        tv?.text = content
    }
}
