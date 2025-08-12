package com.jasper.labplatform.viewbinder

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import androidx.recyclerview.widget.RecyclerView
import com.drakeet.multitype.ItemViewBinder
import com.jasper.labplatform.repository.model.Image
import com.jasper.labplatform.utils.ext.dpToPx
import com.jasper.labplatform.utils.loadImage
import com.jasper.labplatform.view.ImageZoomDialogFragment

class ImageItemViewBinder : ItemViewBinder<Image, ImageItemViewBinder.ViewHolder>() {
    var lastData: Image? = null

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView)

    override fun onBindViewHolder(holder: ViewHolder, item: Image) {
        if (lastData == item) {
            return
        }
        lastData = item
        val imageUrl = item.imageUrl

        loadImage(imageUrl, holder.itemView as ImageView)

        holder.itemView.setOnClickListener {
            val fragmentManager =
                (holder.itemView.context as? androidx.fragment.app.FragmentActivity)?.supportFragmentManager
            if (fragmentManager != null) {
                val dialogFragment = ImageZoomDialogFragment.newInstance(imageUrl = imageUrl)
                dialogFragment.show(fragmentManager, "image_zoom_dialog")
            } else {
                // Handle case where FragmentManager couldn't be obtained
                // Log an error or show a Toast
            }
        }
    }


    override fun onCreateViewHolder(inflater: LayoutInflater, parent: ViewGroup): ViewHolder {
        return ViewHolder(ImageView(inflater.context).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            )
            setPadding(10.dpToPx(), 0, 10.dpToPx(), 5.dpToPx())
        })
    }
}