package com.jasper.labplatform.viewbinder

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.drakeet.multitype.ItemViewBinder
import com.jasper.labplatform.R
import com.jasper.labplatform.repository.model.InfoGroup
import com.jasper.labplatform.utils.setRoundedBackground
import com.jasper.labplatform.view.CustomBubbleAttachPopup
import com.lxj.xpopup.XPopup

class InfoGroupViewBinder : ItemViewBinder<InfoGroup, InfoGroupViewBinder.ViewHolder>() {

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val container: LinearLayout = itemView.findViewById(R.id.container)
        val titleTxt: TextView = itemView.findViewById(R.id.titleTxt)
    }


    override fun onCreateViewHolder(
        inflater: LayoutInflater, parent: ViewGroup
    ): ViewHolder {
        return ViewHolder(inflater.inflate(R.layout.item_info_group, parent, false))
    }

    override fun onBindViewHolder(
        holder: ViewHolder, item: InfoGroup
    ) {
        holder.apply {
            titleTxt.text = item.title
            setRoundedBackground(container, item.color, 10f)
            container.apply {
                removeViews(1, childCount - 1)
                for (info in item.infos) {
                    val view = LayoutInflater.from(context).inflate(R.layout.item_info, this, false)
                    val hintTxt = view.findViewById<TextView>(R.id.hintTxt)
                    val valueTxt = view.findViewById<TextView>(R.id.valueTxt)
                    val (cleanedText, removedList) = processExplainContent(info.hint)
                    hintTxt.text = cleanedText
                    valueTxt.text = info.value
                    view.setOnClickListener {
                        XPopup.Builder(itemView.context)
                            .hasShadowBg(false)
                            .isTouchThrough(true)
                            .isDestroyOnDismiss(true) //对于只使用一次的弹窗，推荐设置这个
                            .atView(view)
                            .isCenterHorizontal(true)
                            .hasShadowBg(false) // 去掉半透明背景
                            .asCustom(
                                CustomBubbleAttachPopup(
                                    itemView.context,
                                    if (removedList.isEmpty()) info.hint else removedList.joinToString(
                                        "\n"
                                    )
                                )
                            )
                            .show()
                    }
                    addView(view)
                }
            }
        }
    }

    private fun processExplainContent(content: String): Pair<String, List<String>> {
        val pattern = Regex("#\\[(.*?)]")

        // 提取所有匹配的内容（不包含 #[ 和 ] 符号）
        val removedList = pattern.findAll(content).map { it.groupValues[1] }.toList()

        // 去除匹配内容（包括 #[ 和 ]）
        val cleanedText = pattern.replace(content, "")
        return cleanedText to removedList
    }
}