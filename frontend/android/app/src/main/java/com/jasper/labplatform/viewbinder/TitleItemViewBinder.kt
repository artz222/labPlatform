package com.jasper.labplatform.viewbinder

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.core.graphics.toColorInt
import androidx.recyclerview.widget.RecyclerView
import com.drakeet.multitype.ItemViewBinder
import com.jasper.labplatform.R
import com.jasper.labplatform.model.Title

class TitleItemViewBinder : ItemViewBinder<Title, TitleItemViewBinder.ViewHolder>() {

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val title: TextView = itemView.findViewById(R.id.title)
    }

    override fun onBindViewHolder(holder: ViewHolder, item: Title) {
        holder.title.apply {
            text = item.title
            setBackgroundColor(item.backgroundColor.toColorInt())

        }
        holder.itemView.apply {
            if (holder.layoutPosition == 0) {
                setPadding(0, 0, 0, 10)
            } else {
                setPadding(0, 10, 0, 10)
            }
        }
    }

    override fun onCreateViewHolder(inflater: LayoutInflater, parent: ViewGroup): ViewHolder {
        return ViewHolder(inflater.inflate(R.layout.item_title, parent, false))
    }
}