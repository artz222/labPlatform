package com.jasper.labplatform.viewbinder

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.drakeet.multitype.ItemViewBinder
import com.jasper.labplatform.utils.ext.dpToPx
import com.jasper.labplatform.repository.model.Empty

class EmptyItemViewBinder : ItemViewBinder<Empty, EmptyItemViewBinder.ViewHolder>() {
    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView)

    override fun onBindViewHolder(holder: ViewHolder, item: Empty) {
        holder.itemView.apply {
            layoutParams = ViewGroup.LayoutParams(
                if (item.width == 0) ViewGroup.LayoutParams.MATCH_PARENT else item.width.dpToPx(),
                item.height.dpToPx()
            )
        }
    }

    override fun onCreateViewHolder(inflater: LayoutInflater, parent: ViewGroup): ViewHolder {
        return ViewHolder(View(inflater.context))
    }
}