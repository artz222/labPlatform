package com.jasper.labplatform.viewbinder.diff

import androidx.recyclerview.widget.DiffUtil
import com.jasper.labplatform.repository.model.Empty
import com.jasper.labplatform.repository.model.Image
import com.jasper.labplatform.repository.model.Info
import com.jasper.labplatform.repository.model.Options
import com.jasper.labplatform.repository.model.Title

class ExpInfoRVDiffCallback(
    private val oldList: List<Any>,
    private val newList: List<Any>
) : DiffUtil.Callback() {
    override fun getOldListSize() = oldList.size
    override fun getNewListSize() = newList.size

    override fun areItemsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        // 判断是否是同一个 item（比如 id）
        val oldItem = oldList[oldItemPosition]
        val newItem = newList[newItemPosition]
        return oldItem is Empty && newItem is Empty ||
                oldItem is Image && newItem is Image ||
                oldItem is Info && newItem is Info ||
                oldItem is Options && newItem is Options ||
                oldItem is Title && newItem is Title
    }

    override fun areContentsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        // 判断内容是否完全相同
        val oldItem = oldList[oldItemPosition]
        val newItem = newList[newItemPosition]
        return when {
            oldItem is Empty && newItem is Empty -> oldItem == newItem

            oldItem is Image && newItem is Image -> oldItem == newItem

            oldItem is Info && newItem is Info -> oldItem == newItem

            oldItem is Options && newItem is Options -> oldItem == newItem

            oldItem is Title && newItem is Title -> oldItem == newItem

            else -> false
        }
    }
}
