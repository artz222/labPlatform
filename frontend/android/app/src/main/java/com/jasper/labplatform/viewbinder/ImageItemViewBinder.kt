package com.jasper.labplatform.viewbinder

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.drakeet.multitype.ItemViewBinder
import com.jasper.labplatform.ext.dpToPx
import com.jasper.labplatform.fragments.ImageZoomDialogFragment
import com.jasper.labplatform.model.Image

class ImageItemViewBinder : ItemViewBinder<Image, ImageItemViewBinder.ViewHolder>() {
    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView)

    override fun onBindViewHolder(holder: ViewHolder, item: Image) {
        val imageUrl = item.imageUrl

        Glide.with(holder.itemView.context)
            .load(imageUrl)
//            .placeholder(R.drawable.placeholder_image)
//            .error(R.drawable.error_image)
            .into(holder.itemView as ImageView)

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
                100.dpToPx()
            )
            setPadding(0, 0, 0, 5.dpToPx())
        })
    }
}