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
                    hintTxt.text = info.hint
                    valueTxt.text = info.value
                    addView(view)
                }
            }
        }
    }
}