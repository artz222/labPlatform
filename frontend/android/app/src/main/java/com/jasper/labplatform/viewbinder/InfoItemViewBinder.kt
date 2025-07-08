package com.jasper.labplatform.viewbinder

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.drakeet.multitype.ItemViewBinder
import com.jasper.labplatform.R
import com.jasper.labplatform.repository.model.Info

class InfoItemViewBinder : ItemViewBinder<Info, InfoItemViewBinder.ViewHolder>() {

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val hintTxt: TextView = itemView.findViewById(R.id.hintTxt)
        val valueTxt: TextView = itemView.findViewById(R.id.valueTxt)
    }

    override fun onBindViewHolder(holder: ViewHolder, item: Info) {
        holder.apply {
            hintTxt.text = item.hint
            valueTxt.text = item.value
        }
    }

    override fun onCreateViewHolder(inflater: LayoutInflater, parent: ViewGroup): ViewHolder {
        return ViewHolder(inflater.inflate(R.layout.item_info, parent, false))
    }
}